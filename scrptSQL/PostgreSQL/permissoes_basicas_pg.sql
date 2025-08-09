-- Verificar permissões basicas

SELECT r.usename AS grantor,
       e.usename AS grantee,
       nspname,
       privilege_type,
             is_grantable
        FROM pg_namespace
JOIN LATERAL (SELECT *
                FROM aclexplode(nspacl) AS x) a
          ON true
        JOIN pg_user e
          ON a.grantee = e.usesysid
        JOIN pg_user r
          ON a.grantor = r.usesysid 
       WHERE e.usename = 'admissaopg';
GRANT CREATE ON SCHEMA admissao TO admissaopg;

SELECT 
    r.rolname                         AS role_name,
    r.rolcanlogin                     AS can_login,
    r.rolsuper                        AS superuser,
    r.rolcreaterole                   AS can_create_role,
    r.rolcreatedb                     AS can_create_db,
    r.rolreplication                  AS can_replication,
    r.rolbypassrls                    AS can_bypass_rls,
    COALESCE(
        TO_CHAR(r.rolvaliduntil, 'YYYY-MM-DD HH24:MI:SS'),
        'never'
    )                                 AS password_expiration
FROM pg_roles r
WHERE r.rolcanlogin = TRUE
ORDER BY role_name;




-- Verificar e aplicar 

SELECT
    table_catalog,
    table_schema,
    table_name,
    grantee,
    privilege_type
FROM information_schema.table_privileges
where 1=1
and table_name = 'audit_expurgo'
-- AND grantee 'usr_da_nexti'-- nome do usuario
ORDER BY table_catalog, table_schema, table_name, grantee

GRANT TRIGGER, REFERENCES, TRUNCATE, DELETE, UPDATE, SELECT, INSERT
ON nexti.audit_expurgo
TO usr_da_nexti;

-- Verificar o schema

SELECT schema_name
FROM information_schema.schemata
WHERE schema_owner = 'adam.rodrigues';


-- Funções:

SELECT specific_schema, routine_name
FROM information_schema.routines
WHERE specific_schema NOT IN ('pg_catalog', 'information_schema')
  AND specific_schema = 'nome_do_esquema'
  AND specific_schema IN (
      SELECT role_name FROM pg_roles WHERE rolname = 'adam'
  );

-- Permissões gerais do papel:

SELECT * FROM pg_roles WHERE rolname = 'adam';
