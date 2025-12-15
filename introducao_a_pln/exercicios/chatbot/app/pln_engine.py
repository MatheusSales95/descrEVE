import json
import numpy as np
import joblib
import random
from nltk.stem import RSLPStemmer
from nltk.tokenize import word_tokenize
from sklearn.neural_network import MLPClassifier
from unidecode import unidecode


MODEL_PATH = "modelo_chatbot.pkl"
WORDS_PATH = "palavras.pkl"
CLASSES_PATH = "classes.pkl"
JSON_FILE = "intencoes.json"

stemmer = RSLPStemmer()


def treinar_modelo_pln():
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            intencoes = json.load(f)
    except FileNotFoundError:
        return {"erro": "Arquivo intencoes.json não encontrado."}

    palavras = []
    classes = []
    documentos = []

    for intencao in intencoes['intencoes']:
        tag = intencao['tag']
        classes.append(tag)
        for padrao in intencao['padroes']:
            # Tokeniza e pega a raiz (Stemming)
            w = [stemmer.stem(token.lower()) for token in word_tokenize(
                padrao, language='portuguese')]
            palavras.extend(w)
            documentos.append((w, tag))

    palavras = sorted(list(set([w for w in palavras if w not in ('?', '!')])))
    classes = sorted(list(set(classes)))

    treinamento = []
    saida_vazia = [0] * len(classes)

    for doc in documentos:
        bag = []
        padrao_palavras = doc[0]
        for w in palavras:
            bag.append(1) if w in padrao_palavras else bag.append(0)

        saida_linha = list(saida_vazia)
        saida_linha[classes.index(doc[1])] = 1
        treinamento.append([bag, saida_linha])

    np.random.shuffle(treinamento)
    treinamento = np.array(treinamento, dtype=object)

    X = list(treinamento[:, 0])
    y = list(treinamento[:, 1])

    mlp = MLPClassifier(hidden_layer_sizes=(100, 50),
                        activation='relu', max_iter=2000, random_state=42)
    mlp.fit(X, y)

    joblib.dump(mlp, MODEL_PATH)
    joblib.dump(palavras, WORDS_PATH)
    joblib.dump(classes, CLASSES_PATH)

    return {"mensagem": "Modelo atualizado com sucesso!"}


# Função que usada para descobrir o que o usuário quer

def classificar_intencao(comando):
    try:
        mlp = joblib.load(MODEL_PATH)
        palavras = joblib.load(WORDS_PATH)
        classes = joblib.load(CLASSES_PATH)
    except:
        return None

    frase_stemmed = [stemmer.stem(token.lower()) for token in word_tokenize(
        comando, language='portuguese')]
    bag = [0] * len(palavras)
    for w in frase_stemmed:
        if w in palavras:
            bag[palavras.index(w)] = 1

    if sum(bag) == 0:
        return {"tag": "nao_entendi", "confianca": 0.0}

    input_data = np.array([bag])
    probabilidades = mlp.predict_proba(input_data)[0]
    melhor_indice = np.argmax(probabilidades)
    confianca = probabilidades[melhor_indice]
    tag = classes[melhor_indice]

    return {"tag": tag, "confianca": confianca}

# Função que varre o Banco de Dados e vê se o usuário citou alguma cidade conhecida.


def encontrar_localizacao(frase, db_session, model_estacao):

    # Pega todas as cidades cadastradas no banco
    todas_estacoes = db_session.query(model_estacao).all()
    frase_limpa = unidecode(frase.lower())
    for estacao in todas_estacoes:
        # Normalização dos nomes de cidade
        nome_cidade = unidecode(estacao.cidade.lower())
        nome_estado = unidecode(estacao.estado.lower())

        if nome_cidade in frase_limpa:
            return estacao
        # busca simples, se tiver duas cidades no mesmo estado ele pega a primeira que achar
        if nome_estado in frase_limpa or estacao.estado.lower() in frase_limpa.split():
            return estacao
    return None
