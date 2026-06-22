import json
from datetime import datetime
from decimal import Decimal
from math import asin, cos, radians, sin, sqrt
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from auth import ALGORITHM, SECRET_KEY, get_admin_user, get_entregador_user
from database import get_connection
from delivery_realtime import connect, disconnect, notify_delivery
from models import ClientLocationUpdate, DeliveryAssignDriver, DeliveryCreate, DeliveryCreateFromPedido, DeliveryLocationUpdate, DeliveryStatusUpdate
from sse_manager import notify as notify_sse

router = APIRouter()

DELIVERY_STATUSES = {
    'aguardando_coleta',
    'coletado',
    'em_rota',
    'proximo_destino',
    'entregue',
    'cancelado',
}

ACTIVE_STATUSES = ('aguardando_coleta', 'coletado', 'em_rota', 'proximo_destino')


def serializar(valor):
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, datetime):
        return valor.isoformat()
    return valor


def serializar_row(row):
    return {k: serializar(v) for k, v in row.items()}


def haversine_meters(lat1, lon1, lat2, lon2):
    radius = 6371000
    dlat = radians(float(lat2) - float(lat1))
    dlon = radians(float(lon2) - float(lon1))
    a = sin(dlat / 2) ** 2 + cos(radians(float(lat1))) * cos(radians(float(lat2))) * sin(dlon / 2) ** 2
    return int(2 * radius * asin(sqrt(a)))


def estimar_eta(distance_meters):
    # Velocidade conservadora para entregas urbanas: 20 km/h.
    return int((distance_meters / 5.55) if distance_meters else 0)


def geocodificar_endereco(endereco):
    query = endereco.strip()
    if 'brasil' not in query.lower() and 'brazil' not in query.lower():
        query += ', Brasil'
    url = 'https://nominatim.openstreetmap.org/search?' + urlencode({
        'q': query,
        'format': 'json',
        'limit': 1,
        'addressdetails': 0,
    })
    req = Request(url, headers={'User-Agent': 'AquaLog/1.0 delivery tracking'})
    try:
        with urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception:
        raise HTTPException(502, 'Não foi possível localizar o endereço do cliente no mapa agora.')
    if not data:
        raise HTTPException(400, 'Não encontramos coordenadas para o endereço do cliente. Confira o endereço cadastrado.')
    return float(data[0]['lat']), float(data[0]['lon'])


def buscar_entrega(cur, delivery_id):
    cur.execute(
        '''
        SELECT d.*, c.nome AS cliente_nome, c.telefone AS cliente_telefone,
               e.nome AS entregador_nome, e.telefone AS entregador_telefone, e.veiculo AS entregador_veiculo,
               dl.latitude AS entregador_latitude, dl.longitude AS entregador_longitude,
               dl.accuracy AS entregador_accuracy, dl.created_at AS ultima_localizacao
        FROM deliveries d
        JOIN clientes c ON c.id = d.cliente_id
        LEFT JOIN entregadores e ON e.id = d.entregador_id
        LEFT JOIN delivery_locations dl ON dl.id = (
            SELECT id FROM delivery_locations WHERE delivery_id = d.id ORDER BY created_at DESC, id DESC LIMIT 1
        )
        WHERE d.id = %s
        ''',
        (delivery_id,),
    )
    row = cur.fetchone()
    return serializar_row(row) if row else None


def registrar_historico(cur, delivery_id, antigo, novo, actor_type, actor_id, note=''):
    cur.execute(
        '''
        INSERT INTO delivery_status_history
        (delivery_id, status_old, status_new, actor_type, actor_id, note)
        VALUES (%s,%s,%s,%s,%s,%s)
        ''',
        (delivery_id, antigo, novo, actor_type, actor_id, note or ''),
    )


def publicar_entrega(cur, delivery_id, evento='delivery_update'):
    entrega = buscar_entrega(cur, delivery_id)
    if entrega:
        payload = {'acao': evento, 'delivery': entrega, 'delivery_id': delivery_id}
        notify_sse('delivery_update', payload)
        notify_delivery(delivery_id, payload)
    return entrega


def validar_status(status):
    if status not in DELIVERY_STATUSES:
        raise HTTPException(400, 'Status de entrega inválido')


@router.get('/deliveries')
def listar_entregas(status: str = Query(None), q: str = Query(None), admin=Depends(get_admin_user)):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        sql = '''
            SELECT d.*, c.nome AS cliente_nome, e.nome AS entregador_nome, e.veiculo AS entregador_veiculo,
                   dl.latitude AS entregador_latitude, dl.longitude AS entregador_longitude,
                   dl.accuracy AS entregador_accuracy, dl.created_at AS ultima_localizacao
            FROM deliveries d
            JOIN clientes c ON c.id = d.cliente_id
            LEFT JOIN entregadores e ON e.id = d.entregador_id
            LEFT JOIN delivery_locations dl ON dl.id = (
                SELECT id FROM delivery_locations WHERE delivery_id = d.id ORDER BY created_at DESC, id DESC LIMIT 1
            )
            WHERE 1=1
        '''
        params = []
        if status:
            validar_status(status)
            sql += ' AND d.status = %s'
            params.append(status)
        if q:
            like = '%' + q + '%'
            sql += ' AND (c.nome LIKE %s OR e.nome LIKE %s OR d.destino_endereco LIKE %s OR d.id = %s)'
            params.extend([like, like, like, q if q.isdigit() else 0])
        sql += ' ORDER BY FIELD(d.status, "em_rota", "proximo_destino", "coletado", "aguardando_coleta", "entregue", "cancelado"), d.updated_at DESC'
        cur.execute(sql, params)
        return {'success': True, 'data': [serializar_row(row) for row in cur.fetchall()]}
    finally:
        cur.close()
        con.close()


@router.post('/deliveries')
def criar_entrega(entrega: DeliveryCreate, admin=Depends(get_admin_user)):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute('SELECT id FROM clientes WHERE id=%s', (entrega.cliente_id,))
        if not cur.fetchone():
            raise HTTPException(404, 'Cliente não encontrado')
        if entrega.entregador_id:
            cur.execute('SELECT id FROM entregadores WHERE id=%s', (entrega.entregador_id,))
            if not cur.fetchone():
                raise HTTPException(404, 'Entregador não encontrado')
        if entrega.pedido_id:
            cur.execute('SELECT id FROM pedidos WHERE id=%s', (entrega.pedido_id,))
            if not cur.fetchone():
                raise HTTPException(404, 'Pedido não encontrado')

        cur.execute(
            '''
            INSERT INTO deliveries
            (pedido_id, cliente_id, entregador_id, origem_endereco, origem_latitude, origem_longitude,
             destino_endereco, destino_latitude, destino_longitude, status, observacoes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'aguardando_coleta',%s)
            ''',
            (
                entrega.pedido_id,
                entrega.cliente_id,
                entrega.entregador_id,
                entrega.origem_endereco,
                entrega.origem_latitude,
                entrega.origem_longitude,
                entrega.destino_endereco,
                entrega.destino_latitude,
                entrega.destino_longitude,
                entrega.observacoes or '',
            ),
        )
        delivery_id = cur.lastrowid
        registrar_historico(cur, delivery_id, None, 'aguardando_coleta', 'admin', admin.get('id'), 'Entrega criada')
        con.commit()
        entrega_criada = publicar_entrega(cur, delivery_id, 'delivery_created')
        return {'success': True, 'data': entrega_criada}
    finally:
        cur.close()
        con.close()


@router.post('/deliveries/from-pedido')
def criar_entrega_por_pedido(dados: DeliveryCreateFromPedido, admin=Depends(get_admin_user)):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute(
            '''
            SELECT p.id, p.cliente_id, p.entregador_id, p.status,
                   c.nome AS cliente_nome, c.endereco, c.numero_casa, c.bairro, c.referencia,
                   c.latitude AS cliente_latitude, c.longitude AS cliente_longitude
            FROM pedidos p
            JOIN clientes c ON c.id = p.cliente_id
            WHERE p.id=%s
            ''',
            (dados.pedido_id,),
        )
        pedido = cur.fetchone()
        if not pedido:
            raise HTTPException(404, 'Pedido não encontrado')
        if pedido['status'] in ('entregue', 'cancelado'):
            raise HTTPException(400, 'Não é possível criar rastreamento para pedido finalizado')
        entregador_id = dados.entregador_id or pedido.get('entregador_id')
        if not entregador_id:
            raise HTTPException(400, 'Selecione um entregador para iniciar o rastreamento')
        cur.execute('SELECT id FROM entregadores WHERE id=%s', (entregador_id,))
        if not cur.fetchone():
            raise HTTPException(404, 'Entregador não encontrado')
        cur.execute('SELECT id FROM deliveries WHERE pedido_id=%s AND status NOT IN ("entregue","cancelado") LIMIT 1', (dados.pedido_id,))
        existente = cur.fetchone()
        if existente:
            entrega = buscar_entrega(cur, existente['id'])
            return {'success': True, 'data': entrega}

        destino = ', '.join([str(x) for x in [pedido.get('endereco'), pedido.get('numero_casa'), pedido.get('bairro')] if x])
        if pedido.get('cliente_latitude') is not None and pedido.get('cliente_longitude') is not None:
            destino_lat = float(pedido['cliente_latitude'])
            destino_lng = float(pedido['cliente_longitude'])
        else:
            destino_lat, destino_lng = geocodificar_endereco(destino)
        cur.execute(
            '''
            INSERT INTO deliveries
            (pedido_id, cliente_id, entregador_id, origem_endereco, origem_latitude, origem_longitude,
             destino_endereco, destino_latitude, destino_longitude, status, observacoes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'aguardando_coleta',%s)
            ''',
            (
                pedido['id'],
                pedido['cliente_id'],
                entregador_id,
                dados.origem_endereco,
                dados.origem_latitude,
                dados.origem_longitude,
                destino,
                destino_lat,
                destino_lng,
                'Criado automaticamente a partir do pedido',
            ),
        )
        delivery_id = cur.lastrowid
        registrar_historico(cur, delivery_id, None, 'aguardando_coleta', 'admin', admin.get('id'), 'Entrega criada automaticamente')
        con.commit()
        entrega = publicar_entrega(cur, delivery_id, 'delivery_created')
        return {'success': True, 'data': entrega}
    finally:
        cur.close()
        con.close()


@router.get('/driver/deliveries/active')
def entregas_ativas_entregador(user=Depends(get_entregador_user)):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute(
            '''
            SELECT * FROM deliveries
            WHERE entregador_id=%s AND status IN ('aguardando_coleta','coletado','em_rota','proximo_destino')
            ORDER BY updated_at DESC
            ''',
            (user.get('id'),),
        )
        return {'success': True, 'data': [serializar_row(row) for row in cur.fetchall()]}
    finally:
        cur.close()
        con.close()


@router.get('/deliveries/{delivery_id}')
def obter_entrega(delivery_id: int, admin=Depends(get_admin_user)):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        entrega = buscar_entrega(cur, delivery_id)
        if not entrega:
            raise HTTPException(404, 'Entrega não encontrada')
        return {'success': True, 'data': entrega}
    finally:
        cur.close()
        con.close()


@router.get('/site/deliveries/{delivery_id}')
def obter_entrega_cliente(delivery_id: int, telefone: str = Query(...)):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        entrega = buscar_entrega(cur, delivery_id)
        if not entrega:
            raise HTTPException(404, 'Entrega não encontrada')
        digits_request = ''.join(ch for ch in telefone if ch.isdigit())
        digits_cliente = ''.join(ch for ch in (entrega.get('cliente_telefone') or '') if ch.isdigit())
        if not digits_request or not digits_cliente.endswith(digits_request[-8:]):
            raise HTTPException(403, 'Entrega não autorizada para este telefone')
        return {'success': True, 'data': entrega}
    finally:
        cur.close()
        con.close()


@router.post('/site/deliveries/{delivery_id}/client-location')
def enviar_localizacao_cliente(delivery_id: int, dados: ClientLocationUpdate, telefone: str = Query(...)):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        entrega = buscar_entrega(cur, delivery_id)
        if not entrega:
            raise HTTPException(404, 'Entrega não encontrada')
        digits_request = ''.join(ch for ch in telefone if ch.isdigit())
        digits_cliente = ''.join(ch for ch in (entrega.get('cliente_telefone') or '') if ch.isdigit())
        if not digits_request or not digits_cliente.endswith(digits_request[-8:]):
            raise HTTPException(403, 'Entrega não autorizada para este telefone')

        cur.execute('''UPDATE deliveries
                       SET cliente_atual_latitude=%s, cliente_atual_longitude=%s, cliente_atual_accuracy=%s, updated_at=NOW()
                       WHERE id=%s''',
                    (dados.latitude, dados.longitude, dados.accuracy, delivery_id))
        con.commit()
        publicar_entrega(cur, delivery_id, 'client_location_updated')
        return {'success': True}
    finally:
        cur.close()
        con.close()


@router.patch('/deliveries/{delivery_id}/driver')
def associar_entregador(delivery_id: int, dados: DeliveryAssignDriver, admin=Depends(get_admin_user)):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute('SELECT id FROM entregadores WHERE id=%s', (dados.entregador_id,))
        if not cur.fetchone():
            raise HTTPException(404, 'Entregador não encontrado')
        cur.execute('UPDATE deliveries SET entregador_id=%s, updated_at=NOW() WHERE id=%s', (dados.entregador_id, delivery_id))
        if cur.rowcount == 0:
            raise HTTPException(404, 'Entrega não encontrada')
        con.commit()
        return {'success': True, 'data': publicar_entrega(cur, delivery_id, 'driver_assigned')}
    finally:
        cur.close()
        con.close()


@router.patch('/deliveries/{delivery_id}/status')
def atualizar_status(delivery_id: int, dados: DeliveryStatusUpdate, admin=Depends(get_admin_user)):
    validar_status(dados.status)
    return _atualizar_status_entrega(delivery_id, dados.status, 'admin', admin.get('id'), dados.observacao)


@router.patch('/deliveries/{delivery_id}/status/driver')
def atualizar_status_entregador(delivery_id: int, dados: DeliveryStatusUpdate, user=Depends(get_entregador_user)):
    validar_status(dados.status)
    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute('SELECT entregador_id FROM deliveries WHERE id=%s', (delivery_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, 'Entrega não encontrada')
        if row['entregador_id'] != user.get('id'):
            raise HTTPException(403, 'Você só pode atualizar suas próprias entregas')
    finally:
        cur.close()
        con.close()
    return _atualizar_status_entrega(delivery_id, dados.status, 'entregador', user.get('id'), dados.observacao)


def _atualizar_status_entrega(delivery_id, status, actor_type, actor_id, observacao=''):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute('SELECT status FROM deliveries WHERE id=%s', (delivery_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, 'Entrega não encontrada')
        antigo = row['status']
        campos_tempo = {
            'coletado': ', collected_at=COALESCE(collected_at, NOW())',
            'em_rota': ', started_at=COALESCE(started_at, NOW())',
            'entregue': ', delivered_at=COALESCE(delivered_at, NOW())',
            'cancelado': ', canceled_at=COALESCE(canceled_at, NOW())',
        }
        sql = 'UPDATE deliveries SET status=%s, updated_at=NOW()' + campos_tempo.get(status, '') + ' WHERE id=%s'
        cur.execute(sql, (status, delivery_id))
        registrar_historico(cur, delivery_id, antigo, status, actor_type, actor_id, observacao)
        con.commit()
        return {'success': True, 'data': publicar_entrega(cur, delivery_id, 'status_changed')}
    finally:
        cur.close()
        con.close()


@router.get('/deliveries/{delivery_id}/locations')
def historico_localizacao(delivery_id: int, admin=Depends(get_admin_user)):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute(
            '''
            SELECT id, delivery_id, entregador_id, latitude, longitude, accuracy, heading, speed, source, created_at
            FROM delivery_locations
            WHERE delivery_id=%s
            ORDER BY created_at DESC, id DESC
            LIMIT 500
            ''',
            (delivery_id,),
        )
        return {'success': True, 'data': [serializar_row(row) for row in cur.fetchall()]}
    finally:
        cur.close()
        con.close()


@router.post('/deliveries/driver/location')
def enviar_localizacao(dados: DeliveryLocationUpdate, user=Depends(get_entregador_user)):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        params = [user.get('id')]
        sql = '''
            SELECT * FROM deliveries
            WHERE entregador_id=%s
              AND status IN ('aguardando_coleta','coletado','em_rota','proximo_destino')
        '''
        if dados.delivery_id:
            sql += ' AND id=%s'
            params.append(dados.delivery_id)
        elif dados.pedido_id:
            sql += ' AND pedido_id=%s'
            params.append(dados.pedido_id)
        sql += ' ORDER BY updated_at DESC LIMIT 1'
        cur.execute(sql, params)
        entrega = cur.fetchone()
        if not entrega:
            raise HTTPException(404, 'Nenhuma entrega ativa encontrada para este entregador')

        distance = haversine_meters(dados.latitude, dados.longitude, entrega['destino_latitude'], entrega['destino_longitude'])
        eta = estimar_eta(distance)
        novo_status = entrega['status']
        if entrega['status'] in ('coletado', 'em_rota') and distance <= 350:
            novo_status = 'proximo_destino'
        elif entrega['status'] in ('aguardando_coleta', 'coletado'):
            novo_status = 'em_rota'

        cur.execute(
            '''
            INSERT INTO delivery_locations
            (delivery_id, entregador_id, latitude, longitude, accuracy, heading, speed, source)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ''',
            (
                entrega['id'],
                user.get('id'),
                dados.latitude,
                dados.longitude,
                dados.accuracy,
                dados.heading,
                dados.speed,
                dados.source or 'browser',
            ),
        )
        cur.execute(
            '''
            UPDATE deliveries
            SET distance_meters=%s, eta_seconds=%s, status=%s, started_at=COALESCE(started_at, NOW()), updated_at=NOW()
            WHERE id=%s
            ''',
            (distance, eta, novo_status, entrega['id']),
        )
        if novo_status != entrega['status']:
            registrar_historico(cur, entrega['id'], entrega['status'], novo_status, 'entregador', user.get('id'), 'Atualizado por localização')
        con.commit()
        return {'success': True, 'data': publicar_entrega(cur, entrega['id'], 'location_updated')}
    finally:
        cur.close()
        con.close()


@router.websocket('/deliveries/ws/{delivery_id}')
async def websocket_entrega(websocket: WebSocket, delivery_id: int, token: str = Query(None), telefone: str = Query(None)):
    if not await _websocket_autorizado(delivery_id, token, telefone):
        await websocket.close(code=1008)
        return
    await connect(delivery_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        disconnect(delivery_id, websocket)


async def _websocket_autorizado(delivery_id: int, token: str = None, telefone: str = None):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        entrega = buscar_entrega(cur, delivery_id)
        if not entrega:
            return False
        if token:
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                if payload.get('tipo') == 'admin':
                    return True
                if payload.get('tipo') == 'entregador' and payload.get('id') == entrega.get('entregador_id'):
                    return True
            except JWTError:
                return False
        if telefone:
            req = ''.join(ch for ch in telefone if ch.isdigit())
            cli = ''.join(ch for ch in (entrega.get('cliente_telefone') or '') if ch.isdigit())
            return bool(req and cli.endswith(req[-8:]))
        return False
    finally:
        cur.close()
        con.close()
