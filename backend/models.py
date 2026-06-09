from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class AdminLogin(BaseModel):
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    tipo: str
    nome: str


class Cliente(BaseModel):
    nome: str = Field(min_length=3)
    telefone: str = Field(min_length=8)
    endereco: str = Field(min_length=3)
    numero_casa: Optional[str] = None
    bairro: str = Field(min_length=2)
    referencia: Optional[str] = None


class Entregador(BaseModel):
    nome: str = Field(min_length=3)
    telefone: str = Field(min_length=8)
    veiculo: str = Field(min_length=2)
    codigo_acesso: str = Field(min_length=4)
    status: str = 'disponivel'


class EntregadorUpdate(BaseModel):
    nome: str = Field(min_length=3)
    telefone: str = Field(min_length=8)
    veiculo: str = Field(min_length=2)
    codigo_acesso: str = ''
    status: str = 'disponivel'


class EntregadorLogin(BaseModel):
    codigo_acesso: str


class Produto(BaseModel):
    nome: str = Field(min_length=2)
    preco: float = Field(gt=0)
    estoque: int = Field(ge=0)
    estoque_minimo: int = Field(default=5, ge=0)
    ativo: bool = True


class ConfiguracoesLoja(BaseModel):
    nome_loja: str = Field(default='ÁquaLog', min_length=2)
    subtitulo_loja: str = Field(default='Pedido online da distribuidora', min_length=2)
    aviso_cliente: Optional[str] = ''
    pix_chave: Optional[str] = ''
    estoque_minimo_padrao: int = Field(default=5, ge=0)
    loja_aberta: bool = True
    som_novo_pedido: bool = True


class Cupom(BaseModel):
    codigo: str = Field(min_length=2, max_length=40)
    percentual: float = Field(gt=0, le=100)
    ativo: bool = True
    validade_inicio: Optional[date] = None
    validade_fim: Optional[date] = None
    valor_minimo: float = Field(default=0, ge=0)
    limite_usos: Optional[int] = Field(default=None, ge=1)


class CancelamentoPedido(BaseModel):
    motivo: Optional[str] = Field(default='', max_length=255)


class Pedido(BaseModel):
    cliente_id: int
    entregador_id: Optional[int] = None
    produto_id: int
    quantidade: int = Field(gt=0)
    forma_pagamento: str = Field(min_length=2)
    status: str = 'recebido'


class PedidoEntregadorUpdate(BaseModel):
    entregador_id: Optional[int] = None


class PedidoItemSite(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)


class PedidoSite(BaseModel):
    nome: str = Field(min_length=3)
    telefone: str = Field(min_length=8)
    email: Optional[str] = None
    endereco: str = Field(min_length=3)
    numero_casa: Optional[str] = None
    bairro: str = Field(min_length=2)
    referencia: Optional[str] = None
    produto_id: Optional[int] = None
    quantidade: Optional[int] = Field(default=None, gt=0)
    itens: Optional[List[PedidoItemSite]] = None
    forma_pagamento: str = Field(min_length=2)
    cupom_codigo: Optional[str] = Field(default=None, max_length=40)


class ComprovantePix(BaseModel):
    conteudo: str = Field(min_length=3, max_length=250000)
    arquivo_nome: Optional[str] = Field(default=None, max_length=120)


class SuporteMensagem(BaseModel):
    mensagem: str = Field(min_length=1, max_length=1000)


class PaginacaoParams(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=200)
