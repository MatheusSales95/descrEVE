#!/usr/bin/env python3
import random

nome = 'Um possivel Herói'
nivel = 1
ouro = 50.5
esta_vivo = True
inventario = ['Poção']
equipamento = ['Espada simples', 'Escudo simples']
atributos = {'forca': 5, 'agilidade': 6, 'destreza': 5}

print(f'''Eu sou {nome},
estou no LVL {nivel},
entre meus pertences estão {ouro} moedas de ouro,
uma {inventario[0]},
meus principais atributos são: Força {atributos['forca']},
Agilidade {atributos['agilidade']} e Destreza {atributos['destreza']} ''')


class inimigo:
    def __init__(self, nome, nivel, vida):
        self.nome = nome
        self.nivel = nivel
        self.vida = vida


orc = inimigo('Orc', 1, 50)


class arma:
    def __init__(self, nome, dano):
        self.nome = nome
        self.dano = dano

    def dano_infligido(self, damage):
        taxa_de_acerto = random.randint(1, 20)
        damage = 0
        if taxa_de_acerto == 1:
            print('Miss')
            damage = 0
        elif taxa_de_acerto == 20:
            print('Dano Critico')
            damage = self.dano * 2
        else:
            damage = (self.dano + taxa_de_acerto)/2

        return damage


espada = arma('Espada simples', 10)


def recolher(loot):

    global ouro
    global inventario

    print(f'seu loot foi: {loot}')
    for item in loot:
        coleta = input(f'Voce quer {item}? ')
        if coleta.strip().lower() == 'sim':
            print(f"Você coletou: {item}")
            inventario.append(item)
            if item == 'Ouro':
                print(f'Você encontrou ouro! agora voce tem {ouro + 1}')
        else:
            print(f"Você não coletou: {item}")
    for item in inventario:
        if item == 'Ouro':
            inventario.remove(item)
        else:
            print(f"Item no inventário: {item}")


def batalha():
    hp = orc.vida
    while (hp > 0):
        print(f'A vida do Orc é {hp}')
        dano = espada.dano_infligido(espada.dano)
        print(f'Você causou {dano} de dano')
        hp -= dano
        if hp <= 0:
            loot = ["Espada Quebrada", "Ouro", "Pedra",
                    "Ouro", "Poção", "Bota Furada"]
            print('Voce derrotou o inimigo')
            recolher(loot)
            break


batalha()

if esta_vivo:
    resposta = input('Deseja abrir a porta? ')
    if resposta.strip().lower() == 'sim':
        if 'Chave Mestra' in inventario:
            print('A porta se abriu')
        elif 'Chave Mestra' not in inventario:
            print('Você não tem a chave')
            arrombar = input('Deseja tentar arrombar a porta? ')
            if arrombar.strip().lower() == 'sim':
                if nivel >= 5:
                    print('Você arromba a porta')
                else:
                    print(
                        'Porta trancada.Você precisa ser nível 5+ para arrombar a porta.')
            else:
                print('Você nao tenta arrombar a porta')
        else:
            print('Porta trancada. Você precisa de uma Chave Mestra para abrir a porta')

    else:
        print('Porta trancada. Você não faz nada!')
else:
    print('Você está morto...')
