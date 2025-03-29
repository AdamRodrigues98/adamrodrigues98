import configparser
import os
import mysql.connector
from cryptography.fernet import Fernet

########################################################
# Codigo abaixo coleta os dados  #
# da replica, e insere em Dev    #
##################################

# Carrega a chave do ambiente
def load_key_from_env(env_var):
    key = os.getenv(env_var)
    if key is None:
        raise ValueError(f"Chave não encontrada na variável de ambiente: {env_var}")
    return key.encode()

projeto_ad = 'projeto_ad.ini'
key_env_var = 'CHAVE_projeto_ad'


def decrypt_config_file(input_file, key):
    cipher_suite = Fernet(key)
    with open(input_file, 'rb') as f:
        f.read(4) 
        encrypted_config_data = f.read()
    config_data = cipher_suite.decrypt(encrypted_config_data).decode()
    return config_data

current_dir = os.path.dirname(os.path.abspath(__file__))
projeto_ad_path = os.path.join(current_dir, projeto_ad)

key = load_key_from_env(key_env_var)
config_data = decrypt_config_file(projeto_ad_path, key)


if config_data is not None:
    config = configparser.ConfigParser()
    config.read_string(config_data)

origem_host = config['mysql_origem_db']['host']
origem_database = config['mysql_origem_db']['database']
origem_user = config['mysql_origem_db']['user']
origem_password = config['mysql_origem_db']['password']
origem_port = config['mysql_origem_db']['port']

destino_host = config['mysql_destino_db']['host']
destino_database = config['mysql_destino_db']['database']
destino_user = config['mysql_destino_db']['user']
destino_password = config['mysql_destino_db']['password']
destino_port = config['mysql_destino_db']['port']

origem_db = mysql.connector.connect(
    host=origem_host,
    user=origem_user,
    port=origem_port,
    password=origem_password,
    database=origem_database
)

destino_db = mysql.connector.connect(
    host=destino_host,
    user=destino_user,
    port=destino_port,
    password=destino_password,
    database=destino_database
)
cursor_origem = origem_db.cursor(dictionary=True)
cursor_destino = destino_db.cursor()

#Condições
cursor_destino.execute("SELECT COUNT(*) AS count FROM projeto_ad")
result = cursor_destino.fetchone()

if result:
    projeto_ad_count = result[0]

    if projeto_ad_count > 0:

        cursor_destino.execute(""" TRUNCATE TABLE projeto_ad """)

#Querys
cursor_origem = origem_db.cursor(dictionary=True)
query = "SELECT id FROM adam.customer WHERE contract_ad IS NOT NULL"

cursor_origem.execute(query)

ids_customers = cursor_origem.fetchall()


ids_string = ', '.join(str(id_dict['id']) for id_dict in ids_customers)


consulta = f"""WITH customer_count AS
                (
                    SELECT .....
                    WHERE per.customer_id IN ({ids_string})
                                        """
cursor_origem.execute(consulta)
resultados = cursor_origem.fetchall()

#Inserir na tabela destino
for linha in resultados:
      valores = tuple(linha.values())
      placeholders = ','.join(['%s'] * len(valores))
      consulta_insercao = f"INSERT INTO projeto_ad VALUES ({placeholders})"
      cursor_destino.execute(consulta_insercao, valores)
destino_db.commit()
  
cursor_origem.close()
cursor_destino.close()
origem_db.close()
destino_db.close()


