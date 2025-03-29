import os
import mysql.connector
import pymssql
import configparser
from cryptography.fernet import Fernet

############################################################
# Codigo abaixo pega os dados do SQL Server web_server1 e  #
# popula a tabela projeto_ad_web_server1                   #
############################################################

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


#Conexão com o BD
origem_host = config['sqlserver_origem_db']['host']
origem_database = config['sqlserver_origem_db']['database']
origem_user = config['sqlserver_origem_db']['user']
origem_password = config['sqlserver_origem_db']['password']


server = origem_host
database = origem_database
username = origem_user
password = origem_password


conn = pymssql.connect(server=server, user=username, password=password, database=database)

#Query SQL Server
cursor = conn.cursor()


query = """
  SELECT 
    ....
    ;
"""

cursor.execute(query)



destino_host = config['mysql_destino_db']['host']
destino_database = config['mysql_destino_db']['database']
destino_user = config['mysql_destino_db']['user']
destino_password = config['mysql_destino_db']['password']
destino_port = config['mysql_destino_db']['port']

mysql_conn = mysql.connector.connect(
    host= destino_host,
    user= destino_user,
    password= destino_password,
    database= destino_database,
    port= destino_port
)

#Condições
mysql_cursor = mysql_conn.cursor()

mysql_cursor.execute("SELECT COUNT(*) AS count FROM projeto_ad_web_server1")
result = mysql_cursor.fetchone()

if result:
    web_server1_count = result[0]

    if web_server1_count > 0:

        mysql_cursor.execute(""" TRUNCATE TABLE projeto_ad_web_server1 """)

#Inserção
batch_size = 1000  
batch = []
for row in cursor.fetchall():
    batch.append(row)
    if len(batch) >= batch_size:
        mysql_cursor.executemany("""
            INSERT INTO projeto_ad_web_server1 (....)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, batch)
        batch = []

if batch:
    mysql_cursor.executemany("""
            INSERT INTO projeto_ad_web_server1 (...)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """, batch)


mysql_conn.commit()
conn.close()
mysql_conn.close()
