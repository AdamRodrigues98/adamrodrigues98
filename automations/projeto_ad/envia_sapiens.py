import pymysql
import os
from zeep import Client
from datetime import datetime, timedelta
import configparser
from cryptography.fernet import Fernet

###########################################################
# Codigo abaixo pega os dados de duas tabelas, projeto_ad # 
# e projeto_ad_ad, realiza o envio para o WebService #
########################################################### 



def load_key_from_env(env_var):
    key = os.getenv(env_var)
    if key is None:
        raise ValueError(f"Chave não encontrada na variável de ambiente: {env_var}")
    return key.encode()

ad_mysql = 'ad_mysql.ini'
key_env_var = 'CHAVE_ad'

def decrypt_config_file(input_file, key):
    cipher_suite = Fernet(key)
    with open(input_file, 'rb') as f:
        f.read(4) 
        encrypted_config_data = f.read()
    config_data = cipher_suite.decrypt(encrypted_config_data).decode()
    return config_data


current_dir = os.path.dirname(os.path.abspath(__file__))
ad_mysql_path = os.path.join(current_dir, ad_mysql)


key = load_key_from_env(key_env_var)
config_data = decrypt_config_file(ad_mysql_path, key)

if config_data is not None:
    config = configparser.ConfigParser()
    config.read_string(config_data)

destino_host = config['mysql_destino_db']['host']
destino_database = config['mysql_destino_db']['database']
destino_user = config['mysql_destino_db']['user']
destino_password = config['mysql_destino_db']['password']


conexao = pymysql.connect(
    host= destino_host,
    user= destino_user,
    password= destino_password,
    database= destino_database
)

cursor = conexao.cursor(pymysql.cursors.DictCursor)

cursor.execute("SELECT COUNT(*) AS count FROM projeto_ad")
projeto_ad_count = cursor.fetchone()['count']

cursor.execute("SELECT COUNT(*) AS count FROM projeto_ad_ad")
projeto_ad_ad_count = cursor.fetchone()['count']

if projeto_ad_count > 0 and projeto_ad_ad_count > 0:
        cursor.execute("""
        SELECT 
        usu....""") # Aqui é onde pega os valores do campo para ser enviados no webserver
dados_tabela = cursor.fetchall()

url = 'http://' #informar a url do webservice


client = Client(url)

for linha in dados_tabela: # Aqui os dados que estão no banco serão informados de acordo com os campos do webserver, caso o campo tenha um valor padrão só informar o valor não há necessidade de pegar no banco
    dados = {
        'user': ' ', #informar o usuario
        'password': ' ', #informar a senha
        'encryption': '',
        'parameters': {
            'contratosEntrada': {
                'itens': {
                    'Sub': '+',
                    'codiho': '190',
                    'ACplCvs': linha['usu_cplcvs'],
                    'AObsCms': 'Lançamento de projeto_ad',
                    'tipo': 'S'
                },
                'NCodEmp': '0',
                'NCodFil': '1',
                'Ctr': linha['numctr'],
                'Nvalor': linha['n_valor']
            },
            'flowInstanceID': '',
            'flowName': 'Processamento projeto_ad'
        }
    }


    response = client.service.InserirMovimentacao(**dados)


else:
    pass  

cursor.close()
conexao.close()
