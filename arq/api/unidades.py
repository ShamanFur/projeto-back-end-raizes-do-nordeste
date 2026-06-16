from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from arq.infraestrutura.database import get_db
from arq.infraestrutura.modelos import Unidade
from arq.dominio.schemas import UnidadeCriar, UnidadeResposta
from typing import List

router = APIRouter(prefix="/unidades", tags= ["Unidades"])#endpoints começam com /unidades

@router.post("/", response_model=UnidadeResposta, status_code=201)#cria as unidades como um endpoint Post e depois de receber os dado vai retornar o status 201 
def criar_unidade(unidade: UnidadeCriar, db:Session = Depends(get_db)):
    nova_unidade = Unidade(
        nome= unidade.nome,
        endereco = unidade.endereco
        #ativa esta default = a true entao nao precisa informar
    )
    db.add (nova_unidade)
    db.commit()
    db.refresh(nova_unidade)
    return nova_unidade

@router.get("/", response_model=List[UnidadeResposta])
def listar_unidades(db: Session=Depends(get_db)):
    return db.query(Unidade).filter(Unidade.ativo==True).all()
#endpoint Get retorna todas as unidades ativas e o filter(Unidade.ativa == True) garante que unidades desativadas não aparecem na lista

@router.get("/{unidade_id}", response_model=UnidadeResposta)#o {unidade_id} é um path param fazendo o ID aparecer na própria URL
def buscar_unidade(unidade_id: int, db: Session= Depends(get_db)):
    unidade = db.query(Unidade). filter(Unidade.id == unidade_id).first()
    if not unidade:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "UNIDADE_INEXISTENTE",
                "message": "Unidade não existe :( ",
                "details": [],
                "path": f"/unidades/{unidade_id}"
            }
        )
    return unidade

@router.patch("/{unidades_id}/desativar", status_code=204)#endpoint Patch pq só vamos atualizar um campo/ 204 = sem conteudo
def desativar_unidade(unidade_id: int, db: Session=Depends(get_db)):
    unidade = db.query(Unidade). filter(Unidade.id == unidade_id).first()
    if not unidade:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "UNIDADE_NAO_ENCONTRADA",
                "message": "Unidade não encontrada.",
                "details": [],
                "path": f"/unidades/{unidade_id}/desativar"
            }
        )
    unidade.ativa = False #troca o ativa de true para false continuando no banco de dados mas sem aparecer nas listas
    db.commit()

