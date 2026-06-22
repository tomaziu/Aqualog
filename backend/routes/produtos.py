import os
import uuid
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from database import get_connection
from models import Produto
from auth import get_admin_user
from sse_manager import notify
from logger import logger

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parent.parent / 'uploads' / 'produtos'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
MAX_SIZE = 5 * 1024 * 1024
OUTPUT_SIZE = (400, 400)


@router.get('/produtos')
def listar(page: int = Query(1, ge=1), per_page: int = Query(200, ge=1, le=500), admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT COUNT(*) total FROM produtos')
    total = cur.fetchone()['total']
    offset = (page - 1) * per_page
    cur.execute('''SELECT *,
                          CASE WHEN estoque <= estoque_minimo THEN 1 ELSE 0 END AS estoque_baixo
                   FROM produtos
                   ORDER BY ativo DESC, estoque_baixo DESC, id DESC
                   LIMIT %s OFFSET %s''', (per_page, offset))
    dados = cur.fetchall(); cur.close(); con.close()
    return {'success': True, 'data': dados, 'total': total, 'page': page, 'per_page': per_page}


@router.post('/produtos')
def criar(produto: Produto, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor()
    cur.execute('''INSERT INTO produtos (nome, preco, estoque, estoque_minimo, ativo)
                   VALUES (%s,%s,%s,%s,%s)''',
                (produto.nome, produto.preco, produto.estoque, produto.estoque_minimo, 1 if produto.ativo else 0))
    con.commit(); novo_id = cur.lastrowid; cur.close(); con.close()
    return {'success': True, 'data': {'id': novo_id, 'mensagem': 'Produto cadastrado'}}


@router.put('/produtos/{id}')
def editar(id: int, produto: Produto, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT estoque FROM produtos WHERE id=%s', (id,))
    atual = cur.fetchone()
    if not atual:
        cur.close(); con.close()
        raise HTTPException(404, 'Produto não encontrado')
    cur.execute('''UPDATE produtos
                   SET nome=%s, preco=%s, estoque=%s, estoque_minimo=%s, ativo=%s
                   WHERE id=%s''',
                (produto.nome, produto.preco, produto.estoque, produto.estoque_minimo, 1 if produto.ativo else 0, id))
    if int(atual.get('estoque') or 0) != int(produto.estoque):
        cur.execute('''INSERT INTO estoque_movimentacoes
                       (produto_id, pedido_id, tipo, quantidade, estoque_anterior, estoque_novo, observacao)
                       VALUES (%s, NULL, 'ajuste_manual', %s, %s, %s, 'Ajuste manual no cadastro de produto')''',
                    (id, int(produto.estoque) - int(atual.get('estoque') or 0), int(atual.get('estoque') or 0), int(produto.estoque)))
    con.commit(); cur.close(); con.close()
    return {'success': True, 'data': {'mensagem': 'Produto atualizado'}}


@router.delete('/produtos/{id}')
def excluir(id: int, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT id FROM produtos WHERE id=%s', (id,))
    if not cur.fetchone():
        cur.close(); con.close()
        raise HTTPException(404, 'Produto não encontrado')
    cur.execute('UPDATE produtos SET ativo=0 WHERE id=%s', (id,))
    con.commit(); cur.close(); con.close()
    return {'success': True, 'data': {'mensagem': 'Produto inativado'}}


@router.post('/produtos/{id}/imagem')
async def upload_imagem(id: int, file: UploadFile = File(...), admin=Depends(get_admin_user)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f'Tipo de arquivo não permitido. Use: JPG, PNG, WebP ou GIF')

    conteudo = await file.read()
    if len(conteudo) > MAX_SIZE:
        raise HTTPException(400, f'Arquivo muito grande. Tamanho máximo: 5MB')

    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        cur.execute('SELECT id, imagem FROM produtos WHERE id=%s', (id,))
        produto = cur.fetchone()
        if not produto:
            raise HTTPException(404, 'Produto não encontrado')

        if HAS_PIL:
            img = Image.open(BytesIO(conteudo))
            img_original = img.copy()
            original_ext = file.filename.rsplit('.', 1)[-1] if '.' in (file.filename or '') else 'png'
            original_nome = f'produto_{id}_original_{uuid.uuid4().hex[:8]}.{original_ext}'
            caminho_original = UPLOAD_DIR / original_nome
            img_original.save(caminho_original)

            img = img.convert('RGB')
            img.thumbnail(OUTPUT_SIZE, Image.LANCZOS)
            left = (img.width - min(img.width, OUTPUT_SIZE[0])) // 2
            top = (img.height - min(img.height, OUTPUT_SIZE[1])) // 2
            right = left + min(img.width, OUTPUT_SIZE[0])
            bottom = top + min(img.height, OUTPUT_SIZE[1])
            img = img.crop((left, top, right, bottom))
            buf = BytesIO()
            img.save(buf, format='WEBP', quality=85)
            conteudo = buf.getvalue()
            extensao = 'webp'
            content_type = 'image/webp'
        else:
            extensao = file.filename.rsplit('.', 1)[-1] if '.' in (file.filename or '') else 'png'
            content_type = file.content_type

        nome_arquivo = f'produto_{id}_{uuid.uuid4().hex[:8]}.{extensao}'
        caminho = UPLOAD_DIR / nome_arquivo

        if produto.get('imagem'):
            nome_antigo = Path(produto['imagem']).name
            caminho_antigo = UPLOAD_DIR / nome_antigo
            if caminho_antigo.exists():
                caminho_antigo.unlink(missing_ok=True)

        with open(caminho, 'wb') as f:
            f.write(conteudo)

        url_imagem = f'/uploads/produtos/{nome_arquivo}'
        cur.execute('UPDATE produtos SET imagem=%s WHERE id=%s', (url_imagem, id))
        con.commit()

        notify('refresh', {'acao': 'produto_imagem_atualizada', 'produto_id': id})

        return {'success': True, 'data': {'imagem': url_imagem, 'mensagem': 'Imagem atualizada'}}
    except HTTPException:
        con.rollback()
        raise
    except Exception as e:
        con.rollback()
        logger.exception(f"Erro no upload de imagem: {e}")
        raise HTTPException(500, 'Erro ao processar imagem')
    finally:
        cur.close(); con.close()


@router.delete('/produtos/{id}/imagem')
def remover_imagem(id: int, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        cur.execute('SELECT id, imagem FROM produtos WHERE id=%s', (id,))
        produto = cur.fetchone()
        if not produto:
            raise HTTPException(404, 'Produto não encontrado')

        if produto.get('imagem'):
            nome_arquivo = Path(produto['imagem']).name
            caminho = UPLOAD_DIR / nome_arquivo
            if caminho.exists():
                caminho.unlink(missing_ok=True)
            for orig in UPLOAD_DIR.glob(f'produto_{id}_original_*'):
                orig.unlink(missing_ok=True)

        cur.execute('UPDATE produtos SET imagem=NULL WHERE id=%s', (id,))
        con.commit()

        notify('refresh', {'acao': 'produto_imagem_atualizada', 'produto_id': id})

        return {'success': True, 'data': {'mensagem': 'Imagem removida'}}
    except HTTPException:
        con.rollback()
        raise
    finally:
        cur.close(); con.close()


@router.get('/produtos/{id}/imagem-original')
def obter_imagem_original(id: int, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        cur.execute('SELECT id FROM produtos WHERE id=%s', (id,))
        if not cur.fetchone():
            raise HTTPException(404, 'Produto não encontrado')

        originais = sorted(UPLOAD_DIR.glob(f'produto_{id}_original_*'), key=lambda f: f.stat().st_mtime, reverse=True)
        if not originais:
            raise HTTPException(404, 'Imagem original não encontrada')

        return {'success': True, 'data': {'url': f'/uploads/produtos/{originais[0].name}'}}
    finally:
        cur.close(); con.close()
