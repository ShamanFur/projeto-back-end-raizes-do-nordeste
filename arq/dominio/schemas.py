from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from arq.infraestrutura.modelos import PerfilEnum, CanalPedidoEnum, StatusPedidoEnum, StatusPagamentoEnum

# todo schemas do usuario se faltar ou o email nao funcionar retorna com erro 422

#             USUARIO
#cadastro do usuario
class UsuarioCadastro(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    consentimento_lgpd: bool

#login do usuario
class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str
    
#resposta ao usuario
class UsuarioResposta(BaseModel):
    id: int
    nome: str
    email: EmailStr
    perfil: PerfilEnum
    ativo: bool
    class Config:#converter um objeto do banco direto para esse schema
        from_attributes = True

#             TOKEN
#token de autenticação
class Token(BaseModel):
    acesso_token: str
    token_tipo: str
    user: UsuarioResposta

#             UNIDADE
# unidade de cada restaurante (crirar e consultar)
class UnidadeCriar(BaseModel):
    nome: str
    endereco: str

class UnidadeResposta(BaseModel):
    id: int
    nome: str
    endereco: str
    ativo: bool
    class Config:
        from_attributes = True

#         PRODUTOS
class ProdutoCriar(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: float

class ProdutoResposta(BaseModel):
    id: int
    nome: str 
    descricao: Optional[str] = None
    preco: float
    ativo: bool
    class Config:
        from_attributes = True

#         ESTOQUE (ENTRADA/SAIDA)
class EstoqueMovimentar(BaseModel):
    unidade_id: int
    produto_id: int
    quantidade: int

class EstoqueResposta(BaseModel):
    id: int
    unidade_id: int
    produto_id: int
    quantidade: int
    class Config:
        from_attributes= True

#         PEDIDO
class ItemPedidoCriar(BaseModel):
    produto_id: int
    quantidade: int

class PedidoCriar(BaseModel):
    unidade_id: int
    canal_pedido: CanalPedidoEnum
    itens: List[ItemPedidoCriar]
    forma_pagamento: str

class ItemPedidoResposta(BaseModel):
      produto_id: int
      quantidade: int
      preco_unitario: float
      class Config:
          from_attributes = True

class PedidoResposta(BaseModel):
    id: int
    status: StatusPedidoEnum
    canal_pedido: CanalPedidoEnum
    total: float
    criado_em: datetime
    itens: List[ItemPedidoCriar]
    class Config:
        from_attributes = True

#           PAGAMENTO 
class PagamentoResposta(BaseModel):
    id: int
    pedido_id: int
    forma_pagamento: str
    status: StatusPagamentoEnum
    class Config:
        from_attributes = True

#             FIDELIDADE
class FidelidadeReposta(BaseModel):
    id: int
    cliente_id: int
    pontos: int 
    class Config:
        from_attributes = True

#erro padrao(vai virar um Json é um schema Pydantic, quando o FastAPI retorna ela se converte em Json) 
class ErroPadrao(BaseModel):
    error: str
    mensagens: str
    detalhes: Optional[List[dict]] = []
    path: Optional[str] = None


