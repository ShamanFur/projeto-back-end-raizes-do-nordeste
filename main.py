from fastapi import FastAPI
from arq.api import auth, unidades, produtos, estoque, pedidos, pagamentos, fidelidade

app = FastAPI(
    title="Projeto: Raízes do Nordeste API",
    description="API Back-end para o projeto da rede de lanchonetes Raízes do Nordeste",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(unidades.router)
app.include_router(produtos.router)
app.include_router(estoque.router)
app.include_router(pedidos.router)
app.include_router(pagamentos.router)
app.include_router(fidelidade.router)

@app.get("/")
def raiz():
    return {"mensagem": "A API da Raízes do Nordeste funcionando!"}