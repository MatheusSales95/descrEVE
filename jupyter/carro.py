from fastapi import FastAPI

app = FastAPI()

# --- 1. A Lógica de Negócio (Sua Classe) ---
class Carro:
    def __init__(self, modelo, consumo):
        self.modelo = modelo
        self.consumo = consumo
        self.tanque = 0  # Começa vazio

    def abastecer(self, litros):
        self.tanque += litros
        if self.tanque > 50:
            self.tanque = 50
        return self.tanque

    def dirigir(self, distancia):
        litros_necessarios = distancia / self.consumo
        if litros_necessarios <= self.tanque:
            self.tanque -= litros_necessarios
            return f"Sucesso! Viajou {distancia}km. Restam {self.tanque:.1f}L"
        else:
            return "Erro: Combustível insuficiente!"

# Criamos um carro global para a API usar
meu_carro = Carro("Ferrari", 5) # Faz 5km por litro

# --- 2. As Rotas da API (O Controle Remoto) ---

@app.get("/")
def status():
    return {
        "modelo": meu_carro.modelo,
        "tanque_atual": meu_carro.tanque
    }

@app.get("/abastecer/{litros}")
def rota_abastecer(litros: float):
    nivel_atual = meu_carro.abastecer(litros)
    return {"mensagem": f"Abastecido! Tanque agora tem {nivel_atual}L"}

@app.get("/dirigir/{km}")
def rota_dirigir(km: float):
    resultado = meu_carro.dirigir(km)
    return {"resultado": resultado, "tanque_restante": meu_carro.tanque}
