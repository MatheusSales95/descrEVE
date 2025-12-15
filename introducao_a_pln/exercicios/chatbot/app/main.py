import yaml
import random
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, database, pln_engine, ml_engine
from .config import settings, get_path  # <--- Importa settings

app = FastAPI(
    title=settings['app']['nome'],
    version=settings['app']['versao']
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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

# Rotas de Treino


@app.post("/treinar_bot")
def treinar_nlp():
    return pln_engine.treinar_modelo_pln()


@app.post("/treinar_chuva")
def treinar_clima(db: Session = Depends(database.get_db)):
    return ml_engine.treinar_modelo(db)

# Rota Chat


@app.post("/conversar")
def conversar(dados: ComandoInput, db: Session = Depends(database.get_db)):
    comando = dados.texto
    analise = pln_engine.classificar_intencao(comando)

    limite_confianca = settings['nlp']['parametros']['limite_confianca']

    if not analise or analise['confianca'] < limite_confianca:
        return {"resposta": "Desculpe, não entendi. Tente ser mais específico."}

    tag = analise['tag']

    # Lê respostas do YAML
    intencoes_path = get_path(settings['nlp']['caminhos']['intencoes'])
    try:
        with open(intencoes_path, "r", encoding="utf-8") as f:
            dados_yaml = yaml.safe_load(f)

        # Procura a tag no YAML
        for item in dados_yaml['intencoes']:
            if item['tag'] == tag:
                if 'respostas' in item:
                    return {"resposta": random.choice(item['respostas']), "tag": tag}

                # Se for ver_clima
                if item.get('acao') == 'BUSCAR_DB':
                    estacao = pln_engine.encontrar_localizacao(
                        comando, db, models.Estacao)
                    if not estacao:
                        return {"resposta": "Entendi que quer saber do clima, mas não achei a cidade."}

                    ultima_medicao = db.query(models.Medicao)\
                        .filter(models.Medicao.estacao_id == estacao.id)\
                        .order_by(desc(models.Medicao.data_medicao))\
                        .first()

                    if not ultima_medicao:
                        return {"resposta": "Sem dados para essa cidade."}

                    previsao = ml_engine.prever_agora(
                        ultima_medicao.temperatura_max, ultima_medicao.temperatura_min,
                        ultima_medicao.umidade_relativa, ultima_medicao.pressao_atmosferica,
                        ultima_medicao.velocidade_vento
                    )

                    if not previsao:
                        return {"resposta": "Erro: Modelo de clima não treinado."}

                    vai_chover = "Sim" if previsao['vai_chover'] else "Não"

                    msg = (f"Análise para {estacao.cidade}:\n"
                           f"{ultima_medicao.temperatura_min}°C / {ultima_medicao.temperatura_max}°C\n"
                           f"Previsão de Chuva: {vai_chover}")

                    return {"resposta": msg, "dados_tecnicos": previsao}

    except Exception as e:
        return {"erro": str(e)}

    return {"resposta": "Sem resposta configurada."}
