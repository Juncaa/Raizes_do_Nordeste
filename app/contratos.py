from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginEntrada(BaseModel):
    email: EmailStr
    senha: str


class UsuarioSaida(BaseModel):
    id: int
    nome: str
    email: str
    perfil: str

    model_config = ConfigDict(from_attributes=True)


class TokenSaida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioSaida


class UnidadeSaida(BaseModel):
    id: int
    nome: str
    cidade: str
    uf: str
    cozinha_completa: bool
    ativa: bool

    model_config = ConfigDict(from_attributes=True)


class ProdutoSaida(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float
    pontos_gerados: int

    model_config = ConfigDict(from_attributes=True)


class ItemPedidoEntrada(BaseModel):
    produto_id: int = Field(alias="produtoId")
    quantidade: int = Field(gt=0)

    model_config = ConfigDict(populate_by_name=True)


class PedidoEntrada(BaseModel):
    canal_pedido: str = Field(alias="canalPedido")
    unidade_id: int = Field(alias="unidadeId")
    itens: List[ItemPedidoEntrada]

    model_config = ConfigDict(populate_by_name=True)


class ItemPedidoSaida(BaseModel):
    produto_id: int
    quantidade: int
    preco_unitario: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)


class PedidoSaida(BaseModel):
    id: int
    cliente_id: int
    unidade_id: int
    canal_pedido: str
    status: str
    total: float
    itens: List[ItemPedidoSaida]

    model_config = ConfigDict(from_attributes=True)


class PagamentoEntrada(BaseModel):
    forma_pagamento: str = Field("MOCK", alias="formaPagamento")
    aprovado: bool = True

    model_config = ConfigDict(populate_by_name=True)


class PagamentoSaida(BaseModel):
    id: int
    pedido_id: int
    forma_pagamento: str
    status: str
    retorno_gateway: str

    model_config = ConfigDict(from_attributes=True)


class StatusEntrada(BaseModel):
    status: str


class AuditoriaSaida(BaseModel):
    id: int
    usuario_id: int
    acao: str
    detalhe: str

    model_config = ConfigDict(from_attributes=True)


class SaldoFidelidadeSaida(BaseModel):
    usuario_id: int
    pontos: int
