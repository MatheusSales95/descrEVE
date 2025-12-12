from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import models, database, ml_engine

app = FastAPI(title="Sistema de Previsão de Chuva 🌧️")

# --- Modelos de Entrada (Para validar o JSON que o usuário envia) ---


class ClimaInput(BaseModel):
    temperatura_max: float
    temperatura_min: float
    umidade: float
    pressao: float
    vento: float

# --- Rotas ---


@app.get("/estacoes")
def listar_estacoes(db: Session = Depends(database.get_db)):
    return db.query(models.Estacao).all()


@app.post("/treinar")
def treinar_inteligencia(db: Session = Depends(database.get_db)):
    """
    Vai ao banco de dados, pega o histórico e ensina o MLP a prever chuva.
    """
    resultado = ml_engine.treinar_modelo(db)
    return resultado


@app.post("/prever")
def prever_tempo(dados: ClimaInput):
    """
    Recebe dados do tempo de hoje e diz se vai chover amanhã.
    """
    resultado = ml_engine.prever_agora(
        dados.temperatura_max,
        dados.temperatura_min,
        dados.umidade,
        dados.pressao,
        dados.vento
    )

    if resultado is None:
        raise HTTPException(
            status_code=400, detail="O modelo ainda não foi treinado! Rode a rota /treinar primeiro.")

    return resultado
