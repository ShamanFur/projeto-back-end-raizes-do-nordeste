from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from arq.infraestrutura.database import get_db
from arq.infraestrutura.modelos import Pedido, ItemPedido, Produto, Estoque, StatusPedidoEnum, Pagamento, Fidelidade, StatusPagamentoEnum, PerfilEnum
from arq.dominio.schemas import PedidoCriar, PedidoResposta
from typing import List, Optional
from arq.aplicacao.seguranca import get_usuario_atual, requer_perfil

router= APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.post("/", response_model= PedidoResposta, status_code=201)
def criar_pedido(pedido: PedidoCriar, db: Session = Depends(get_db), usuario_atual = Depends(get_usuario_atual)):
    #protecao JWT (so usuarios logados)
    # calcula e valida os itens e estoque
    total = 0.0
    itens_validados =[]

    for item in pedido.itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if not produto:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "PRODUTO_NAO_ENCONTRADO",
                    "message": f"Produto {item.produto_id} não encontrado",
                    "details": [],
                    "path": "/pedidos"
                }
            )
        estoque = db.query(Estoque).filter (Estoque.unidade_id == pedido.unidade_id, Estoque.produto_id== item.produto_id).first()
        if not estoque or estoque.quantidade < item.quantidade:#not estoque = caso de nunca ter tido estoque
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "ESTOQUE_INSUFICIENTE",
                    "message": f"Estoque insuficiente para o produto {produto.nome}.",
                    "details": [
                        {"field": f"itens[{item.produto_id}].quantidade",
                         "issue": f"Disponível: {estoque.quantidade if estoque else 0}"}],
                    "path": "/pedidos"
                }
            )
        total += produto.preco * item.quantidade
        itens_validados.append((produto, item.quantidade, estoque))
    #cria o pedido
    novo_pedido = Pedido(
        cliente_id= usuario_atual.id, #arrumado
        unidade_id= pedido.unidade_id,
        canal_pedido= pedido.canal_pedido,
        total= total
    )
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    # cria os itens e baixa o estoque
    for produto, quantidade, estoque in itens_validados:
        item_pedido =ItemPedido(
            pedido_id = novo_pedido.id,
            produto_id = produto.id,
            quantidade = quantidade,
            preco_unitario= produto.preco 
        )
        db.add(item_pedido)
        estoque.quantidade -= quantidade

    db.commit()
    db.refresh(novo_pedido)
    return novo_pedido

#lisca dos pedidos com filtro
@router.get("/",response_model=List[PedidoResposta])
def listar_pedidos(
    canal_pedido: Optional[str] = None,
    status: Optional[str] = None,
    db: Session= Depends(get_db), 
    usuario_atual =Depends(get_usuario_atual)):

    query= db.query(Pedido)
    if canal_pedido:
        query = query.filter(Pedido.canal_pedido == canal_pedido)
    if status:
        query= query.filter(Pedido.status == status)
    return query.all()

@router.get("/{pedido_id}", response_model=PedidoResposta)
def buscar_pedido(pedido_id: int, db:Session=Depends(get_db), usuario_atual =Depends(get_usuario_atual)):
    pedido= db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "PEDIDO_NAO_ENCONTRADO",
                "message": "Pedido não foi localizado!!",
                "details": [],
                "path": f"/pedidos/{pedido_id}"
            }
        )
    return pedido

#atualiza o status do pedido
@router.patch("/{pedido_id}/status",response_model=PedidoResposta)
def atualizar_status(pedido_id: int, novo_status: StatusPedidoEnum, db:Session=Depends(get_db), usuario_atual= Depends(requer_perfil([PerfilEnum.ADMIN, PerfilEnum.GERENTE, PerfilEnum.COZINHA]))):
    pedido = db.query(Pedido).filter (Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "PEDIDO_NAO_ENCONTRADO",
                "message": "Pedido não foi localizado!!",
                "details": [],
                "path": f"/pedidos/{pedido_id}/status"
            }
        )
    pedido.status= novo_status
    db.commit()
    db.refresh(pedido)
    return pedido

#cancelar pedido mas sem poder cancelar o que ja foi entregue
@router.patch("/{pedido_id}/cancelar", response_model=PedidoResposta)
def cancelar_pedido(pedido_id:int, db:Session=Depends(get_db), usuario_atual =Depends(get_usuario_atual)):
    pedido = db.query(Pedido).filter (Pedido.id== pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "PEDIDO_NAO_ENCONTRADO",
                "message": "Pedido não foi localizado!!",
                "details": [],
                "path": f"/pedidos/{pedido_id}/cancelar"
            }
        )
    if pedido.status == StatusPedidoEnum.ENTREGUE:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "PEDIDO_JA_ENTREGUE",
                "message": "Pedido já entregue, não é possivel cancelar!",
                "details": [],
                "path": f"/pedidos/{pedido_id}/cancelar"
            }
        )
    pedido.status = StatusPedidoEnum.CANCELADO
    db.commit()
    db.refresh(pedido)
    return pedido


