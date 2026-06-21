from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from arq.infraestrutura.database import get_db
from arq.infraestrutura.modelos import Pedido, Pagamento, Fidelidade, StatusPedidoEnum, StatusPagamentoEnum
from arq.dominio.schemas import PagamentoResposta
from arq.aplicacao.pagamento import processar_pagamento
import json

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

@router.post("/{pedido_id}/processar", response_model=PagamentoResposta, status_code=201)
def processar_pagamento_mock(pedido_id:int, db:Session = Depends(get_db)):
    # busca o pedido
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=404, detail={
                "error": "PEDIDO_NAO_ENCONTRADO",
                "message": "Pedido não existe!",
                "details": [],
                "path": f"/pagamentos/{pedido_id}/processar"
            }
        )
    # verifica se o pedido foi pago
    if pedido.status != StatusPedidoEnum.AGUARDANDO_PAGAMENTO:
        raise HTTPException(status_code=409, detail={
            "error": "PEDIDO_JA_PROCESSADO",
            "message": f"Este pedido já foi processado. E esta atualmente: {pedido.status.value}",
            "details": [],
            "path": f"/pagamentos/{pedido_id}/processar"
            }
        )
    # processa o pagemnto mock
    resultado_mock = processar_pagamento(
        pedido_id=pedido_id,
        valor=pedido.total,
        forma_pagamento="Mock"
    )
# status baseado no resultado do pagamento
    status_pagamento = StatusPagamentoEnum.APROVADO if resultado_mock["status"] == "Aprovado" else StatusPagamentoEnum.RECUSADO

# registra o pagamento
    pagamento= Pagamento(
    pedido_id=pedido_id,
    forma_pagamento="Mock",
    status=status_pagamento,
    payload=json.dumps(resultado_mock)
)
    db.add(pagamento)

#atualiza o status do pedido
    if status_pagamento == StatusPagamentoEnum.APROVADO:
        pedido.status = StatusPedidoEnum.PAGO

# adiciona pontos de fidelidade sendo 1 ponto por real gasto
    fidelidade = db.query(Fidelidade).filter(Fidelidade.cliente_id == pedido.cliente_id).first()
    if fidelidade:
        fidelidade.pontos += int(pedido.total)

    db.commit()
    db.refresh(pagamento)
    return pagamento