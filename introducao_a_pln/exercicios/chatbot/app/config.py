import yaml
import os
from pathlib import Path

# Define o caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"


def carregar_config():
    """Lê o arquivo YAML e retorna um dicionário Python"""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado em: {CONFIG_PATH}")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as exc:
            print(f"Erro ao ler o YAML: {exc}")
            return None


# Instância global da configuração (Singleton)
settings = carregar_config()
