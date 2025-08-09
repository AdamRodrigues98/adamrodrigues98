from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator  # Airflow ≥2.3
from airflow.decorators import task, task_group
from airflow.providers.trino.hooks.trino import TrinoHook
from airflow.providers.trino.operators.trino import TrinoOperator
from airflow.providers.amazon.aws.operators.s3 import S3DeleteObjectsOperator

default_args = {
    'is_paused_upon_creation': True,
    'start_date': datetime(2024, 1, 1)
}

codigos_clientes        = [999]
CATALOGO_ORIGEM         = "mysql"
SCHEMA_ORIGEM           = "adam"
CATALOGO_DESTINO        = "iceberg"
SCHEMA_DESTINO          = "client1"

nomes_tabelas_dominio     = []
nomes_tabelas_customer_id = ['person', 'user_account']
joins_por_cliente         = {999: []}
tabelas_com_join          = []
tabelas_com_dois_joins    = []
tabelas_com_tres_joins    = []

LOAD_EXPR = "current_timestamp" 

def create_trino_task(task_id: str, sql: str) -> TrinoOperator:
    return TrinoOperator(
        task_id=task_id,
        sql=sql,
        trino_conn_id='trino_default'
    )

@task
def build_ctas_sql(table_name: str) -> str:
    hook = TrinoHook(trino_conn_id='trino_default')
    cols = hook.get_records(f"""
        SELECT column_name, data_type
          FROM {CATALOGO_ORIGEM}.information_schema.columns
         WHERE table_schema = '{SCHEMA_ORIGEM}'
           AND table_name   = '{table_name}'
         ORDER BY ordinal_position
    """)
    if not cols:
        raise ValueError(f"Nenhuma coluna encontrada para '{table_name}'")
    select_parts = []
    for col, dtype in cols:
        if dtype.lower().startswith('timestamp') and '(0)' in dtype:
            select_parts.append(f"CAST({col} AS TIMESTAMP(3)) AS {col}")
        else:
            select_parts.append(col)

    select_parts.append(f"{LOAD_EXPR} AS load_date")

    select_list = ",\n       ".join(select_parts)
    full_name = f"{CATALOGO_DESTINO}.{SCHEMA_DESTINO}.{table_name}"
    return f"""
CREATE TABLE {full_name}
WITH (
    format = 'PARQUET',
    format_version = 2,
    location = 's3://adam-data-client1/adam/full/{table_name}/'
)
AS
SELECT
       {select_list}
  FROM {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.{table_name}
 WHERE 1 = 0
""".strip()

@task_group
def drop_and_create_destino():
    tabelas = set(
        nomes_tabelas_dominio +
        nomes_tabelas_customer_id +
        [list(j.keys())[0] for j in tabelas_com_join] +
        [list(j.keys())[0] for joins in joins_por_cliente.values() for j in joins] +
        [list(j.keys())[0] for j in tabelas_com_dois_joins] +
        [list(j.keys())[0] for j in tabelas_com_tres_joins]
    )
    for tabela in tabelas:
        drop = create_trino_task(f"drop_{tabela}", f"DROP TABLE IF EXISTS {CATALOGO_DESTINO}.{SCHEMA_DESTINO}.{tabela}")
        clear = S3DeleteObjectsOperator(
            task_id=f"clear_s3_{tabela}",
            aws_conn_id='aws_default',
            bucket='adam-data-client1',
            prefix=f"adam/full/{tabela}/"
        )
        ctas_sql = build_ctas_sql.override(task_id=f"build_ctas_sql_{tabela}")(tabela)
        create = create_trino_task(f"create_{tabela}", sql=ctas_sql)
        drop >> clear >> create

############################################
#           Tabelas Dominio      #
############################################
@task_group
def carregar_dominio():
    for tabela in nomes_tabelas_dominio:
        create_trino_task(
            task_id=f"insert_domain_{tabela}",
            sql=f"""
INSERT INTO {CATALOGO_DESTINO}.{SCHEMA_DESTINO}.{tabela}
SELECT T.*,
       {LOAD_EXPR} AS load_date
  FROM {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.{tabela} T
"""
        )

############################################
#           Tabelas por Customer_ID        #
############################################
@task_group
def cliente_task_group(customer_id: int):
    for tabela in nomes_tabelas_customer_id:
        create_trino_task(
            task_id=f"insert_cust_{tabela}_{customer_id}",
            sql=f"""
INSERT INTO {CATALOGO_DESTINO}.{SCHEMA_DESTINO}.{tabela}
SELECT T.*,
       {LOAD_EXPR} AS load_date
  FROM {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.{tabela} T
 WHERE customer_id = {customer_id}
"""
        )

############################################
#           Tabelas com JOIN               #
############################################
    for join in tabelas_com_join:
        t1, c1 = list(join.items())[0]
        t2, c2 = list(join.items())[1]

        insert = create_trino_task(
            task_id=f"insert_join_{t1}_{customer_id}",
            sql=f"""
INSERT INTO {CATALOGO_DESTINO}.{SCHEMA_DESTINO}.{t1}
SELECT T.*,
       {LOAD_EXPR} AS load_date
  FROM {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.{t1} T
  JOIN {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.{t2} T2
    ON T.{c1} = T2.{c2}
 WHERE T2.customer_id = {customer_id}"""
        )

############################################
#     Tabelas com JOIN  por cliente        #
############################################

    joins_cliente = joins_por_cliente.get(customer_id, [])

    for join in joins_cliente:
        t1, c1 = list(join.items())[0]
        t2, c2 = list(join.items())[1]

        insert = create_trino_task(
            task_id=f"insert_join_custom_{t1}_{customer_id}",
            sql=f"""
INSERT INTO {CATALOGO_DESTINO}.{SCHEMA_DESTINO}.{t1}
SELECT T.*,
    {LOAD_EXPR} AS load_date 
FROM {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.{t1} T
JOIN {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.{t2} T2
ON T.{c1} = T2.{c2}
WHERE T2.customer_id = {customer_id}"""
        )
############################################
#        Tabelas com dois JOINs            #
############################################
    for join in tabelas_com_dois_joins:
        t1 = list(join.keys())[0]
        c1, t2, c2, c3, t3, c4 = join[t1]  

        insert = create_trino_task(
            task_id=f"insert_dois_joins_{t1}_{customer_id}",
            sql=f"""
INSERT INTO {CATALOGO_DESTINO}.{SCHEMA_DESTINO}.{t1}
SELECT T1.*,
       {LOAD_EXPR} AS load_date
  FROM {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.{t1} T1
  INNER JOIN {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.{t2} T2 ON T1.{c1} = T2.{c2}
  INNER JOIN {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.{t3} T3 ON T2.{c3} = T3.{c4}
 WHERE T3.customer_id = {customer_id}"""
        )


############################################
#      Tabelas com tres JOINs              #
############################################
    for join in tabelas_com_tres_joins:
        t1 = list(join.keys())[0]
        c1, t2, c2, c3, t3, c4, c5, t4, c6 = join[t1]

        insert = create_trino_task(
            task_id=f"insert_tres_joins_{t1}_{customer_id}",
            sql=f"""
INSERT INTO {CATALOGO_DESTINO}.{SCHEMA_DESTINO}.{t1}
SELECT T1.*,
       {LOAD_EXPR} AS load_date
  FROM {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.{t1} T1
  INNER JOIN {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.{t2} T2 ON T1.{c1} = T2.{c2}
  INNER JOIN {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.{t3} T3 ON T2.{c3} = T3.{c4}
  INNER JOIN {CATALOGO_ORIGEM}.{SCHEMA_ORIGEM}.{t4} T4 ON T3.{c5} = T4.{c6}
 WHERE T4.customer_id = {customer_id}"""
        )


with DAG(
    "client1_lakehouse_PARQUET",
    description="ETL Dinâmico: CTAS em Parquet e INSERTs com filtros e joins",
    default_args=default_args,
    schedule_interval="10 11 * * *",
    catchup=False,
    concurrency=2,
    max_active_runs=1,
    tags=["trino", "lakehouse", "client1", "S3", "Parquet"]
) as dag:

    drop_create = drop_and_create_destino()

    start_inserts = EmptyOperator(task_id="start_inserts")

    dominio = carregar_dominio()

    clientes = [cliente_task_group(customer_id=c) for c in codigos_clientes]


    drop_create >> start_inserts
    start_inserts >> dominio
    start_inserts >> clientes
