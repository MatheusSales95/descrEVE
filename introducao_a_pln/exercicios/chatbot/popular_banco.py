import psycopg2
import random
import os
from dotenv import load_dotenv  # Importa o carregador de env
from faker import Faker
from datetime import date, timedelta

# 1. Carrega as variáveis do arquivo .env
load_dotenv()

# 2. Pega as configurações de forma segura
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

fake = Faker('pt_BR')


def gerar_dados():
    try:
        # Tenta conectar usando as variáveis do .env
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print(f"Conectado ao banco '{DB_CONFIG['dbname']}' com sucesso!")

        # --- A PARTIR DAQUI TUDO IGUAL AO ANTERIOR ---

        # 1. Criar 5 Estações
        cidades = [("São José dos Campos", "SP"), ("Jacareí", "SP"),
                   ("Taubaté", "SP"), ("Salvador", "BA"), ("Curitiba", "PR")]

        ids_estacoes = []

        for i, (cidade, estado) in enumerate(cidades):
            codigo = f"{estado}-{i+1:03d}"
            lat = float(fake.latitude())
            lon = float(fake.longitude())

            # Usando ON CONFLICT para não dar erro se rodar o script 2 vezes
            cur.execute("""
                INSERT INTO estacoes (codigo_estacao, cidade, estado, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s) 
                ON CONFLICT (codigo_estacao) DO NOTHING
                RETURNING id;
            """, (codigo, cidade, estado, lat, lon))

            # Se a estação já existia, buscamos o ID dela
            result = cur.fetchone()
            if result:
                estacao_id = result[0]
                ids_estacoes.append(estacao_id)
                print(f"Estação criada/encontrada: {cidade} ({codigo})")
            else:
                # Caso onde o ON CONFLICT ignorou a inserção, buscamos o ID manualmente
                cur.execute(
                    "SELECT id FROM estacoes WHERE codigo_estacao = %s", (codigo,))
                estacao_id = cur.fetchone()[0]
                ids_estacoes.append(estacao_id)

        # 2. Gerar medições
        print("\nGerando histórico climático (pode levar alguns segundos)...")
        data_inicial = date(2023, 1, 1)
        registros = []

        for est_id in ids_estacoes:
            for dias in range(365):
                data_atual = data_inicial + timedelta(days=dias)

                temp_max = round(random.uniform(18, 38), 1)
                temp_min = round(temp_max - random.uniform(5, 12), 1)
                umidade = round(random.uniform(30, 99), 1)
                pressao = round(random.uniform(990, 1025), 1)
                vento = round(random.uniform(0, 25), 1)

                # Lógica do Alvo
                score_chuva = 0
                if umidade > 75:
                    score_chuva += 40
                if pressao < 1005:
                    score_chuva += 30
                if (temp_max - temp_min) < 6:
                    score_chuva += 20
                score_chuva += random.randint(-15, 15)

                choveu_amanha = 1 if score_chuva > 50 else 0

                registros.append(
                    (est_id, data_atual, temp_max, temp_min, umidade, pressao, vento, choveu_amanha))

        query = """
            INSERT INTO medicoes 
            (estacao_id, data_medicao, temperatura_max, temperatura_min, umidade_relativa, pressao_atmosferica, velocidade_vento, choveu_dia_seguinte)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.executemany(query, registros)
        conn.commit()

        print(f"\nSucesso! {len(registros)} registros inseridos.")
        cur.close()
        conn.close()

    except Exception as e:
        print(f"ERRO: {e}")
        print("Dica: Verifique se os dados no arquivo .env estão corretos.")


if __name__ == "__main__":
    gerar_dados()
