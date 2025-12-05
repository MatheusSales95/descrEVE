from fastapi import FastAPI
import random

app = FastAPI()


class Heroi:
    def __init__(self, nome, nivel, forca, agilidade, sorte):
        self.nome = nome
        self.forca = forca
        self.agilidade = agilidade
        self.sorte = sorte
        self.nivel = nivel
        self.inventario = ['Poção']
        self.equipamento = ['Espada simples', 'Escudo simples']
        self.ouro = 50


class Inimigo:
    def __init__(self, nome, poder, vida):
        self.nome = nome
        self.poder = poder
        self.vida = vida


class Arma:
    def __init__(self, nome, dano):
        self.nome = nome
        self.dano = dano

    def dano_infligido(self):
        taxa_de_acerto = random.randint(0, 20)
        damage = 0
        critico = ""
        if taxa_de_acerto == 1:
            critico = "miss"
            damage = 0
        elif taxa_de_acerto == 20:
            critico = "critico"
            damage = self.dano * 2
        else:
            critico = "normal"
            damage = self.dano + (taxa_de_acerto/2)
        return {"damage": damage, "tipo": critico}


personagem = Heroi('um possivel Heroi', 1, 10, 5, 5)

orc = Inimigo('Orc', 15, 30)

arma_mao_direita = Arma('Espada Simples', 10)


@app.get("/")
def rota_main():
    return {"Nome": personagem.nome, "obs": "para acessar a luta entre com /atacar"}


@app.get("/inventario")
def rota_inventario():
    return {"inventario": personagem.inventario, "ouro": personagem.ouro, }


@app.get("/status_inimigo")
def status_inimigo():
    return {"nome": orc.nome, "poder": orc.poder, "vida": orc.vida}


def loot():
    loot = ["Espada Quebrada", "Pedra", "Poção", "Bota Furada"]
    personagem.ouro += 10
    return loot


@app.get("/atacar")
def atacar():
    ataque = arma_mao_direita.dano_infligido()
    dano = ataque["damage"]
    critico = ataque["tipo"]
    if orc.vida <= 0:
        return {"mensagem": "Inimigo já foi derrotado!"}
    else:
        if critico == "miss":
            return {"mensagem": "Erro critico: Miss", "dano_infligido": dano, "vida_inimigo": orc.vida}
        elif critico == "critico":
            orc.vida -= dano
            return {"mensagem": "Dano Critico!!!", "dano_infligido": dano, "vida_inimigo": orc.vida}
        else:
            orc.vida -= dano
            return {"dano_infligido": dano, "vida_inimigo": orc.vida}
    if orc.vida <= 0:
        orc.vida = 0
        itens_loot = loot()
        return {"resultado": "Vitoria", "dano": dano, "loot": itens_loot}
