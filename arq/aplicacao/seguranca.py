from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from arq.infraestrutura.database import get_db
from arq.infraestrutura.modelos import Usuario, PerfilEnum
from arq.aplicacao.auth import verificar_token

# define o endpoint de login para o OAuth2 para evitar ter que colocar munalmente o token em cada requisição
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/auth/login")
#função que recebe o token do cliente e e a sessão do banco para retornar o usuario ja logado(uso do depends para não ter que colocar manualmente o token)
def get_usuario_atual(
        token: str = Depends(oauth2_scheme), db: Session = Depends(get_db) 
        ) -> Usuario:
    #verifica se o token é valido usando o auth.py
    payload = verificar_token(token)
    #401 é o status de não autorizado
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
                "error": "TOKEN_INVALIDO",
                "message": "Token inválido ou expirado. Faça login novamente.",
                "details": [],
                "path": ""
            },
            headers={"WWW-Authenticate": "Bearer"}
            #é um padrão HTTP que diz ao cliente que precisa de autenticação Bearer
        )
    usuario_id= payload.get("sub")#Pega o ID do usuário de dentro do token (sub é um padrão do JWT para subject)
    usuario = db.query(Usuario). filter (Usuario.id == int(usuario_id)). first()
    if not usuario or not usuario.ativo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
                "error": "USUARIO_INEXISTENTE",
                "message": "Usuário não existe ou esta inativo",
                "details": [],
                "path": ""
        }
    )
    return usuario

#403 = usuário autorizado mas sem permissão
def requer_perfil(perfis: list):
    def verificar(usuario: Usuario = Depends(get_usuario_atual)):
        if usuario.perfil not in perfis:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                    "error": "SEM_ACESSO",
                    "message": "Você não tem a permissão necessaria pra acessar esse recurso",
                    "details": [],
                    "path": ""
                }
            )
        return usuario
    return verificar



