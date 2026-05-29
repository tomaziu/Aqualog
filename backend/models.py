from pydantic import BaseModel, Field
from typing import Optional


class AdminLogin(BaseModel):
    senha: str


class Cliente(BaseModel):
    nome: str = Field(min_length=3)
    telefone: str = Field(min_length=8)
    endereco: str = Field(min_length=3)
    bairro: str = Field(min_length=2)
    referencia: Optional[str] = None


class Entregador(BaseModel):
    nome: str = Field(min_length=3)
    telefone: str = Field(min_length=8)
    veiculo: str = Field(min_length=2)
    codigo_acesso: str = Field(min_length=4)
    status: str = 'disponivel'


class EntregadorLogin(BaseModel):
    codigo_acesso: str


class Produto(BaseModel):
    nome: str = Field(min_length=2)
    preco: float = Field(gt=0)
    estoque: int = Field(ge=0)


class Pedido(BaseModel):
    cliente_id: int
    entregador_id: Optional[int] = None
    produto_id: int
    quantidade: int = Field(gt=0)
    forma_pagamento: str = Field(min_length=2)
    status: str = 'recebido'
