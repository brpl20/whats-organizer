from re import sub

def sanitize_path(path: str) -> str:
    '''
    uma função para sanitizar comandos. é uma função básica, que não
    garante nenhuma segurança absoluta (ataques com encoding diferente
    ainda poderiam funcionar), mas ela deve diminuir o risco de ataques,
    por exemplo, lfi (usando ../../../)
    '''
    # remove nullbytes pra previnir bypass ex.: .%00./.%00./
    if '\x00' in path:
        path=''.join(path.split('\x00'))
    path = sub(r'\.\.', '', path)
    return path