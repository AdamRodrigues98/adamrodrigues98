from datetime import datetime, timedelta
from airflow import DAG
from airflow.models import Variable
from airflow.providers.trino.operators.trino import TrinoOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.dummy import DummyOperator
import time

#########################
#   Configuração da DAG #
#########################

default_args = {
    'is_paused_upon_creation': True,
    'start_date': datetime(2024, 1, 1),
    'execution_timeout': timedelta(hours=1),
}

CUSTOMER_NAME = "nexti"
CATALOGO_ORIGEM = "mysqlauditoria"
CATALOGO_DESTINO = "iceberg"
SCHEMA_ORIGEM = "auditoria"
SCHEMA_DESTINO = "auditoria"
MAX_RUNS = 15
LIMIT = 50000


VAR_NAME = f"auditoria_run_count_{CUSTOMER_NAME}"

dag = DAG(
    f"auditoria_move_data_{CUSTOMER_NAME}",
    description='DAG para inserção no Iceberg, Transacional e execução da procedure',
    default_args=default_args,
    schedule_interval='30 10 * * *',  # 07:30 em UTC
    concurrency=1,
    max_active_runs=1,
    catchup=False,
)

###############################
#       Tarefas da DAG        #
###############################


def check_run_count(**kwargs):
    for _ in range(5):
        try:
            run_count = int(Variable.get(VAR_NAME, default_var=0))
            
            if run_count >= MAX_RUNS:
                new_count = 0
                Variable.set(VAR_NAME, new_count)
                print(f"Contador atingiu {MAX_RUNS}. Reiniciando para 0.")
            else:
                new_count = run_count + 1
                Variable.set(VAR_NAME, new_count)
                print(f"Contador atualizado: {run_count} → {new_count}")
            
            return new_count
        
        except Exception as e:
            print(f"Erro ao atualizar contador: {str(e)}")
            time.sleep(1)

get_run_count = PythonOperator(
    task_id='get_run_count',
    python_callable=check_run_count,
    provide_context=True,
    dag=dag,
)

def decide_next_run(**kwargs):
    run_count = int(Variable.get(VAR_NAME, default_var=0))
    
    if run_count == 0:
        print("Contador está zerado (atingiu MAX_RUNS). Encerrando execução.")
        return "stop_execution"
    
    return "check_row_count"

validate_run_count = BranchPythonOperator(
    task_id="validate_run_count",
    python_callable=decide_next_run,
    provide_context=True,
    dag=dag,
)

check_row_count = TrinoOperator(
    task_id='check_row_count',
    sql=f"""
        SELECT COUNT(*) AS total
        FROM {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.auditoria_trail
        WHERE action_date < current_date - INTERVAL '1' year
    """,
    trino_conn_id='trino_default',
    dag=dag,
)

def decide_continue_or_stop(**kwargs):
    ti = kwargs['ti']
    result = ti.xcom_pull(task_ids='check_row_count')

    if not result or not result[0]:
        print("Nenhum resultado encontrado no COUNT. Encerrando DAG.")
        return "stop_execution"

    count = result[0][0]
    print(f"Contagem de registros: {count}")
    if count > LIMIT:
        return "insert_into_iceberg"
    return "stop_execution"

decide_branch = BranchPythonOperator(
    task_id='decide_continue_or_stop',
    python_callable=decide_continue_or_stop,
    provide_context=True,
    dag=dag,
)

# Insert no Iceberg
insert_into_iceberg = TrinoOperator(
    task_id="insert_into_iceberg",
    sql=f"""
    INSERT INTO {CATALOGO_DESTINO}.{SCHEMA_DESTINO}.auditoria_trail (
        id, user_account_id, customer_id, entity_name, path_name,
        entity_id, action, old_value, new_value, action_date, move_date
    )
    SELECT
        id, user_account_id, customer_id, entity_name, path_name,
        entity_id, action, old_value, new_value, action_date, now()
    FROM {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.auditoria_trail
    WHERE action_date < current_date - INTERVAL '1' year
    ORDER BY id ASC
    LIMIT {LIMIT}
    """,
    trino_conn_id='trino_default',
    dag=dag
)

# Insert no transacional
insert_into_transacional = TrinoOperator(
    task_id="insert_into_transacional",
    sql=f"""
    INSERT INTO {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.auditoria_delete
    SELECT id
    FROM {CATALOGO_DESTINO}.{SCHEMA_DESTINO}.auditoria_trail
    WHERE move_date IN (
        SELECT DISTINCT move_date
        FROM {CATALOGO_DESTINO}.{SCHEMA_DESTINO}.auditoria_trail
        ORDER BY move_date DESC
        LIMIT 1
    )
    """,
    trino_conn_id='trino_default',
    dag=dag
)

# Chama a procedure no MySQL
execute_procedure = MySqlOperator(
    task_id="execute_procedure",
    sql="CALL auditoria.sp_delete_from_auditoria_trail()",
    mysql_conn_id="auditoria_default",
    dag=dag
)

# Dispara a próxima execução da própria DAG
trigger_next_run = TriggerDagRunOperator(
    task_id='trigger_next_run',
    trigger_dag_id=f"auditoria_move_data_{CUSTOMER_NAME}", 
    dag=dag,
)

# Dummy para encerrar quando atingir o limite
stop_execution = DummyOperator(
    task_id="stop_execution",
    dag=dag,
)


###############################
#     Encadeamento da DAG     #
###############################

get_run_count >> validate_run_count
validate_run_count >> check_row_count
validate_run_count >> stop_execution
check_row_count >> decide_branch
decide_branch >> insert_into_iceberg >> insert_into_transacional >> execute_procedure >> trigger_next_run
decide_branch >> stop_execution
stop_execution  
