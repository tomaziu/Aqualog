import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt

from routes.admin import router as admin_router
from routes.clientes import router as clientes_router
from routes.entregadores import router as entregadores_router
from routes.produtos import router as produtos_router
from routes.pedidos import router as pedidos_router
from routes.site import router as site_router
from routes.suporte import router as suporte_router
from routes.configuracoes import router as configuracoes_router
from routes.cupons import router as cupons_router
from routes.backup import router as backup_router
from routes.deliveries import router as deliveries_router
from delivery_realtime import init as delivery_rt_init
from sse_manager import init as sse_init, event_generator
from auth import SECRET_KEY, ALGORITHM
from logger import logger


@asynccontextmanager
async def lifespan(app):
    logger.info("Starting ÁquaLog API")
    loop = asyncio.get_running_loop()
    sse_init(loop)
    delivery_rt_init(loop)
    logger.info("SSE manager initialized")
    yield
    logger.info("Shutting down ÁquaLog API")


app = FastAPI(title='ÁquaLog API', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={'success': False, 'error': 'Erro interno do servidor'},
    )


API_PREFIX = '/api/v1'

app.include_router(admin_router, prefix=API_PREFIX)
app.include_router(clientes_router, prefix=API_PREFIX)
app.include_router(entregadores_router, prefix=API_PREFIX)
app.include_router(produtos_router, prefix=API_PREFIX)
app.include_router(pedidos_router, prefix=API_PREFIX)
app.include_router(site_router, prefix=API_PREFIX)
app.include_router(suporte_router, prefix=API_PREFIX)
app.include_router(configuracoes_router, prefix=API_PREFIX)
app.include_router(cupons_router, prefix=API_PREFIX)
app.include_router(backup_router, prefix=API_PREFIX)
app.include_router(deliveries_router, prefix=API_PREFIX)


@app.get(API_PREFIX + '/health')
def health():
    return {'status': 'ok', 'versao': '1.0.0'}


@app.get(API_PREFIX + '/events')
async def sse_events(token: str = Query(None)):
    if not token:
        raise HTTPException(401, detail='Token necessário')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('tipo') != 'admin':
            raise HTTPException(403, detail='Acesso restrito')
    except JWTError:
        raise HTTPException(401, detail='Token inválido')

    return StreamingResponse(
        event_generator(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        },
    )


frontend_dir = str(Path(__file__).resolve().parent.parent / 'frontend')
uploads_dir = str(Path(__file__).resolve().parent / 'uploads')
app.mount('/uploads', StaticFiles(directory=uploads_dir), name='uploads')
app.mount('/', StaticFiles(directory=frontend_dir, html=True))

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', '8000'))
    uvicorn.run('main:app', host='0.0.0.0', port=port)
