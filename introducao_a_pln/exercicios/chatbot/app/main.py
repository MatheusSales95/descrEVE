import json
import random
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, database, pln_engine, ml_engine

app = FastAPI(title="Assistente Meteorológico Inteligente")

# CORS permite que o front consuma a API solicitada
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, etc.
    allow_headers=["*"],
)


class ComandoInput(BaseModel):
    texto: str


class ClimaInput(BaseModel):
    temperatura_max: float
    temperatura_min: float
    umidade: float
    pressao: float
    vento: float


# ROTAS DE TREINAMENTO

@app.post("/treinar_bot")
def treinar_nlp():
    return pln_engine.treinar_modelo_pln()


@app.post("/treinar_chuva")
def treinar_clima(db: Session = Depends(database.get_db)):
    return ml_engine.treinar_modelo(db)

# ROTA PRINCIPAL (CHATBOT)


@app.post("/conversar")
def conversar(dados: ComandoInput, db: Session = Depends(database.get_db)):
    comando = dados.texto

    # Entender a Intenção (Usando a IA de NLP)
    analise = pln_engine.classificar_intencao(comando)

    # Se a IA não tiver certeza ou falhar
    if not analise or analise['confianca'] < 0.6:
        return {"resposta": "Desculpe, não entendi. Tente perguntar sobre o clima de uma cidade específica."}

    tag = analise['tag']

    # Se for Saudação ou Despedida (Respostas prontas do JSON)
    try:
        with open("intencoes.json", "r", encoding="utf-8") as f:
            dados_json = json.load(f)
            for item in dados_json['intencoes']:
                if item['tag'] == tag and 'respostas' in item:
                    return {"resposta": random.choice(item['respostas']), "tag": tag}
    except FileNotFoundError:
        return {"erro": "Arquivo intencoes.json não encontrado."}

    # Se for Clima, precisamos buscar no banco e usar a IA de Chuva
    if tag == "ver_clima":
        # Identifica a cidade na frase
        estacao = pln_engine.encontrar_localizacao(comando, db, models.Estacao)

        if not estacao:
            return {
                "resposta": "Entendi que você quer saber do clima, mas não identifiquei a cidade no texto. Tente citar o nome completo, ex: 'Clima em São José dos Campos'.",
                "tag": tag
            }

        # Busca a última medição real dessa estação no banco
        ultima_medicao = db.query(models.Medicao)\
            .filter(models.Medicao.estacao_id == estacao.id)\
            .order_by(desc(models.Medicao.data_medicao))\
            .first()

        if not ultima_medicao:
            return {"resposta": f"Encontrei a estação de {estacao.cidade}, mas não há dados de medição cadastrados para ela."}

        # Aqui ele precisa dos arquivos .pkl criados no /treinar_chuva
        previsao_chuva = ml_engine.prever_agora(
            ultima_medicao.temperatura_max,
            ultima_medicao.temperatura_min,
            ultima_medicao.umidade_relativa,
            ultima_medicao.pressao_atmosferica,
            ultima_medicao.velocidade_vento
        )

        if previsao_chuva is None:
            return {"resposta": "Erro: O modelo de previsão de chuva não foi treinado. Por favor, execute a rota /treinar_chuva primeiro."}

        vai_chover = "Sim" if previsao_chuva['vai_chover'] else "Não"
        confianca = previsao_chuva['confianca']

        # Monta a resposta
        resposta_texto = (
            f"Análise para {estacao.cidade}-{estacao.estado} (Data base: {ultima_medicao.data_medicao}):\n"
            f"Temperaturas: {ultima_medicao.temperatura_min}°C / {ultima_medicao.temperatura_max}°C\n"
            f"Umidade: {ultima_medicao.umidade_relativa}%\n"
            f"Previsão de Chuva p/ dia seguinte: {vai_chover} (Certeza da IA: {confianca})"
        )

        return {
            "resposta": resposta_texto,
            "dados_tecnicos": {
                "cidade_id": estacao.id,
                "lat": estacao.latitude,
                "previsao_raw": previsao_chuva
            }
        }

    return {"resposta": "Não sei como responder isso ainda."}


# ROTAS UTILITÁRIAS

@app.get("/estacoes")
def listar_estacoes(db: Session = Depends(database.get_db)):
    return db.query(models.Estacao).all()


@app.post("/prever_manual")
def prever_tempo_manual(dados: ClimaInput):
    """
    Rota para testar a IA de chuva sem precisar falar com o Chatbot.
    """
    return ml_engine.prever_agora(
        dados.temperatura_max, dados.temperatura_min,
        dados.umidade, dados.pressao, dados.vento
    )
