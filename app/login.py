import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from app.database import pegar_banco
from app.tabelas import Usuario

SECRET_KEY = os.getenv("SECRET_KEY", "chave-local")
TOKEN_MINUTOS = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
ALGORITMO = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def gerar_hash_senha(senha: str) -> str:
    # Gera senha sem salvar o texto puro no banco.
    salt = "raizes_salt_academico"
    senha_bytes = senha.encode("utf-8")
    salt_bytes = salt.encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", senha_bytes, salt_bytes, 100000).hex()


def senha_confere(senha_digitada: str, senha_salva: str) -> bool:
    hash_digitado = gerar_hash_senha(senha_digitada)
    return hmac.compare_digest(hash_digitado, senha_salva)


def criar_token(usuario: Usuario) -> str:
    # Cria um token com id, e-mail e perfil do usuário.
    validade = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTOS)
    dados_token = {
        "sub": str(usuario.id),
        "email": usuario.email,
        "perfil": usuario.perfil,
        "exp": validade,
    }
    return jwt.encode(dados_token, SECRET_KEY, algorithm=ALGORITMO)


def usuario_atual(token: str = Depends(oauth2_scheme), banco: Session = Depends(pegar_banco)) -> Usuario:
    try:
        dados = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO])
        usuario_id = int(dados.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
        )

    usuario = banco.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=401, detail="Usuário do token não encontrado.")
    return usuario


def exigir_perfil(*perfis_liberados: str):
    # Realiza o bloqueio caso o usuário não tenha permissão.
    def verificar(usuario: Usuario = Depends(usuario_atual)) -> Usuario:
        if usuario.perfil not in perfis_liberados:
            raise HTTPException(
                status_code=403, detail="Usuário sem permissão para esta operação.")
        return usuario

    return verificar
