from fastapi import FastAPI

app = FastAPI()


class Carro:
    def __init__(self, modelo, consumo):
        self.modelo = modelo
        self.consumo = consumo
        self.tanque = 0

    def abastecer(self, litros):
        self.tanque += litros
        if self.tanque > 50:
            self.tanque = 50
            print("O tanque está cheio e excedeu a capacidade máxima de 50 litros.")

    def dirigir(self, distacia):
        if distacia / self.consumo <= self.tanque:
            self.tanque -= distacia / self.consumo
            print(
                f"Você dirigiu {distacia} km. O nível atual do tanque é de {self.tanque} litros.")
        else:
            print("Combustível insuficiente para a distância desejada.")


fusca = Carro("Fusca", 5)


@app.get("/")
def get_carro_info():
    return {"modelo": "Fusca", "consumo": 5, "tanque_atual": fusca.tanque}


@app.get("/abastecer/{litros}")
def rota_abastecer(litros: float):
    nivel_atual = fusca.abastecer(litros)
    return {"mensagem": f"Tanque abastecido. Nível atual: {nivel_atual} litros."}


@app.get("/dirigir/{km}")
def dirigir(km: float):
    resultado = fusca.dirigir(km)
    return {"resultado": resultado, "tanque restante": fusca.tanque}
