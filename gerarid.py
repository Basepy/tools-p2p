
import string
import random




# Função para gerar código de TXID alfanuméricos
def gerar_identificador():
    caracteres02 = string.digits
    init = "STK"
    codigo_02 = ''.join(random.choices(caracteres02, k=10))
    id_codigo = f'{init}{codigo_02}'
    return id_codigo
