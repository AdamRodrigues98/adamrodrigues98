import pymysql
import os
from datetime import datetime, timedelta
import configparser
from cryptography.fernet import Fernet

##########################################################
# Salvar dados para historico e relatorios caso precise. # 
########################################################## 

def load_key_from_env(env_var):
    key = os.getenv(env_var)
    if key is None:
        raise ValueError(f"Chave não encontrada na variável de ambiente: {env_var}")
    return key.encode()

web_server1_mysql = 'web_server1_mysql.ini'
key_env_var = 'CHAVE_web_server1'

def decrypt_config_file(input_file, key):
    cipher_suite = Fernet(key)
    with open(input_file, 'rb') as f:
        f.read(4) 
        encrypted_config_data = f.read()
    config_data = cipher_suite.decrypt(encrypted_config_data).decode()
    return config_data


current_dir = os.path.dirname(os.path.abspath(__file__))
web_server1_mysql_path = os.path.join(current_dir, web_server1_mysql)


key = load_key_from_env(key_env_var)
config_data = decrypt_config_file(web_server1_mysql_path, key)

if config_data is not None:
    config = configparser.ConfigParser()
    config.read_string(config_data)

#Conexão com o DB
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

#Condições
cursor = conexao.cursor(pymysql.cursors.DictCursor)

cursor.execute("SELECT COUNT(*) AS count FROM projeto_ad")
projeto_ad_count = cursor.fetchone()['count']

cursor.execute("SELECT COUNT(*) AS count FROM projeto_ad_web_server1")
projeto_ad_web_server1_count = cursor.fetchone()['count']

#Inserir nas tabelas para ter um historico
if projeto_ad_count > 0 and projeto_ad_web_server1_count > 0:

    cursor.execute("""
INSERT INTO projeto_ad_web_server1_hist (
 ....
                   """)

    cursor.execute("""INSERT INTO projeto_ad_hist (cod_cliente, qtd, contract_web_server1, date_insert)
                   SELECT cod_cliente, qtd, contract_web_server1, date_insert FROM projeto_ad; """)
    
    cursor.execute(""" INSERT INTO projeto_ad_relatorio
                        ....
                   """)

    cursor.execute(""" TRUNCATE TABLE projeto_ad """)

    cursor.execute(""" TRUNCATE TABLE projeto_ad_web_server1 """)

    conexao.commit()
else:
    pass    

conexao.close()