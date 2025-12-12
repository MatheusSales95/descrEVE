import nltk
import spacy
from nltk.corpus import machado
from nltk.tokenize import word_tokenize, sent_tokenize

nltk.download('machado')
nltk.download('punkt_tab')

# Carregando Dom Casmurro
texto_completo = machado.raw('romance/marm08.txt')
print(f"Texto carregado! Total de caracteres: {len(texto_completo)}")

# tonkenização

# por palavra
token_palavras = word_tokenize(texto_completo, language='portuguese')
# por sentenca
token_sentencas = sent_tokenize(texto_completo, language='portuguese')

print(f'total de palavras: {len(token_palavras)}')
print(f'total de sentencas: {len(token_sentencas)}')

# carrega pt-br para o SpaCY
try:
    nlp = spacy.load("pt_core_news_sm")
    print("Modelo carregado com sucesso!")
except OSError:
    print("Precisamos baixar o modelo. Tente rodar no terminal: python -m spacy download pt_core_news_sm")

frase_escolhida = token_sentencas[10]

doc = nlp(frase_escolhida)

print(f"Frase: {frase_escolhida}\n")
print(f"{'TOKEN':<15} {'POS (Classe)':<15} {'EXPLICAÇÃO'}")
print("-" * 45)

for token in doc:
    print(f"{token.text:<15} {token.pos_:<15} {spacy.explain(token.pos_)}")
