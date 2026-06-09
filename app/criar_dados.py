from app.database import Base, SessionLocal, engine
from app.tabelas import Estoque, Unidade, Usuario, Produto
from app.login import gerar_hash_senha


def criar_dados_iniciais():
    # Cria dados para testes
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    banco = SessionLocal()

    usuarios = [
        Usuario(nome="Cliente Teste", email="cliente@exemplo.com",
                senha_hash=gerar_hash_senha("123456"), perfil="CLIENTE", aceita_fidelidade=True),
        Usuario(nome="Admin Teste", email="admin@exemplo.com",
                senha_hash=gerar_hash_senha("123456"), perfil="ADMIN", aceita_fidelidade=False),
        Usuario(nome="Cozinha Teste", email="cozinha@exemplo.com",
                senha_hash=gerar_hash_senha("123456"), perfil="COZINHA", aceita_fidelidade=False),
        Usuario(nome="Gerente Teste", email="gerente@exemplo.com",
                senha_hash=gerar_hash_senha("123456"), perfil="GERENTE", aceita_fidelidade=False),
    ]

    unidades = [
        Unidade(nome="Raízes Recife Centro", cidade="Recife",
                uf="PE", cozinha_completa=True),
        Unidade(nome="Raízes Fortaleza Compacta",
                cidade="Fortaleza", uf="CE", cozinha_completa=False),
    ]

    produtos = [
        Produto(nome="Tapioca de queijo coalho", descricao="Tapioca simples com queijo coalho.",
                preco=12.0, precisa_cozinha_completa=False, pontos_gerados=1),
        Produto(nome="Cuscuz recheado", descricao="Cuscuz com carne de sol e queijo.",
                preco=18.0, precisa_cozinha_completa=True, pontos_gerados=2),
        Produto(nome="Bolo de macaxeira", descricao="Fatia de bolo regional.",
                preco=8.0, precisa_cozinha_completa=False, pontos_gerados=1),
        Produto(nome="Suco de cajá", descricao="Suco regional gelado.",
                preco=9.0, precisa_cozinha_completa=False, pontos_gerados=1),
    ]

    banco.add_all(usuarios + unidades + produtos)
    banco.commit()

    estoques = [
        Estoque(unidade_id=1, produto_id=1, quantidade=50),
        Estoque(unidade_id=1, produto_id=2, quantidade=30),
        Estoque(unidade_id=1, produto_id=3, quantidade=40),
        Estoque(unidade_id=1, produto_id=4, quantidade=40),
        Estoque(unidade_id=2, produto_id=1, quantidade=25),
        Estoque(unidade_id=2, produto_id=2, quantidade=20),
        Estoque(unidade_id=2, produto_id=3, quantidade=20),
        Estoque(unidade_id=2, produto_id=4, quantidade=20),
    ]

    banco.add_all(estoques)
    banco.commit()
    banco.close()
    print("Banco recriado com dados de teste.")


if __name__ == "__main__":
    criar_dados_iniciais()
