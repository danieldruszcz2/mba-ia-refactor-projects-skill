from datetime import datetime, timezone


def utc_now():
    """Instante atual em UTC como datetime naive.

    As colunas DateTime do SQLite não guardam fuso; normalizar aqui mantém o
    formato serializado (`str(datetime)`) e as comparações consistentes.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
