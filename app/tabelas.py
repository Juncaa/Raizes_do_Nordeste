from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


# Aqui guarda os usuários do sistema e o perfil de acesso de cada um.

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    perfil = Column(String)
    aceita_fidelidade = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)


# Cada unidade possui seu próprio cardápio e também seu próprio estoque.
class Unidade(Base):
    __tablename__ = "unidades"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    cidade = Column(String)
    uf = Column(String)
    cozinha_completa = Column(Boolean, default=True)
    ativa = Column(Boolean, default=True)

    estoques = relationship("Estoque", back_populates="unidade")
    pedidos = relationship("Pedido", back_populates="unidade")


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    descricao = Column(String)
    preco = Column(Float)
    precisa_cozinha_completa = Column(Boolean, default=False)
    ativo = Column(Boolean, default=True)
    pontos_gerados = Column(Integer, default=1)

    estoques = relationship("Estoque", back_populates="produto")


class Estoque(Base):
    __tablename__ = "estoques"

    id = Column(Integer, primary_key=True, index=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Integer, default=0)

    unidade = relationship("Unidade", back_populates="estoques")
    produto = relationship("Produto", back_populates="estoques")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    unidade_id = Column(Integer, ForeignKey("unidades.id"))
    canal_pedido = Column(String, index=True)
    status = Column(String, default="AGUARDANDO_PAGAMENTO")
    total = Column(Float, default=0)
    criado_em = Column(DateTime, default=datetime.utcnow)

    unidade = relationship("Unidade", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido",
                         cascade="all, delete-orphan")
    pagamentos = relationship("Pagamento", back_populates="pedido")


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Integer)
    preco_unitario = Column(Float)
    subtotal = Column(Float)

    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto")


# Pagamento mock (simulação)
class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    forma_pagamento = Column(String)
    status = Column(String)
    retorno_gateway = Column(String)
    criado_em = Column(DateTime, default=datetime.utcnow)

    pedido = relationship("Pedido", back_populates="pagamentos")


class Fidelidade(Base):
    __tablename__ = "fidelidade"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    pontos = Column(Integer, default=0)
    motivo = Column(String)
    criado_em = Column(DateTime, default=datetime.utcnow)


# Auditoria para registros.
class Auditoria(Base):
    __tablename__ = "auditorias"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer)
    acao = Column(String)
    detalhe = Column(String)
    criado_em = Column(DateTime, default=datetime.utcnow)
