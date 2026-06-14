from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from arq.infraestrutura.database import Base
import enum

#classes enums para valores fixos 
#valores fixos
class PerfilEnum(enum.Enum):
    ADMIN = "admin"
    GERENTE = "GERENTE"
    COZINHA = "COZINHA"
    ATENDENTE = "ATENDENTE"
    CLIENTE = "CLIENTE"

#multiplos canais de pedido
class CanalPedidoEnum(str, enum.Enum):
    APP = "APP"
    TOTEM = "TOTEM"
    BALCAO ="BALCAO"
    PICKUP = "PICKUP"
    WEB = "WEB"

#estado do pedido
class StatusPedidoEnum(str, enum.Enum):
    AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO"
    PAGO = "PAGO"
    PREPARANDO = "PREPARANDO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CALCELADO"

#estado do pagamento
class StatusPagamentoEnum(str, enum.Enum):
    PENDENTE = "PENDENTE"
    RECUSADO = "RECUSADO"
    APROVADO = "APROVADO"

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column (Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(Enum(PerfilEnum), nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, server_default=func.now())
    consentimento_lgpd = Column(Boolean, default=False)

class Unidade(Base):
    __tablename__ = "unidades"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    endereco = Column(String(255), nullable=False)
    ativa = Column(Boolean, default=True)

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    preco = Column(Float, nullable=False)
    ativo = Column(Boolean, default=True)

class Estoque(Base):
    __tablename__ = "estoques"
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    quantidade = Column(Integer, default=0)
    produto = relationship("Produto")
    unidade = relationship("Unidade")


class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    canal_pedido = Column(Enum(CanalPedidoEnum), nullable=False)
    status = Column(Enum(StatusPedidoEnum), default=StatusPedidoEnum.AGUARDANDO_PAGAMENTO)
    total = Column(Float, nullable=False)
    criado_em = Column(DateTime, server_default=func.now())
    cliente = relationship("Usuario")
    unidade = relationship("Unidade")
    itens = relationship("ItemPedido", back_populates="pedido")
class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    produto = relationship("Produto")
    pedido = relationship("Pedido", back_populates="itens")

class Pagamento(Base):
    __tablename__ = "pagamentos"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    forma_pagamento = Column(String(50), nullable=False)
    status = Column(Enum(StatusPagamentoEnum), default=StatusPagamentoEnum.PENDENTE)
    payload = Column(Text, nullable=True) 
    criado_em = Column(DateTime, server_default=func.now())
    pedido = relationship("Pedido")

class Fidelidade(Base):
    __tablename__ = "fidelidades"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)
    pontos = Column(Integer, default=0)
    cliente = relationship("Usuario")