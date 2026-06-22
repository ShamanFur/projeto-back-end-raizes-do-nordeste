from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from arq.infraestrutura.database import get_db
from arq.infraestrutura.modelos import Fidelidade, Usuario
from arq.dominio.schemas import FidelidadeReposta

router = APIRouter(prefix="/fidelidade", tags=["Fidelidade"])
#endpoints começam com /fidelidade

@router.get("/{cliente_id}", response_model=FidelidadeReposta)
def consultar_pontos(cliente_id:int, db:Session = Depends(get_db)):
#verifica se o cliente existe por isso importar o usuario
    cliente= db.query(Usuario) .filter(Usuario.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=404, detail={
                "error": "CLIENTE_NAO_ENCONTRADO",
                "message": "Cliente não possui cadastro.",
                "details": [],
                "path": f"/fidelidade/{cliente_id}"
            }
        )
    fidelidade = db.query(Fidelidade).filter(Fidelidade.cliente_id == cliente_id).first()
    if not fidelidade:
        raise HTTPException(status_code=404, detail={
            "error": "FIDELIDADE_INESXISTENTE",
                "message": "Esse cliente não possui um registro de fidelidade",
                "details": [],
                "path": f"/fidelidade/{cliente_id}"
            }
        )
    return fidelidade

@router.post("/{cliente_id}/resgatar", response_model=FidelidadeReposta)
def resgatar_pontos(cliente_id:int, pontos:int, db:Session= Depends(get_db)):
    # verifica se o cliente existe as mesmas de cima para garantir que o cliente existe
    cliente = db.query(Usuario).filter(Usuario.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "CLIENTE_NAO_ENCONTRADO",
                "message": "Cliente não possui cadastro.",
                "details": [],
                "path": f"/fidelidade/{cliente_id}/resgatar"
            }
        )
    fidelidade = db.query(Fidelidade).filter(Fidelidade.cliente_id == cliente_id).first()
    if not fidelidade:
        raise HTTPException(status_code=404, detail={
                "error": "FIDELIDADE_NAO_EXISTE",
                "message": "Esse cliente não possui um registro de fidelidade",
                "details": [],
                "path": f"/fidelidade/{cliente_id}/resgatar"
            }
        )
    # verifica se tem pontos suficientes
    if fidelidade.pontos < pontos:
        raise HTTPException(status_code=409, detail={
                "error": "PONTOS_INSUFICIENTES",
                "message": "Não é possível fazer o resgate por insuficiencia de pontos",
                "details": [
                    {"field": "pontos", "issue": f"Disponível: {fidelidade.pontos}"}#retorna os pontos disponiveis
                ],
                "path": f"/fidelidade/{cliente_id}/resgatar"
            }
        )
    # verifica consentimento LGPD
    if not cliente.consentimento_lgpd:
        raise HTTPException(status_code=403, detail={
                "error": "CONSENTIMENTO_LGPD_NECESSARIO",
                "message": "É necessário aceitar os termos de privacidade para usar o programa de fidelidade.",
                "details": [],
                "path": f"/fidelidade/{cliente_id}/resgatar"
            }
        )
    #subtrai os pontos, salva e retorna o saldo atualizado
    fidelidade.pontos -= pontos
    db.commit()
    db.refresh(fidelidade)
    return fidelidade
