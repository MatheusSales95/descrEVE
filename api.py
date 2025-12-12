from fastapi import FastAPI

app = FastAPI()

# Rota Principal (Home)
@app.get("/")
def home():
    return {"mensagem": "Olá! Minha primeira API está viva!"}

# Rota de Soma (Exemplo extra)
@app.get("/somar/{n1}/{n2}")
def somar(n1: int, n2: int):
    total = n1 + n2
    return {"resultado": total}
# ... (código anterior continua aqui)

@app.get("/verificar/{numero}")
def verificar_par_impar(numero: int):
    if numero % 2 == 0:
        return {"numero": numero, "status": "Par", "mensagem": "É divisível por 2!"}
    else:
        return {"numero": numero, "status": "Ímpar", "mensagem": "Sobra 1 na divisão por 2."}
