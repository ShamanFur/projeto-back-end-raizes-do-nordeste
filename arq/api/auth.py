from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from arq.infraestrutura.database import get_db
from arq.infraestrutura.modelos import Usuario, Fidelidade
from arq.dominio.schemas import UsuarioCadastro, UsuarioLogin, Token, ErroPadrao
from arq.aplicacao.auth import hash_senha, verificar_senha, criar_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])

#POST
@router.post("/cadastro", response_model=Token, status_code=201)#201 = criado
def cadastrar(usuario: UsuarioCadastro, db: Session = Depends(get_db)):
    #verifica se email já existe
    existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existente:
        raise HTTPException(
            status_code=409, #erro de conflito
            detail={
                "error": "EMAIL_JA_CADASTRADO",
                "message": "Outra pessoa já esta usando este e-mail.",
                "details": [],
                "path": "/auth/cadastro"
            }
        )
    #verifica consentimento LGPD
    if not usuario.consentimento_lgpd:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "CONSENTIMENTO_LGPD_NEGADO",
                "message": "É necessário aceitar os termos de privacidade :)",
                "details": [],
                "path": "/auth/cadastro"
            }
        )
    #cria o usuário
    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=hash_senha(usuario.senha),
        consentimento_lgpd=usuario.consentimento_lgpd
    )
    db.add(novo_usuario) #adiciona
    db.commit()#salva
    db.refresh(novo_usuario)#atualiza

    #cria registro de fidelidade ja no momento que ele cria a conta
    fidelidade = Fidelidade(cliente_id=novo_usuario.id)
    db.add(fidelidade)
    db.commit()

    #gera token
    token = criar_token({"sub": str(novo_usuario.id), "perfil": novo_usuario.perfil.value})
    return Token(
        acesso_token=token,
        token_tipo="Bearer",
        user=novo_usuario
    )

@router.post("/login", response_model=Token, status_code=200)#200 = ok
def login(dados: UsuarioLogin, db: Session = Depends(get_db)):
    # busca usuário se nao achar manda o erro 401 de credenciais invalidas
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=401,
            detail={
                "error": "CREDENCIAIS_INVALIDAS",
                "message": "E-mail ou senha inválidos.",
                "details": [],
                "path": "/auth/login"
            }
        )
    if not usuario.ativo:
        raise HTTPException(
            status_code=403, #403 = proibido/sem acesso
            detail={
                "error": "USUARIO_INATIVO",
                "message": "Usuário está inativo, entre em contato com o suporte para reativar.",
                "details": [],
                "path": "/auth/login"
            }
        )
    token = criar_token({"sub": str(usuario.id), "perfil": usuario.perfil.value})
    return Token(
        acesso_token=token,
        token_tipo="Bearer",
        user=usuario
    )

