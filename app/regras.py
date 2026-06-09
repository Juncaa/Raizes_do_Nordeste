from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.tabelas import Auditoria, Estoque, Fidelidade, ItemPedido, Pagamento, Pedido, Produto, Unidade, Usuario
from app.contratos import PagamentoEntrada, PedidoEntrada

CANAIS_VALIDOS = {"APP", "TOTEM", "BALCAO", "PICKUP", "WEB"}
STATUS_VALIDOS = {"AGUARDANDO_PAGAMENTO",
                  "EM_PREPARO", "PRONTO", "ENTREGUE", "CANCELADO"}


def anotar_auditoria(banco: Session, usuario_id: int, acao: str, detalhe: str):
    # Centraliza a auditoria para facilitar o registro
    registro = Auditoria(usuario_id=usuario_id, acao=acao, detalhe=detalhe)
    banco.add(registro)


def buscar_cardapio_da_unidade(banco: Session, unidade_id: int):
    unidade = banco.get(Unidade, unidade_id)
    if not unidade or not unidade.ativa:
        raise HTTPException(
            status_code=404, detail="Unidade não encontrada ou inativa.")

    produtos_liberados = []
    estoques = banco.query(Estoque).filter(
        Estoque.unidade_id == unidade_id, Estoque.quantidade > 0).all()

    for saldo in estoques:
        produto = saldo.produto
        if not produto.ativo:
            continue
        if produto.precisa_cozinha_completa and not unidade.cozinha_completa:
            continue
        produtos_liberados.append(produto)

    return produtos_liberados


def criar_pedido(banco: Session, dados: PedidoEntrada, cliente: Usuario) -> Pedido:
    canal = dados.canal_pedido.upper()
    if canal not in CANAIS_VALIDOS:
        raise HTTPException(
            status_code=422, detail="canalPedido inválido. Use APP, TOTEM, BALCAO, PICKUP ou WEB.")

    unidade = banco.get(Unidade, dados.unidade_id)
    if not unidade or not unidade.ativa:
        raise HTTPException(
            status_code=404, detail="Unidade não encontrada ou inativa.")

    if not dados.itens:
        raise HTTPException(
            status_code=422, detail="O pedido precisa ter pelo menos um item.")

    pedido_novo = Pedido(
        cliente_id=cliente.id,
        unidade_id=unidade.id,
        canal_pedido=canal,
        status="AGUARDANDO_PAGAMENTO",
    )
    banco.add(pedido_novo)
    banco.flush()

    total_pedido = 0

    for item_recebido in dados.itens:
        produto = banco.get(Produto, item_recebido.produto_id)
        if not produto or not produto.ativo:
            raise HTTPException(
                status_code=404, detail=f"Produto {item_recebido.produto_id} não encontrado.")

        if produto.precisa_cozinha_completa and not unidade.cozinha_completa:
            raise HTTPException(
                status_code=409, detail="Produto indisponível nesta unidade.")

        saldo = banco.query(Estoque).filter(
            Estoque.unidade_id == unidade.id,
            Estoque.produto_id == produto.id,
        ).first()

        if not saldo or saldo.quantidade < item_recebido.quantidade:
            raise HTTPException(
                status_code=409, detail="Estoque insuficiente para concluir o pedido.")

        saldo.quantidade -= item_recebido.quantidade
        subtotal = produto.preco * item_recebido.quantidade
        total_pedido += subtotal

        item_do_pedido = ItemPedido(
            pedido_id=pedido_novo.id,
            produto_id=produto.id,
            quantidade=item_recebido.quantidade,
            preco_unitario=produto.preco,
            subtotal=subtotal,
        )
        banco.add(item_do_pedido)

    pedido_novo.total = total_pedido
    anotar_auditoria(banco, cliente.id, "PEDIDO_CRIADO",
                     f"Pedido {pedido_novo.id} criado pelo canal {canal}.")
    banco.commit()
    banco.refresh(pedido_novo)
    return pedido_novo


def pagar_pedido(banco: Session, pedido_id: int, dados: PagamentoEntrada, usuario: Usuario) -> Pagamento:
    pedido = banco.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    if pedido.status != "AGUARDANDO_PAGAMENTO":
        raise HTTPException(
            status_code=409, detail="Este pedido não está aguardando pagamento.")

    if dados.aprovado:
        status_pagamento = "APROVADO"
        retorno = "Pagamento mock aprovado pelo gateway simulado."
        pedido.status = "EM_PREPARO"
    else:
        status_pagamento = "RECUSADO"
        retorno = "Pagamento mock recusado pelo gateway simulado."
        pedido.status = "CANCELADO"

    pagamento = Pagamento(
        pedido_id=pedido.id,
        forma_pagamento=dados.forma_pagamento,
        status=status_pagamento,
        retorno_gateway=retorno,
    )
    banco.add(pagamento)

    if status_pagamento == "APROVADO":
        gerar_pontos_fidelidade(banco, pedido)

    anotar_auditoria(banco, usuario.id, "PAGAMENTO_MOCK",
                     f"Pedido {pedido.id}: {status_pagamento}.")
    banco.commit()
    banco.refresh(pagamento)
    return pagamento


def mudar_status_pedido(banco: Session, pedido_id: int, novo_status: str, usuario: Usuario) -> Pedido:
    novo_status = novo_status.upper()
    if novo_status not in STATUS_VALIDOS:
        raise HTTPException(
            status_code=422, detail="Status inválido para o pedido.")

    pedido = banco.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    pedido.status = novo_status
    anotar_auditoria(banco, usuario.id, "STATUS_PEDIDO",
                     f"Pedido {pedido.id} alterado para {novo_status}.")
    banco.commit()
    banco.refresh(pedido)
    return pedido


def gerar_pontos_fidelidade(banco: Session, pedido: Pedido):
    cliente = banco.get(Usuario, pedido.cliente_id)
    if not cliente or not cliente.aceita_fidelidade:
        return

    pontos = int(pedido.total // 10)
    if pontos <= 0:
        pontos = 1

    banco.add(Fidelidade(usuario_id=cliente.id,
              pontos=pontos, motivo=f"Pedido {pedido.id}"))


def calcular_saldo_fidelidade(banco: Session, usuario_id: int) -> int:
    lancamentos = banco.query(Fidelidade).filter(
        Fidelidade.usuario_id == usuario_id).all()
    return sum(item.pontos for item in lancamentos)
