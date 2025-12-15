import pandas as pd
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session
from . import models

# salvando arquivos de treinamento e o pré-processamento pelo joblib
MODEL_PATH = "modelo_chuva.pkl"
SCALER_PATH = "escalador.pkl"

# 1. Puxar dados do Banco SQL usando Pandas


def treinar_modelo(db: Session):
    query = db.query(
        models.Medicao.temperatura_max,
        models.Medicao.temperatura_min,
        models.Medicao.umidade_relativa,
        models.Medicao.pressao_atmosferica,
        models.Medicao.velocidade_vento,
        models.Medicao.choveu_dia_seguinte
    )

    # Converte a query do SQLAlchemy direto para DataFrame
    df = pd.read_sql(query.statement, db.bind)

    if df.empty:
        return {"erro": "Não há dados suficientes no banco para treinar."}

    # 2. Separar Features (X) e Alvo (y)
    X = df[['temperatura_max', 'temperatura_min', 'umidade_relativa',
            'pressao_atmosferica', 'velocidade_vento']]
    y = df['choveu_dia_seguinte']

    # 3. Separar Treino e Teste (20% para prova final)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    # 4. Normalizar os dados (Essencial para MLP!)
    # Redes neurais odeiam números em escalas diferentes Z = (x-u)/o, media = 0 valor x = media + desvio
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 5. Criar e Treinar o MLP (O Cérebro)
    # fit = epoca, max_iter = tempo de estudo e ajuste de pesos ate 500 tentativas(fit)
    # relu = ReLU (Rectified Linear Unit): f(x) = max(0, x), resultado (-) = informação irrelevante ou contraditória, (0) = o neurônio fica quieto/desligado (+) = Passa o valor para frente
    mlp = MLPClassifier(hidden_layer_sizes=(
        16, 8), activation='relu', max_iter=500, random_state=42)
    mlp.fit(X_train_scaled, y_train)

    # 6. Avaliar a precisão dos resultados do treinamanto utilizando o text x,y guardado em train_test_split()
    acuracia = mlp.score(X_test_scaled, y_test)

    # 7. Salvar o modelo e o escalador no disco
    joblib.dump(mlp, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    return {
        "mensagem": "Modelo treinado com sucesso!",
        "acuracia": f"{acuracia * 100:.2f}%",
        "tamanho_treino": len(X_train),
        "tamanho_teste": len(X_test)
    }


def prever_agora(temp_max, temp_min, umidade, pressao, vento):
    try:
        mlp = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
    except:
        return None  # Modelo não existe ainda

    # Prepara os dados novos (DataFrame com nomes das colunas)
    # É importante passar os nomes das colunas para o scaler não reclamar (Pandas)
    dados_novos = pd.DataFrame([[temp_max, temp_min, umidade, pressao, vento]],
                               columns=['temperatura_max', 'temperatura_min', 'umidade_relativa', 'pressao_atmosferica', 'velocidade_vento'])

    # Aplica a mesma matemática de escala usada no treino
    dados_scaled = scaler.transform(dados_novos)

    # Faz a previsão (0 ou 1)
    previsao = mlp.predict(dados_scaled)[0]

    # Pega a probabilidade (certeza da rede)
    probabilidade = mlp.predict_proba(dados_scaled)[0][previsao]

    return {
        "vai_chover": bool(previsao),
        "confianca": f"{probabilidade * 100:.2f}%"
    }
