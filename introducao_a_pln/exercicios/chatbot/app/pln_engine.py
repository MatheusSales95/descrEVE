import yaml
import numpy as np
import joblib
from nltk.stem import RSLPStemmer
from nltk.tokenize import word_tokenize
from sklearn.neural_network import MLPClassifier
from unidecode import unidecode
from .config import settings, get_path  # <--- Importa configurações

stemmer = RSLPStemmer()

# Pegando caminhos do config.yaml
MODEL_PATH = get_path(settings['nlp']['caminhos']['modelo_pln'])
WORDS_PATH = get_path(settings['nlp']['caminhos']['vocabulario'])
CLASSES_PATH = get_path(settings['nlp']['caminhos']['classes'])
INTENCOES_FILE = get_path(settings['nlp']['caminhos']['intencoes'])


def treinar_modelo_pln():
    try:
        # Lê o arquivo de intenções em YAML
        with open(INTENCOES_FILE, 'r', encoding='utf-8') as f:
            dados = yaml.safe_load(f)
    except FileNotFoundError:
        return {"erro": f"Arquivo '{INTENCOES_FILE}' não encontrado."}

    palavras = []
    classes = []
    documentos = []

    for intencao in dados['intencoes']:
        tag = intencao['tag']
        classes.append(tag)
        for padrao in intencao['padroes']:
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

    # Usa parâmetros do YAML
    params = settings['nlp']['parametros']
    mlp = MLPClassifier(
        hidden_layer_sizes=tuple(params['hidden_layers']),
        max_iter=params['max_iter'],
        activation='relu',
        random_state=42
    )
    mlp.fit(X, y)

    joblib.dump(mlp, MODEL_PATH)
    joblib.dump(palavras, WORDS_PATH)
    joblib.dump(classes, CLASSES_PATH)

    return {"mensagem": f"Modelo NLP treinado e salvo em {MODEL_PATH}"}


def classificar_intencao(comando):
    try:
        mlp = joblib.load(MODEL_PATH)
        palavras = joblib.load(WORDS_PATH)
        classes = joblib.load(CLASSES_PATH)
    except FileNotFoundError:
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


def encontrar_localizacao(frase, db_session, model_estacao):
    todas_estacoes = db_session.query(model_estacao).all()
    frase_limpa = unidecode(frase.lower())

    for estacao in todas_estacoes:
        nome_cidade = unidecode(estacao.cidade.lower())
        nome_estado = unidecode(estacao.estado.lower())

        if nome_cidade in frase_limpa:
            return estacao
        if nome_estado in frase_limpa:
            return estacao

    return None
