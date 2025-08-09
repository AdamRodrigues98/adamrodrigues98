/******************************
 	Usuario SQL Server
 ******************************/
USE master


CREATE LOGIN adam
WITH PASSWORD = 'SENHA';

ALTER LOGIN sapiens WITH PASSWORD = 'xxxxxxxx';

-- Conectar ao banco de dados onde o usuário será criado
USE sapiens;


-- Criar o usuário no banco de dados
CREATE USER adam
FOR LOGIN adam;

-- Listar Login
SELECT name, type_desc, create_date 
FROM sys.server_principals 
WHERE type IN ('S', 'U', 'G', 'C', 'K');

-- Listar User 
SELECT name, type_desc, create_date 
FROM sys.database_principals
WHERE type IN ('S', 'U', 'G', 'C', 'K');

-- User to Login
SELECT dp.name AS database_user, sp.name AS login_name
FROM sys.database_principals dp
LEFT JOIN sys.server_principals sp
ON dp.sid = sp.sid
WHERE dp.type IN ('S', 'U');

==============================================
Validar permissões especificar para o usuario
==============================================

-- Verificar tipo de Role associado ao user

SELECT dp.name AS usuario, 
       dp.type_desc AS tipo_usuario, 
       r.name AS role_name
FROM sys.database_role_members drm
JOIN sys.database_principals r ON drm.role_principal_id = r.principal_id
JOIN sys.database_principals dp ON drm.member_principal_id = dp.principal_id
WHERE dp.name = 'adam';


-- Verificar todos os acesso do user
SELECT 
    dp.name AS usuario,
    dp.type_desc AS tipo_usuario,
    pe.permission_name AS permissao,
    pe.state_desc AS estado,
    obj.name AS objeto,
    obj.type_desc AS tipo_objeto
FROM sys.database_permissions pe
LEFT JOIN sys.objects obj ON pe.major_id = obj.object_id
JOIN sys.database_principals dp ON pe.grantee_principal_id = dp.principal_id
WHERE dp.name = 'adam'
ORDER BY obj.name, pe.permission_name;


-- Verificar acesso a nivel servidor
SELECT 
    sp.name AS usuario, 
    sp.type_desc AS tipo_usuario, 
    spm.permission_name AS permissao, 
    spm.state_desc AS estado
FROM sys.server_permissions spm
JOIN sys.server_principals sp ON spm.grantee_principal_id = sp.principal_id
WHERE sp.name = 'adam';


User adam xZw5#j$nL

-- Conceder permissões de leitura (SELECT) para o novo usuário
GRANT SELECT TO adam;

REVOKE SELECT ON DATABASE::sapiens FROM adam;

GRANT SELECT ON [dbo].E085CLI TO adam;
GRANT SELECT ON [dbo].E085HCL TO adam;
GRANT SELECT ON [dbo].E160CTR TO adam;
GRANT SELECT ON [dbo].E160CVS TO adam;
GRANT SELECT ON [dbo].E160CVP TO adam;
GRANT SELECT ON [dbo].E075PRO TO adam;
GRANT SELECT ON [dbo].E080SER TO adam;

============================
Permissões
===========================

ALTER ROLE db_owner ADD MEMBER [NOME_DO_USUARIO];
EXEC sp_addrolemember 'db_owner', 'NOME_DO_USUARIO';
ALTER ROLE db_owner DROP MEMBER [NOME_DO_USUARIO];


-- E085CLI,E085HCL,E160CTR,E160CVS,E160CVP, E075PRO,E080SER
/*********************************
  	Verificar permissões
 *********************************/

SELECT  
    [UserName] = ulogin.[name],
    [UserType] = CASE princ.[type]
                    WHEN 'S' THEN 'SQL User'
                    WHEN 'U' THEN 'Windows User'
                    WHEN 'G' THEN 'Windows Group'
                 END,  
    [DatabaseUserName] = princ.[name],       
    [Role] = null,      
    [PermissionType] = perm.[permission_name],       
    [PermissionState] = perm.[state_desc],       
    [ObjectType] = CASE perm.[class] 
                        WHEN 1 THEN obj.type_desc               -- Schema-contained objects
                        ELSE perm.[class_desc]                  -- Higher-level objects
                   END,       
    [ObjectName] = CASE perm.[class] 
                        WHEN 1 THEN OBJECT_NAME(perm.major_id)  -- General objects
                        WHEN 3 THEN schem.[name]                -- Schemas
                        WHEN 4 THEN imp.[name]                  -- Impersonations
                   END,
    [ColumnName] = col.[name]
FROM    
    --database user
    sys.database_principals princ  
LEFT JOIN
    --Login accounts
    sys.server_principals ulogin on princ.[sid] = ulogin.[sid]
LEFT JOIN        
    --Permissions
    sys.database_permissions perm ON perm.[grantee_principal_id] = princ.[principal_id]
LEFT JOIN
    --Table columns
    sys.columns col ON col.[object_id] = perm.major_id 
                    AND col.[column_id] = perm.[minor_id]
LEFT JOIN
    sys.objects obj ON perm.[major_id] = obj.[object_id]
LEFT JOIN
    sys.schemas schem ON schem.[schema_id] = perm.[major_id]
LEFT JOIN
    sys.database_principals imp ON imp.[principal_id] = perm.[major_id]
WHERE 
    princ.[type] IN ('S','U','G') AND
    -- No need for these system accounts
    princ.[name] NOT IN ('sys', 'INFORMATION_SCHEMA')
    



-- Conectar ao banco de dados onde o usuário será criado
USE sapiens;


-- Criar o usuário no banco de dados
CREATE USER [carlos.silva] FOR LOGIN [carlos.silva];


GRANT SELECT ON [dbo].E160CVP TO [carlos.silva];
GRANT SELECT ON [dbo].E160CVS TO [carlos.silva];
GRANT SELECT ON [dbo].E160OBS TO [carlos.silva];
GRANT SELECT ON [dbo].E085CLI TO [carlos.silva];

REVOKE SELECT ON [dbo].E160CVP FROM [carlos.silva];
REVOKE SELECT ON [dbo].E160CVS FROM [carlos.silva];
REVOKE SELECT ON [dbo].E160OBS FROM [carlos.silva];
REVOKE SELECT ON [dbo].E085CLI FROM [carlos.silva];


GRANT SELECT ON SCHEMA::dbo TO [carlos.silva];

