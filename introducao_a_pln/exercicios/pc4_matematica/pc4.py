import spacy
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    nlp = spacy.load("pt_core_news_sm")
except:
    print("Modelo SpaCy não encontrado. Verifique a instalação.")

# Três solicitações de Service Desk
solicitacoes = [
    "A impressora do financeiro não está imprimindo, está piscando uma luz vermelha.",  # 1. Hardware
    "Preciso que instale o VS Code e o Python no meu computador para desenvolvimento.",  # 2. Software
    # 3. Hardware (Similar ao 1)
    "Minha impressora parou de funcionar e tem um papel atolado nela."
]

# Normalização


def pre_processar(texto):
    doc = nlp(texto.lower())

    tokens_limpos = []

    for token in doc:
        # Stop Words e Pontuação
        if not token.is_stop and not token.is_punct:
            # Lematização
            tokens_limpos.append(token.lemma_)

    # O Scikit-Learn espera uma string inteira ("impressora financeiro imprimir..."), não uma lista
    return " ".join(tokens_limpos)


# Aplicando a limpeza em todos os documentos
corpus = [pre_processar(doc) for doc in solicitacoes]

print("--- Documentos Processados (Normalizados) ---")
for i, doc in enumerate(corpus):
    print(f"Doc {i+1}: {doc}")
print("-" * 50)

vectorizer = TfidfVectorizer()
matriz_tfidf = vectorizer.fit_transform(corpus)

# Mostrando os vetores
df_vetores = pd.DataFrame(
    matriz_tfidf.toarray(),
    columns=vectorizer.get_feature_names_out(),
    index=["Solicitação 1", "Solicitação 2", "Solicitação 3"]
)
print("\n--- Vetores (Representação Numérica) ---\n")
print(df_vetores.round(2))

# --- 4. CÁLCULO DE SIMILARIDADE (Cosseno) ---
# A função cosine_similarity compara todos contra todos
matriz_similaridade = cosine_similarity(matriz_tfidf)

# Transformando em DataFrame para visualizar a Matriz Bonita
df_sim = pd.DataFrame(
    matriz_similaridade,
    index=["Solicitação 1", "Solicitação 2", "Solicitação 3"],
    columns=["Solicitação 1", "Solicitação 2", "Solicitação 3"]
)

print("\n--- Matriz de Similaridade de Cosseno ---\n")
print(df_sim.round(2))


print("\n--- Conclusão ---\n")
sim_1_2 = matriz_similaridade[0][1]  # Doc 1 vs Doc 2
sim_1_3 = matriz_similaridade[0][2]  # Doc 1 vs Doc 3
