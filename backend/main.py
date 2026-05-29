import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes.admin import router as admin_router
from routes.clientes import router as clientes_router
from routes.entregadores import router as entregadores_router
from routes.produtos import router as produtos_router
from routes.pedidos import router as pedidos_router

app = FastAPI(title='ÁquaLog API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(admin_router)
app.include_router(clientes_router)
app.include_router(entregadores_router)
app.include_router(produtos_router)
app.include_router(pedidos_router)

frontend_dir = str(Path(__file__).resolve().parent.parent / 'frontend')
app.mount('/', StaticFiles(directory=frontend_dir, html=True))

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', '8000'))
    uvicorn.run('main:app', host='0.0.0.0', port=port)
