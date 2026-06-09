import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

SECRET_KEY = os.getenv('JWT_SECRET', 'aqualog-secret-key-change-in-production')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_HOURS = 24


def criar_token(data: dict) -> str:
    payload = data.copy()
    payload['exp'] = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verificar_senha(senha: str, hash_s: str) -> bool:
    return bcrypt.checkpw(senha.encode('utf-8'), hash_s.encode('utf-8'))


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(401, detail='Token de autenticação necessário')
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(401, detail='Token inválido ou expirado')


def get_admin_user(payload: dict = Depends(get_current_user)):
    if payload.get('tipo') != 'admin':
        raise HTTPException(403, detail='Acesso restrito ao admin')
    return payload


def get_entregador_user(payload: dict = Depends(get_current_user)):
    if payload.get('tipo') != 'entregador':
        raise HTTPException(403, detail='Acesso restrito a entregadores')
    return payload
