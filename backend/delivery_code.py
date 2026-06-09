import secrets


def gerar_codigo_entrega() -> str:
    return f'{secrets.randbelow(900000) + 100000}'
