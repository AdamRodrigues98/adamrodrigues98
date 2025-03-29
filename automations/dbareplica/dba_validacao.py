import mysql.connector
from configparser import ConfigParser
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
import datetime

def apontamento(arquivo):
    parser = ConfigParser()
    parser.read(arquivo)
    return parser

config = apontamento('dbareplica/replica.ini')


origem_host = config.get('mysql_origem_db', 'host')
origem_database = config.get('mysql_origem_db', 'database')
origem_user = config.get('mysql_origem_db', 'user')
origem_password = config.get('mysql_origem_db', 'password')
origem_port = config.get('mysql_origem_db', 'port')

destino_host = config.get('mysql_destino_db', 'host')
destino_database = config.get('mysql_destino_db', 'database')
destino_user = config.get('mysql_destino_db', 'user')
destino_password = config.get('mysql_destino_db', 'password')
destino_port = config.get('mysql_destino_db', 'port')

try:
    origem_db = mysql.connector.connect(
        host=origem_host,
        user=origem_user,
        port=origem_port,
        password=origem_password,
        database=origem_database
    )

    if origem_db.is_connected():
        print("Conexão bem-sucedida ao banco de dados de origem.")
        
except mysql.connector.Error as e:
    print(f"Erro ao conectar ao banco de dados de origem: {e}")

try:
    destino_db = mysql.connector.connect(
        host=destino_host,
        user=destino_user,
        port=destino_port,
        password=destino_password,
        database=destino_database
    )

    if destino_db.is_connected():
        print("Conexão bem-sucedida ao banco de dados de destino.")
        
except mysql.connector.Error as e:
    print(f"Erro ao conectar ao banco de dados de destino: {e}")

cursor_origem = origem_db.cursor(dictionary=True)
cursor_destino = destino_db.cursor()

try:
    query_select = """
        SELECT 
            Id, 
            User, 
            Host,
            Command, 
            Time,
            State, 
            db, 
            Info
        FROM INFORMATION_SCHEMA.PROCESSLIST 
        WHERE 
            Command = 'Query' 
            AND Time > 1200
            AND State = 'executing'
            AND user NOT IN ('rdsadmin', 'rdsrepladmin', 'system user', 'event_scheduler')
            AND (info IS NULL OR info NOT LIKE '%IGNORE_KILL_QUERY_ON_DATABASE_TIMEOUT%');
    """
    cursor_origem.execute(query_select)
    results = cursor_origem.fetchall()  

    if results:
        print(f"{len(results)} registros encontrados na origem.")
        query_insert = """
            INSERT INTO dba.relatorio_queries (
                id_killed, 
                `USER`, 
                `Host`, 
                `Command`, 
                `Time`, 
                `State`, 
                `DB`, 
                `info`, 
                `created_at`
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW());
        """

        for row in results:
            cursor_destino.execute(query_insert, (
                row['Id'], 
                row['User'], 
                row['Host'], 
                row['Command'], 
                row['Time'], 
                row['State'], 
                row['db'], 
                row['Info']
            ))

        destino_db.commit() 
        print("Dados gravados no banco de destino com sucesso!")
    
    else:
        print("Nenhum dado encontrado para transferir.")

    query_kill = """
        SELECT CONCAT('CALL mysql.rds_kill(', Id, ');') AS kill_command
        FROM INFORMATION_SCHEMA.PROCESSLIST
        WHERE Command = 'Query' 
        AND Time > 1200
        AND State = 'executing'
        AND user NOT IN ('rdsadmin', 'rdsrepladmin', 'system user', 'event_scheduler', 'usr_analytics')
        AND (info IS NULL OR info NOT LIKE '%IGNORE_KILL_QUERY_ON_DATABASE_TIMEOUT%');
    """
    cursor_origem.execute(query_kill)
    kill_commands = cursor_origem.fetchall()

    for command in kill_commands:
        kill_command = command['kill_command'] 
        print(f"Executando: {kill_command}")
        cursor_origem.execute(kill_command)

    print("Comandos de KILL executados com sucesso!")

except mysql.connector.Error as e:
    print(f"Erro ao executar consulta SQL: {e}")

finally:
    cursor_origem.close()
    origem_db.close()
    cursor_destino.close()
    destino_db.close()
