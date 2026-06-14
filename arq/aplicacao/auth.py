from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()
#valores estao na .env 
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

#usado pra criptografar as senhas dos tabela usuarios(o melhor baseando em videos do youtube e artigos)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#criptografa a senha usada antes de colocar no banco de dados 
def hash_senha (senha: str) -> str:
    return pwd_context.hash(senha)

#comparar as senhas e ver se batem mas sem descriptografar
def verificar_senha (senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha, senha_hash)

#crias o token e emitir o tempo de expiração 
def criar_token (dados: dict) -> str:
    dados_copia = dados.copy()
    expira_em = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    dados_copia.update({"exp": expira_em})
    return jwt.encode(dados_copia, SECRET_KEY, algorithm=ALGORITHM)

#verifica e valida o token e retorna os dados 
def verificar_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
