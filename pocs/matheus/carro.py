class Carro:
    def __init__(self, modelo, consumo, __tanque):
        self.modelo = modelo
        self.consumo = consumo
        self.tanque = __tanque

    def set_abastecer(self, litros):
        self.tanque += litros
        if self.tanque > 50:
            self.tanque = 50
            print("O tanque está cheio e excedeu a capacidade máxima de 50 litros.")

    def get_ver_tanque(self):
        print(f"O nível atual do tanque é de {self.tanque} litros.")

    def dirigir(self, distacia):
        if distacia / self.consumo <= self.tanque:
            self.tanque -= distacia / self.consumo
            print(
                f"Você dirigiu {distacia} km. O nível atual do tanque é de {self.tanque} litros.")
        else:
            print("Combustível insuficiente para a distância desejada.")


fusca = Carro("Fusca", 5, 0)
fusca.set_abastecer(50)
fusca.get_ver_tanque()
fusca.dirigir(100)

ferrari = Carro("Ferrari", 5, 10)
ferrari.set_abastecer(20)
ferrari.get_ver_tanque()
ferrari.dirigir(150)
