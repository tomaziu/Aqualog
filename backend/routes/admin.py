import os
from fastapi import APIRouter, HTTPException
from models import AdminLogin

router = APIRouter()


@router.post('/admin/login')
def admin_login(login: AdminLogin):
    if login.senha != os.getenv('ADMIN_PASSWORD', 'admin123'):
        raise HTTPException(401, 'Senha incorreta')
    return {'mensagem': 'OK'}
