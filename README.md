# Raízes do Nordeste - Projeto Back-end

Projeto acadêmico da trilha **Back-end**, na qual foi desenvolvido um estudo de caso da rede de restaurante **Raízes do Nordeste**.

O sistema simula o fluxo principal de pedidos da rede, permitindo login de usuários, consulta de unidades e cardápio, criação de pedidos, controle de estoque, pagamento mock, atualização de status, fidelidade e auditoria.

A API implementa o fluxo principal:

**Pedido → Pagamento mock → Atualização de status**

Também possui autenticação por token, perfis de usuário, estoque por unidade, fidelidade, auditoria e filtro de pedidos por `canalPedido`.

## Tecnologias

- Python 3.12
- FastAPI
- SQLite
- SQLAlchemy
- PyJWT
- Pytest
- Postman

## Estrutura do projeto

```text
raizes_do_nordeste/
├── app/
│   ├── main.py       # rotas da API
│   ├── tabelas.py     # tabelas do banco
│   ├── contratos.py    # entradas e saídas da API
│   ├── regras.py     # regras de negócio
│   ├── login.py   # login, token e senha com hash
│   ├── database.py   # conexão com SQLite
│   └── criar_dados.py       # dados iniciais para teste
├── tests/
│   └── test_fluxo.py
├── postman/
│   └── Raizes_Backend_Postman_Collection.json
├── diagramas/
├── .env.example
├── requirements.txt
└── README.md
```

## Como rodar na máquina

git clone https://github.com/Juncaa/Raizes_do_Nordeste.git

Entre na pasta do projeto:


```bash
cd raizes_do_nordeste
```

Crie o ambiente virtual:

```bash
py -3.12 -m venv .venv
```

Ative o ambiente virtual:

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Crie o banco com dados de teste:

```bash
python -m app.criar_dados
```

Inicie a API:

```bash
uvicorn app.main:app --reload
```

## Documentação da API

Após iniciar a API, a documentação automática do FastAPI pode ser acessada pelo navegador:

```text
http://127.0.0.1:8000/docs
```

Nessa página é possível visualizar os endpoints disponíveis, consultar os contratos de entrada e saída da API e testar as requisições diretamente pelo Swagger/OpenAPI.

## Como rodar os testes

Antes de rodar os testes, garanta que as dependências foram instaladas e que o ambiente virtual está ativado.

Para executar os testes automatizados, use:

```bash
python -m pytest
```

Se tudo estiver correto, o terminal deve retornar algo parecido com:

```text
2 passed
```

Além dos testes automatizados, o projeto também possui uma coleção Postman para testar o fluxo principal da API. O arquivo está na pasta:

```text
postman/Raizes_Backend_Postman_Collection.json
```

A ordem recomendada para testar o fluxo principal no Postman é:

```text
1. Login do cliente
2. Listar unidades
3. Consultar cardápio da unidade
4. Criar pedido com canalPedido
5. Realizar pagamento mock
6. Consultar pedido atualizado
7. Atualizar status do pedido
8. Consultar auditoria
```

## Usuários de teste

| Perfil | E-mail | Senha |
|---|---|---|
| Cliente | cliente@exemplo.com | 123456 |
| Admin | admin@exemplo.com | 123456 |
| Cozinha | cozinha@exemplo.com | 123456 |
| Gerente | gerente@exemplo.com | 123456 |

O arquivo `.env.example` mostra as variáveis usadas pelo projeto. Para rodar localmente, os valores padrão já funcionam.

```env
APP_NAME=Raizes do Nordeste API
DATABASE_URL=sqlite:///./raizes.db
SECRET_KEY=troque-esta-chave-em-producao
ACCESS_TOKEN_EXPIRE_MINUTES=120
```
