from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from arq.infraestrutura.database import get_db
from arq.infraestrutura.modelos import Estoque, Produto, Unidade
from arq.dominio.schemas import EstoqueMovimentar, EstoqueResposta
from typing import List

router= APIRouter(prefix="/estoque", tags=["Estoque"])

@router.post("/entrada", response_model= EstoqueResposta, status_code=201) # verifica se a unidade existe e se nao retorna erro 404 isso vale pra todas as verificações
def entrada_estoque(dados: EstoqueMovimentar, db: Session =Depends(get_db)):
    unidade = db.query(Unidade). filter(Unidade.id == dados.unidade_id).first()
    if not unidade:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "UNIDADE_NAO_EXISTE",
                "message": "Unidade não encontrada :( ",
                "details": [],
                "path": "/estoque/entrada"
            }
        )
    produto = db.query(Produto).filter(Produto.id == dados.produto_id).first()# verifica se o produto existe
    if not produto:
        raise HTTPException(
            status_code=404,
            detail={
                 "error": "PRODUTO_INEXISTENTE",
                "message": "Produto não registrado!",
                "details": [],
                "path": "/estoque/entrada"
            }
        )
    # verifica se ja existe estoque para esse produto nessa unidade
    estoque= db.query(Estoque). filter(Estoque.unidade_id == dados.unidade_id, Estoque.produto_id == dados.produto_id).first()
    if estoque:
        # se tiver ele soma a quantidade
        estoque.quantidade += dados.quantidade
    else:
        # se nao cria um novo registro
        estoque = Estoque(
            unidade_id = dados.unidade_id,
            produto_id = dados.produto_id,
            quantidade= dados.quantidade
        )
        db.add(estoque)
    db.commit()
    db.refresh(estoque)
    return estoque

#endpoint para remover proodutos do estoque quando o pedido é feito
@router.post("/saida", response_model=EstoqueResposta)
def saida_estoque(dados:EstoqueMovimentar, db:Session=Depends(get_db)):
    estoque = db.query(Estoque).filter(Estoque.unidade_id == dados.unidade_id, Estoque.produto_id== dados.produto_id).first()
    if not estoque:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "ESTOQUE_NAO_ENCONTRADO",
                "message": "A unidade atual não possui nenhum deste produto em estoque!",
                "details": [],
                "path": "/estoque/saida"
            }
        )
    #verifica se tem o suficiente e se nao tiver retorna 409 = confilto
    if estoque.quantidade < dados.quantidade:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "ESTOQUE_INSUFICIENTE",
                "message": "Quantidade insuficiente em estoque.",
                "details": [
                    {"field": "quantidade", "issue": f"Disponível: {estoque.quantidade}"}
                ],
                "path": "/estoque/saida"
            }
        )
    #tira a quantidade do estoque, salva e retorna o saldo atualizado
    estoque.quantidade -= dados.quantidade
    db.commit()
    db.refresh(estoque)
    return estoque

#consultar todos os produtos e suas quantidades naquela unidade
@router.get("/unidade/{unidade_id}", response_model=List[EstoqueResposta])
def consultar_unidade_estoque(unidade_id: int, db:Session=Depends(get_db)):
    unidade = db.query(Unidade). filter(Unidade.id == unidade_id).first()
    if not unidade:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "UNIDADE_NAO_ENCONTRADA",
                "message": "Unidade não encontrada!",
                "details": [],
                "path": f"/estoque/unidade/{unidade_id}"
            }
        )
    return db.query(Estoque). filter(Estoque.unidade_id == unidade_id).all()