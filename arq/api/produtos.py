from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from arq.infraestrutura.database import get_db
from arq.infraestrutura.modelos import Produto
from arq.dominio.schemas import ProdutoCriar, ProdutoResposta
from typing import List

#é a mesma coisa da unidades a diferença é que ao inves de patch usamos o put pra atualizar tudo

router = APIRouter(prefix="/produtos", tags=["Produtos"])

@router.post("/", response_model=ProdutoResposta, status_code=201)
def criar_produto(produto: ProdutoCriar, db: Session = Depends(get_db)):
    novo_produto = Produto(
        nome=produto.nome,
        descricao=produto.descricao,
        preco=produto.preco
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto

@router.get("/", response_model=List[ProdutoResposta])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Produto).filter(Produto.ativo == True).all()

@router.get("/{produto_id}", response_model=ProdutoResposta)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "PRODUTO_INEXISTENTE",
                "message": "Produto não registrado!",
                "details": [],
                "path": f"/produtos/{produto_id}"
            }
        )
    return produto

@router.put("/{produto_id}", response_model=ProdutoResposta)
def atualizar_produto(produto_id: int, dados: ProdutoCriar, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "PRODUTO_INEXISTENTE",
                "message": "Produto não registrado! ",
                "details": [],
                "path": f"/produtos/{produto_id}"
            }
        )
    produto.nome = dados.nome
    produto.descricao = dados.descricao
    produto.preco = dados.preco
    db.commit()
    db.refresh(produto)
    return produto

@router.patch("/{produto_id}/desativar", status_code=204)
def desativar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "PRODUTO_INEXISTENTE",
                "message": "Produto não registrado!",
                "details": [],
                "path": f"/produtos/{produto_id}"
            }
        )
    produto.ativo = False
    db.commit()