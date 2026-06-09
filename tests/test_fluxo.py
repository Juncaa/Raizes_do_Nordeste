from fastapi.testclient import TestClient
from app.main import app
from app.criar_dados import criar_dados_iniciais

client = TestClient(app)


def setup_module(module):
    criar_dados_iniciais()


def token(email):
    resposta = client.post(
        '/auth/login', json={'email': email, 'senha': '123456'})
    assert resposta.status_code == 200
    return resposta.json()['access_token']


def test_fluxo_pedido_pagamento_status_e_auditoria():
    token_cliente = token('cliente@exemplo.com')
    token_cozinha = token('cozinha@exemplo.com')
    token_admin = token('admin@exemplo.com')

    cab_cliente = {'Authorization': f'Bearer {token_cliente}'}
    cab_cozinha = {'Authorization': f'Bearer {token_cozinha}'}
    cab_admin = {'Authorization': f'Bearer {token_admin}'}

    unidades = client.get('/unidades')
    assert unidades.status_code == 200
    assert len(unidades.json()) >= 1

    cardapio = client.get('/unidades/1/cardapio')
    assert cardapio.status_code == 200
    assert len(cardapio.json()) >= 1

    pedido = client.post('/pedidos', headers=cab_cliente, json={
        'canalPedido': 'APP',
        'unidadeId': 1,
        'itens': [{'produtoId': 1, 'quantidade': 2}]
    })
    assert pedido.status_code == 201
    pedido_id = pedido.json()['id']
    assert pedido.json()['status'] == 'AGUARDANDO_PAGAMENTO'

    pagamento = client.post(f'/pagamentos/pedidos/{pedido_id}', headers=cab_cliente, json={
        'formaPagamento': 'MOCK',
        'aprovado': True
    })
    assert pagamento.status_code == 200
    assert pagamento.json()['status'] == 'APROVADO'

    status = client.patch(
        f'/pedidos/{pedido_id}/status', headers=cab_cozinha, json={'status': 'PRONTO'})
    assert status.status_code == 200
    assert status.json()['status'] == 'PRONTO'

    auditoria = client.get('/auditorias', headers=cab_admin)
    assert auditoria.status_code == 200
    assert len(auditoria.json()) >= 1


def test_erros_principais():
    token_cliente = token('cliente@exemplo.com')
    cab_cliente = {'Authorization': f'Bearer {token_cliente}'}

    sem_token = client.get('/pedidos')
    assert sem_token.status_code == 401

    sem_permissao = client.get('/auditorias', headers=cab_cliente)
    assert sem_permissao.status_code == 403

    sem_canal = client.post('/pedidos', headers=cab_cliente, json={
        'unidadeId': 1,
        'itens': [{'produtoId': 1, 'quantidade': 1}]
    })
    assert sem_canal.status_code == 422

    sem_estoque = client.post('/pedidos', headers=cab_cliente, json={
        'canalPedido': 'APP',
        'unidadeId': 1,
        'itens': [{'produtoId': 1, 'quantidade': 999}]
    })
    assert sem_estoque.status_code == 409
