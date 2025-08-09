from __future__ import print_function
import os
import pymysql
import logging
import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger.addHandler(handler)

USER_TABLES = {
    'user-scalability': {
        'select_tables': [
             'cliente'
            ,'dispositivo'

    ],
        'dml_tables': [
            'approving_overtime_day_of_week'
            ,'approving_overtime_time_tracking_type'
            ,'batch_manual_comptime'
        ]
    },
    'ponto-scalability': {
        'select_tables': [
             'authorization'
            ,'city'
            ,'client'
            ,'device'
            ,'person'
        ],
        'dml_tables': [
            'adjustment_reason'
            ,'direction'
            ,'shedlock'
        ]
    },
    'ponto-api': {
    'inherits': 'ponto-scalability',
        'dml_tables': [],
        'select_from_parent_dml': True
    },
    'user-api': {
    'inherits': 'user-scalability',
        'dml_tables': [],
        'select_from_parent_dml': True
    },
    'ponto-service-create': {
    'inherits': 'ponto-scalability'
    },
    'ponto-service-adjust': {
    'inherits': 'ponto-scalability'
    },
    'ponto-service-remove': {
    'inherits': 'ponto-scalability'
    },
    'ponto-oddmarkings-producer': {
    'inherits': 'ponto-scalability',
        'dml_tables': ['shedlock'],
        'select_from_parent_dml': True
    },
    'ponto-anr-producer': {
    'inherits': 'ponto-scalability',
        'dml_tables': ['shedlock'],
        'select_from_parent_dml': True
    },
    'ponto-cnr-producer': {
    'inherits': 'ponto-scalability',
        'dml_tables': ['shedlock'],
        'select_from_parent_dml': True
    },
    'ponto-oddmarkings-consumer': {
    'inherits': 'ponto-scalability',
        'dml_tables': ['ponto'],
        'select_from_parent_dml': True
    },
    'ponto-premarked-consumer': {
    'inherits': 'ponto-scalability',
        'dml_tables': ['shedlock'],
        'select_from_parent_dml': True
    },
    'ponto-premarked-producer': {
    'inherits': 'ponto-scalability',
        'dml_tables': ['shedlock'],
        'select_from_parent_dml': True
    },        
         
}


def get_ssm_parameter(name):
    ssm = boto3.client('ssm')
    return ssm.get_parameter(Name=name, WithDecryption=True)['Parameter']['Value']


def create_and_grant_on_database(conn, username, password, db_name, select_tables, dml_tables):
    with conn.cursor() as cur:

        cur.execute("CREATE USER IF NOT EXISTS %s@%s IDENTIFIED WITH mysql_native_password BY %s",(username, '%', password))

        cur.execute(f"REVOKE ALL PRIVILEGES, GRANT OPTION FROM `{username}`@'%';")
        
        cur.execute(f"ALTER USER `{username}`@'%%' IDENTIFIED BY %s;",(password,))

        for tbl in select_tables:cur.execute(f"GRANT SELECT ON `{db_name}`.`{tbl}` TO `{username}`@'%';")

        for tbl in dml_tables:cur.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON `{db_name}`.`{tbl}` TO '{username}'@'%';")


def create_users(host, admin_user, admin_password, port='3306', db_name='nexti', env='qa'):
    if 'master' in host and env == 'prod':
        raise RuntimeError('Não é permitido rodar no master!')

    logger.info(f'Conectando ao RDS em {host}:{port}/{db_name}…')
    conn = pymysql.connect(
        host=host,
        port=int(port),
        user=admin_user,
        passwd=admin_password,
        db=db_name,
        connect_timeout=10
    )
    logger.info('Conectado com sucesso!')

    try:
        for service, info in USER_TABLES.items():
            if 'inherits' in info:
                base_service = info['inherits']
                if base_service not in USER_TABLES:
                    raise KeyError(
                        f"Serviço '{service}' herda de '{base_service}', "
                        f"porém '{base_service}' não está definido em USER_TABLES."
                    )
                parent = USER_TABLES[base_service]

                select_tables = parent['select_tables']
                dml_tables    = parent['dml_tables']

                if 'select_tables' in info:
                    select_tables = info['select_tables']
                if 'dml_tables' in info:
                    dml_tables = info['dml_tables']
            else:
                select_tables = info['select_tables']
                dml_tables    = info['dml_tables']

            if info.get('select_from_parent_dml'):
                parent = USER_TABLES[info['inherits']]
                select_tables = select_tables + parent['dml_tables']
    
            username_param = f"/config/{service}-server-{env}/spring.datasource.username"
            password_param = f"/config/{service}-server-{env}/spring.datasource.password"

            username = get_ssm_parameter(username_param)
            password = get_ssm_parameter(password_param)

            logger.info(f"Criando usuário `{username}` para serviço `{service}` …")

            create_and_grant_on_database(
                conn=conn,
                username=username,
                password=password,
                db_name=db_name,
                select_tables=select_tables,
                dml_tables=dml_tables
            )

        conn.commit()
        logger.info('Todos os usuários criados e permissões aplicadas!')
    except Exception:
        conn.rollback()
        logger.exception('Falha ao aplicar permissões.')
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    USER = os.getenv('DATABASE_CREDENTIAL_USR')
    PWD  = os.getenv('DATABASE_CREDENTIAL_PSW')
    HOST = os.getenv('CNAME')
    ENV  = os.getenv('ENVIRONMENT_NAME', 'qa')
    PORT = os.getenv('DB_PORT', '3306')

    if not all([USER, PWD, HOST]):
        logger.error(
            "As variáveis DATABASE_CREDENTIAL_USR, DATABASE_CREDENTIAL_PSW e CNAME "
            "devem estar definidas."
        )
        exit(1)

    create_users(HOST, USER, PWD, port=PORT, db_name='nexti', env=ENV)