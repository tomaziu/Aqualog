import os
from fastapi import APIRouter, HTTPException
from models import AdminLogin
from auth import criar_token, hash_senha, verificar_senha

router = APIRouter()

ADMIN_PASSWORD_HASH = None


def get_admin_hash():
    global ADMIN_PASSWORD_HASH
    if ADMIN_PASSWORD_HASH is None:
        raw = os.getenv('ADMIN_PASSWORD', 'admin123')
        ADMIN_PASSWORD_HASH = hash_senha(raw)
    return ADMIN_PASSWORD_HASH


@router.post('/admin/login')
def admin_login(login: AdminLogin):
    if not verificar_senha(login.senha, get_admin_hash()):
        raise HTTPException(401, 'Senha incorreta')
    token = criar_token({'tipo': 'admin', 'nome': 'Administrador'})
    return {'access_token': token, 'tipo': 'admin', 'nome': 'Administrador'}
