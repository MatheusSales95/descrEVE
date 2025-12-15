import joblib
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from . import models
from .config import settings, get_path

# Pegando caminhos do config.yaml
MODEL_PATH = get_path(settings['clima']['caminhos']['modelo_chuva'])
SCALER_PATH = get_path(settings['clima']['caminhos']['escalador'])


def treinar_modelo(db_session):
    # 1. Carregar dados do Banco
    dados = db_session.query(models.Medicao).all()

    if not dados:
        return {"erro": "Não há dados suficientes no banco para treinar."}

    df = pd.DataFrame([d.__dict__ for d in dados])

    # 2. Preparar Features (X) e Target (y)
    features = ['temperatura_max', 'temperatura_min',
                'umidade_relativa', 'pressao_atmosferica', 'velocidade_vento']
    X = df[features]
    y = df['choveu_dia_seguinte'].astype(int)

    # 3. Divisão Treino/Teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    # 4. Escalar dados
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 5. Treinar MLP
    mlp = MLPClassifier(hidden_layer_sizes=(
        16, 8), activation='relu', max_iter=500, random_state=42)
    mlp.fit(X_train_scaled, y_train)

    acuracia = mlp.score(X_test_scaled, y_test)

    # 6. Salvar arquivos
    joblib.dump(mlp, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    return {
        "mensagem": "Modelo de Previsão de Chuva treinado com sucesso!",
        "acuracia_teste": f"{acuracia * 100:.2f}%",
        "caminho_modelo": MODEL_PATH
    }


def prever_agora(t_max, t_min, umidade, pressao, vento):
    try:
        mlp = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
    except FileNotFoundError:
        return None

    dados_novos = np.array([[t_max, t_min, umidade, pressao, vento]])
    dados_scaled = scaler.transform(dados_novos)

    previsao = mlp.predict(dados_scaled)[0]
    probabilidade = mlp.predict_proba(dados_scaled)[0][previsao]

    return {
        "vai_chover": bool(previsao),
        "confianca": f"{probabilidade * 100:.2f}%"
    }
