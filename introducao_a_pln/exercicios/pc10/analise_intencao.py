import spacy

# Garantindo que o modelo está carregado
try:
    nlp = spacy.load("pt_core_news_sm")
except:
    print("Modelo não encontrado. Verifique o download.")


def analisar_intencao(frase):

    doc = nlp(frase)

    # Proteção para frase vazia
    if len(doc) == 0:
        return "Vazio"

    # 1. Regra da Pergunta (olhando a pontuação final)
    # doc[-1] pega o último token da frase
    if doc[-1].text == "?":
        return "Pergunta"

    # 2. Regra do Comando (Dica do PDF: olhar a primeira palavra)
    # doc[0] pega o primeiro token
    primeira_classe = doc[0].pos_

    if primeira_classe == "VERB":
        return "Comando"

    # 3. Se não for pergunta nem comando, é afirmação
    return "Afirmação"

# --- Bateria de Testes ---

# frases_teste = [
#     "Qual é o seu nome?",         # Esperado: Pergunta
#     "Feche a porta agora.",       # Esperado: Comando (Feche = Verbo)
#     "O céu está azul.",           # Esperado: Afirmação (O = Determinante)
#     "Estude para a prova.",       # Esperado: Comando (Estude = Verbo)
#     "Eu estudei ontem."           # Esperado: Afirmação (Eu = Pronome)
# ]

# print(f"{'FRASE':<30} {'RESULTADO':<15}")
# print("-" * 45)

# for f in frases_teste:
#     resultado = analisar_intencao(f)
#     print(f"{f:<30} {resultado:<15}")


# com input
resultado = analisar_intencao(input('entre com uma frase: '))
print(f"{resultado:<30} {resultado:<15}")
