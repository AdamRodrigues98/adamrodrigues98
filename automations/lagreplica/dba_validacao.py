import mysql.connector
from configparser import ConfigParser
import datetime

def apontamento(arquivo):
    parser = ConfigParser()
    parser.read(arquivo)
    return parser

config = apontamento('lagreplica/replica.ini')

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
    exit()

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
    exit()

cursor_origem = origem_db.cursor(dictionary=True)
cursor_destino = destino_db.cursor()

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
    cursor_origem.execute(query_latency)
    latency_result = cursor_origem.fetchone()
    
    seconds_behind_master = latency_result.get('Seconds_Behind_Master') if latency_result else 0

    seconds_behind_master = seconds_behind_master if seconds_behind_master is not None else 0

    if seconds_behind_master <= 90:
        print(f"Replicação está dentro do limite. Seconds_Behind_Master: {seconds_behind_master}")
    else:
        print(f"Replicação atrasada. Seconds_Behind_Master: {seconds_behind_master}")    


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
                AND Time > 300
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
            AND Time > 420
            AND State = 'executing'
            AND user NOT IN ('rdsadmin', 'rdsrepladmin', 'system user', 'event_scheduler')
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
