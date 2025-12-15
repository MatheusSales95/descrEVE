# Assistente Meteorológico Inteligente

Este projeto é um **Chatbot de Previsão do Tempo** Full Stack. Ele utiliza **Processamento de Linguagem Natural (NLP)** para entender as intenções do usuário e uma **Rede Neural (MLP)** para prever a probabilidade de chuva com base em dados históricos armazenados em um banco **PostgreSQL**.

---

## Funcionalidades Chave

* **NLP (Processamento de Linguagem Natural):**
    * Classificação de intenções (Saudação, Pedido de Clima, Despedida) usando *Bag-of-Words* e um **MLPClassifier**.
    * **Extração de Entidades:** Reconhecimento de nomes de cidades na frase do usuário para consulta no banco de dados.
    * **Stemming (RSLP):** Uso de técnicas para reduzir palavras à sua raiz, melhorando a precisão da classificação em português.
* **Machine Learning (Previsão):**
    * Modelo `MLPClassifier` (Rede Neural) treinado com dados de clima.
    * Prevê se vai chover no dia seguinte, utilizando dados de Temperatura (Min/Max), Umidade, Pressão e Vento.
* **Backend & Banco de Dados:**
    * API construída com **FastAPI** e documentação automática (Swagger/Docs).
    * Persistência de dados com **PostgreSQL** e ORM **SQLAlchemy**.
    * Geração de dados sintéticos para simulação de um histórico de medições.
* **Frontend Simples:**
    * Interface de chat simples (HTML/CSS/JS) que consome a API REST.

---

## Tecnologias Utilizadas

* **Linguagem:** Python 3.12+
* **Framework Web:** FastAPI + Uvicorn
* **Banco de Dados:** PostgreSQL
* **ORM:** SQLAlchemy
* **Data Science:** Scikit-Learn, Pandas, NumPy
* **NLP:** NLTK (RSLP Stemmer)
* **Outros:** `python-dotenv`, `joblib`, `unidecode`.

---

## Instalação e Configuração

### 1. Pré-requisitos
Certifique-se de ter o **Python** e o **PostgreSQL** instalados.

### 2. Configurar o Ambiente Virtual
```bash
python -m venv venv
source venv/bin/activate  # No Linux/Mac
# venv\Scripts\activate   # No Windows
```

### 3.Instalar as Dependências
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary scikit-learn pandas numpy nltk python-dotenv unidecode faker joblib
```

Baixe os recursos do NLTK:
```bash
python -m nltk.downloader rslp punkt
```

### 4. Configurar o Banco de Dados
Crie um arquivo .env na raiz do projeto com suas credenciais:
```bash
DB_NAME=postgres
DB_USER=postgres
DB_PASS=sua_senha
DB_HOST=localhost
DB_PORT=5432
```

### 5. Popule o Banco de Dados
Execute o script para criar as tabelas e gerar dados históricos de clima:
```bash
python popular_banco.py
```

### Como Executar
### 1. Inicie o Servidor Backend
```bash
uvicorn app.main:app --reload
```
A API estará acessível em: http://127.0.0.1:8000

### 2. Treine os Modelos de IA
É crucial treinar os dois modelos (NLP e Clima) para gerar os arquivos .pkl. Acesse o Swagger (http://127.0.0.1:8000/docs) e execute as seguintes rotas:

POST /treinar_bot (Treina o NLP para entender o texto)

POST /treinar_chuva (Treina o MLP para prever o clima)

### 3. Acesse o Chatbot Frontend
Abra o arquivo index.html diretamente no seu navegador e comece a conversar.

## Exemplos de Interação

| Comando do Usuário | Intenção Classificada | Ação do Sistema |
| :--- | :--- | :--- |
| "Olá, tudo bem?" | `saudacao` | Responde com uma saudação aleatória. |
| "Qual a previsão para Salvador?" | `ver_clima` | Busca dados no DB e usa o MLP para a previsão. |
| "Vai chover em São José dos Campos?" | `ver_clima` | Retorna o estado atual do clima e a previsão de chuva. |
| "Até mais!" | `despedida` | Responde com uma despedida. |



