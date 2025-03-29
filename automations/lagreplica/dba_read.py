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

def enviar_email_com_anexo(arquivo, txt_files):
    sender_email = "xxxxxxxx" # Remetente
    receiver_email = ["xxxxx"] #Destinatario
    subject = f"Tempo de replicação acima do desejado - {datetime.datetime.now().strftime('%d-%m-%Y')}"
    body = "Segue os dados em anexo."

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "xxxxxxxxxxxx" # usuario
    smtp_password = "xxxxxxxxxxxx" # Google app password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(receiver_email)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, "plain"))

    with open(arquivo, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(arquivo)}")
        msg.attach(part)

    for txt_file in txt_files:
        with open(txt_file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(txt_file)}")
            msg.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"E-mail enviado com sucesso para {', '.join(receiver_email)}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

    os.remove(arquivo)
    
    for txt_file in txt_files:
        os.remove(txt_file)

config = apontamento('lagreplica/replica.ini')

origem_host = config.get('mysql_origem_db', 'host')
origem_database = config.get('mysql_origem_db', 'database')
origem_user = config.get('mysql_origem_db', 'user')
origem_password = config.get('mysql_origem_db', 'password')
origem_port = config.get('mysql_origem_db', 'port')

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
    print(f"Erro ao conectar ao banco de dados: {e}")
    exit()

cursor = origem_db.cursor(dictionary=True)

try:
    query_latency = """
        SELECT SUM(IF(is_io_thread, TIME, NULL))                                      AS Slave_Connected_time,
            SUM(is_io_thread) IS TRUE                                              AS Slave_IO_Running,
            SUM(is_sql_thread OR (is_system AND NOT is_io_thread)) IS TRUE         AS Slave_SQL_Running,
            (SUM(is_system) = 2) IS TRUE                                           AS Slave_Running,
            SUM(IF(is_sql_thread OR (is_system AND NOT is_io_thread), TIME, NULL)) AS Seconds_Behind_Master
        FROM (
                SELECT PROCESSLIST.*,
                        USER = 'system user'                                                     AS is_system,
                        (USER = 'system user' AND state_type = 'replication_io_thread') IS TRUE  AS is_io_thread,
                        (USER = 'system user' AND state_type = 'replication_sql_thread') IS TRUE AS is_sql_thread,
                        COMMAND = 'Binlog Dump'                                                  AS is_slave
                FROM INFORMATION_SCHEMA.PROCESSLIST
                        LEFT JOIN (
                    -- Replication SQL thread states
                    select 'Waiting for the next event in relay log' state, 'replication_sql_thread' state_type
                    union
                    select 'Reading event from the relay log' state, 'replication_sql_thread' state_type
                    union
                    select 'Making temp file' state, 'replication_sql_thread' state_type
                    union
                    select 'Slave has read all relay log; waiting for the slave I/O thread to update it' state, 'replication_sql_thread' state_type
                    union
                    select 'Waiting until MASTER_DELAY seconds after master executed event' state, 'replication_sql_thread' state_type
                    union
                    select 'Has read all relay log; waiting for the slave I/O thread to update it' state, 'replication_sql_thread' state_type
                    union
                    -- Replication I/O thread states
                    select 'Waiting for an event from Coordinator' state, 'replication_io_thread' state_type
                    union
                    select 'Waiting for master update' state, 'replication_io_thread' state_type
                    union
                    select 'Connecting to master ' state, 'replication_io_thread' state_type
                    union
                    select 'Checking master version' state, 'replication_io_thread' state_type
                    union
                    select 'Registering slave on master' state, 'replication_io_thread' state_type
                    union
                    select 'Requesting binlog dump' state, 'replication_io_thread' state_type
                    union
                    select 'Waiting to reconnect after a failed binlog dump request' state, 'replication_io_thread' state_type
                    union
                    select 'Reconnecting after a failed binlog dump request' state, 'replication_io_thread' state_type
                    union
                    select 'Waiting for master to send event' state, 'replication_io_thread' state_type
                    union
                    select 'Queueing master event to the relay log' state, 'replication_io_thread' state_type
                    union
                    select 'Waiting to reconnect after a failed master event read' state, 'replication_io_thread' state_type
                    union
                    select 'Reconnecting after a failed master event read' state, 'replication_io_thread' state_type
                    union
                    select 'Waiting for the slave SQL thread to free enough relay log space' state, 'replication_io_thread' state_type
                ) known_states ON (known_states.state LIKE CONCAT(PROCESSLIST.STATE, '%'))
                WHERE USER = 'system user'
                    OR COMMAND = 'Binlog Dump'
            ) common_schema_slave_status;
    """
    cursor.execute(query_latency)
    latency_result = cursor.fetchone()

    seconds_behind_master = latency_result.get('Seconds_Behind_Master') if latency_result else 0

    seconds_behind_master = seconds_behind_master if seconds_behind_master is not None else 0

    if seconds_behind_master <= 90:
        print(f"Replicação está dentro do limite. Seconds_Behind_Master: {seconds_behind_master}")
    else:
        print(f"Replicação atrasada. Seconds_Behind_Master: {seconds_behind_master}")    

        query = """
            SELECT 
                Id, 
                User, 
                Host,
                Command, 
                Time,
                State, 
                db, 
                Info,
                NOW() AS Data 
            FROM INFORMATION_SCHEMA.PROCESSLIST 
            WHERE 
                Command = 'Query' 
                AND Time > 420
                AND State = 'executing'
                AND user NOT IN ('rdsadmin', 'rdsrepladmin', 'system user', 'event_scheduler')
                AND (info IS NULL OR info NOT LIKE '%IGNORE_KILL_QUERY_ON_DATABASE_TIMEOUT%');
        """
        
        cursor.execute(query)
        results = cursor.fetchall()

        df = pd.DataFrame(results)

        if df.empty:
            print("Nenhuma linha retornada pela consulta. O e-mail não será enviado.")
        else:
            file_name = 'lagreplica/lag_replica.xlsx'
            
            txt_files = []
            
            for index, row in df.iterrows():
                if len(row['Info']) > 30000:
                    txt_file_name = f'lagreplica/info_longa_{row["Id"]}.txt'  
                    with open(txt_file_name, 'w', encoding='utf-8') as txt_file:
                        txt_file.write(row['Info'])
                    txt_files.append(txt_file_name) 
                    print(f"Arquivo {txt_file_name} gerado com conteúdo do campo 'Info'.")

            with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='ProcessList')

            print("Relatório Excel gerado com sucesso!")
            enviar_email_com_anexo(file_name, txt_files)

except mysql.connector.Error as e:
    print(f"Erro ao executar consulta SQL: {e}")

finally:
    cursor.close()
    origem_db.close()
