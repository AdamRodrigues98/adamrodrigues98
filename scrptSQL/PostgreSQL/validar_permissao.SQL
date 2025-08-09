WITH usuario_var AS (
    SELECT 'usr_analytics' AS usuario
),
usuario_permissoes AS (
    -- Permissões em tabelas
    SELECT 
        'Tabela' AS tipo,
        table_schema AS esquema,
        table_name AS objeto,
        privilege_type AS permissao
    FROM information_schema.table_privileges, usuario_var
    WHERE grantee = usuario_var.usuario
    UNION ALL
    -- Permissões em esquemas
    SELECT 
        'Esquema' AS tipo,
        nspname AS esquema,
        NULL::text AS objeto,
        'USAGE' AS permissao
    FROM pg_namespace, usuario_var
    WHERE has_schema_privilege(usuario_var.usuario, nspname, 'USAGE')
    UNION ALL
    -- Permissões em funções
    SELECT 
        'Função' AS tipo,
        routine_schema AS esquema,
        routine_name AS objeto,
        privilege_type AS permissao
    FROM information_schema.routine_privileges, usuario_var
    WHERE grantee = usuario_var.usuario
    UNION ALL
    -- Permissões no banco de dados
    SELECT 
        'Banco' AS tipo,
        datname AS esquema,
        NULL::text AS objeto,
        'CONNECT' AS permissao
    FROM pg_database, usuario_var
    WHERE has_database_privilege(usuario_var.usuario, datname, 'CONNECT')
    UNION ALL
    -- Permissões em roles
    SELECT 
        'Role' AS tipo,
        r.rolname AS esquema,
        NULL::text AS objeto,
        'Member' AS permissao
    FROM pg_roles r
    JOIN pg_auth_members am ON r.oid = am.roleid
    JOIN pg_roles u ON u.oid = am.member, usuario_var
    WHERE u.rolname = usuario_var.usuario
    UNION ALL
    -- Permissões em sequências
    SELECT 
        'Sequência' AS tipo,
        sequence_schema AS esquema,
        sequence_name AS objeto,
        'USAGE' AS permissao
    FROM information_schema.sequences, usuario_var
    WHERE has_sequence_privilege(usuario_var.usuario, sequence_schema || '.' || sequence_name, 'USAGE')
)
SELECT * FROM usuario_permissoes
ORDER BY tipo, esquema, objeto;
