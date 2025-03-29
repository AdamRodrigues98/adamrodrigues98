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
    sender_email = "xxxxx" #Remetente do MySQL
    receiver_email = ["XXXXX"] #destinatario
    subject = f"Querys Travadas na Read - {datetime.datetime.now().strftime('%d-%m-%Y')}"
    body = "Segue os dados em anexo."

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "xxxxx" #usuario
    smtp_password = "xxxxxxxxxxxx"  #app password 

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


config = apontamento('dbareplica/replica.ini')

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

cursor = origem_db.cursor(dictionary=True)

try:
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
            AND Time > 1200
            AND State = 'executing'
            AND user NOT IN ('rdsadmin', 'rdsrepladmin', 'system user', 'event_scheduler');
    """
    
    cursor.execute(query)
    results = cursor.fetchall()

    df = pd.DataFrame(results)

    if df.empty:
        print("Nenhuma linha retornada pela consulta. O e-mail não será enviado.")
    else:
        file_name = 'dbareplica/relatorio_replica.xlsx'
        
        txt_files = []
        
        for index, row in df.iterrows():
            if len(row['Info']) > 30000:
                txt_file_name = f'dbareplica/info_longa_{row["Id"]}.txt'  
                with open(txt_file_name, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(row['Info'])
                txt_files.append(txt_file_name) 
                print(f"Arquivo {txt_file_name} gerado com conteúdo do campo 'Info'.")

        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='ProcessList')
            
            worksheet = writer.sheets['ProcessList']
            for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row):
                for cell in row:
                    worksheet.row_dimensions[cell.row].height = 15 

        print("Relatório Excel gerado com sucesso!")
        
        enviar_email_com_anexo(file_name, txt_files)

except mysql.connector.Error as e:
    print(f"Erro ao executar consulta SQL: {e}")

finally:
    cursor.close()
    origem_db.close()

