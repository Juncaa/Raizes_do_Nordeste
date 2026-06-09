from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import Base, engine, pegar_banco
from app.tabelas import Auditoria, Pedido, Unidade, Usuario
from app.regras import buscar_cardapio_da_unidade, calcular_saldo_fidelidade, criar_pedido, mudar_status_pedido, pagar_pedido
from app.contratos import (
    AuditoriaSaida,
    LoginEntrada,
    PagamentoEntrada,
    PagamentoSaida,
    PedidoEntrada,
    PedidoSaida,
    SaldoFidelidadeSaida,
    StatusEntrada,
    TokenSaida,
    UnidadeSaida,
)
from app.login import criar_token, exigir_perfil, senha_confere, usuario_atual

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Raízes do Nordeste API",
    description="API REST para pedidos, pagamento mock, estoque, fidelidade e auditoria.",
    version="1.0.0"
)


@app.exception_handler(HTTPException)
def tratar_erros_http(request: Request, erro: HTTPException):
    return JSONResponse(
        status_code=erro.status_code,
        content={"erro": erro.status_code, "mensagem": erro.detail},
    )


@app.exception_handler(RequestValidationError)
def tratar_erros_validacao(request: Request, erro: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"erro": 422, "mensagem": "Dados inválidos.",
                 "detalhes": erro.errors()},
    )


@app.get("/")
def inicio():
    return {"status": "online", "mensagem": "API Raízes do Nordeste funcionando."}


@app.post("/auth/login", response_model=TokenSaida, tags=["Auth"])
def login(dados_login: LoginEntrada, banco: Session = Depends(pegar_banco)):
    usuario = banco.query(Usuario).filter(
        Usuario.email == dados_login.email).first()

    if not usuario or not senha_confere(dados_login.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=401, detail="E-mail ou senha inválidos.")

    token = criar_token(usuario)
    return {"access_token": token, "token_type": "bearer", "usuario": usuario}


@app.get("/unidades", response_model=list[UnidadeSaida], tags=["Unidades e Cardápio"])
def listar_unidades(banco: Session = Depends(pegar_banco)):
    return banco.query(Unidade).filter(Unidade.ativa == True).all()


@app.get("/unidades/{unidade_id}/cardapio", tags=["Unidades e Cardápio"])
def consultar_cardapio(unidade_id: int, banco: Session = Depends(pegar_banco)):
    produtos = buscar_cardapio_da_unidade(banco, unidade_id)
    return produtos


@app.post("/pedidos", response_model=PedidoSaida, status_code=201, tags=["Pedidos"])
def cadastrar_pedido(
    dados_pedido: PedidoEntrada,
    usuario_logado: Usuario = Depends(usuario_atual),
    banco: Session = Depends(pegar_banco),
):

    return criar_pedido(banco, dados_pedido, usuario_logado)


@app.get("/pedidos", response_model=list[PedidoSaida], tags=["Pedidos"])
def listar_pedidos(
    canalPedido: str | None = None,
    status: str | None = None,
    usuario_logado: Usuario = Depends(usuario_atual),
    banco: Session = Depends(pegar_banco),
):

    consulta = banco.query(Pedido)

    if usuario_logado.perfil == "CLIENTE":
        consulta = consulta.filter(Pedido.cliente_id == usuario_logado.id)

    if canalPedido:
        consulta = consulta.filter(Pedido.canal_pedido == canalPedido.upper())

    if status:
        consulta = consulta.filter(Pedido.status == status.upper())

    return consulta.order_by(Pedido.id.desc()).all()


@app.get("/pedidos/{pedido_id}", response_model=PedidoSaida, tags=["Pedidos"])
def consultar_pedido(
    pedido_id: int,
    usuario_logado: Usuario = Depends(usuario_atual),
    banco: Session = Depends(pegar_banco),
):
    pedido = banco.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    if usuario_logado.perfil == "CLIENTE" and pedido.cliente_id != usuario_logado.id:
        raise HTTPException(
            status_code=403, detail="Você não pode consultar pedido de outro cliente.")

    return pedido


@app.patch("/pedidos/{pedido_id}/status", response_model=PedidoSaida, tags=["Pedidos"])
def atualizar_status(
    pedido_id: int,
    dados_status: StatusEntrada,
    usuario_logado: Usuario = Depends(
        exigir_perfil("COZINHA", "GERENTE", "ADMIN")),
    banco: Session = Depends(pegar_banco),
):
    return mudar_status_pedido(banco, pedido_id, dados_status.status, usuario_logado)


@app.post("/pagamentos/pedidos/{pedido_id}", response_model=PagamentoSaida, tags=["Pagamentos"])
def pagamento_mock(
    pedido_id: int,
    dados_pagamento: PagamentoEntrada,
    usuario_logado: Usuario = Depends(usuario_atual),
    banco: Session = Depends(pegar_banco),
):
    return pagar_pedido(banco, pedido_id, dados_pagamento, usuario_logado)


@app.get("/fidelidade/saldo", response_model=SaldoFidelidadeSaida, tags=["Fidelidade"])
def consultar_saldo_fidelidade(
    usuario_logado: Usuario = Depends(usuario_atual),
    banco: Session = Depends(pegar_banco),
):
    pontos = calcular_saldo_fidelidade(banco, usuario_logado.id)
    return {"usuario_id": usuario_logado.id, "pontos": pontos}


@app.get("/auditorias", response_model=list[AuditoriaSaida], tags=["Auditoria"])
def listar_auditorias(
    usuario_logado: Usuario = Depends(exigir_perfil("ADMIN", "GERENTE")),
    banco: Session = Depends(pegar_banco),
):
    return banco.query(Auditoria).order_by(Auditoria.id.desc()).limit(50).all()
