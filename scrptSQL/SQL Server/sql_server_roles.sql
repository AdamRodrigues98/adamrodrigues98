========================================
Roles de Banco de Dados (Database Roles)
========================================
/*
Role                | Descrição                                      
-------------------+-----------------------------------------------
db_owner          | Controle total sobre o banco de dados       
db_securityadmin  | Gerencia permissões dentro do banco de dados
db_accessadmin    | Gerencia acessos ao banco de dados          
db_backupoperator | Pode fazer backup do banco de dados         
db_ddladmin       | Pode criar, alterar e excluir objetos       
db_datareader     | Pode ler todos os dados do banco            
db_datawriter     | Pode inserir, atualizar e excluir dados     
db_denydatareader | Proíbe o usuário de ler dados              
db_denydatawriter | Proíbe o usuário de modificar dados         
*/

Consulta para listar todas as roles do banco e seus membros:

SELECT r.name AS role_name, dp.name AS usuario
FROM sys.database_role_members drm
JOIN sys.database_principals r ON drm.role_principal_id = r.principal_id
JOIN sys.database_principals dp ON drm.member_principal_id = dp.principal_id
ORDER BY r.name, dp.name;

=================================
Roles de Servidor (Server Roles)
=================================

/*
Role              | Descrição                                      
-----------------+-----------------------------------------------
sysadmin        | Controle total sobre o servidor               
serveradmin     | Gerencia configurações do servidor           
securityadmin   | Gerencia logins e permissões de servidor     
processadmin    | Gerencia processos no SQL Server             
setupadmin      | Gerencia configurações de linked servers     
diskadmin       | Gerencia arquivos de disco do SQL Server     
dbcreator       | Pode criar, alterar, excluir bancos de dados 
bulkadmin       | Pode importar dados em massa (BULK INSERT)   
*/


Consulta para listar todas as roles de servidor e seus membros:

SELECT r.name AS role_name, sp.name AS usuario
FROM sys.server_role_members srm
JOIN sys.server_principals r ON srm.role_principal_id = r.principal_id
JOIN sys.server_principals sp ON srm.member_principal_id = sp.principal_id
ORDER BY r.name, sp.name;

========================
Permissões Individuais
========================

/*
Permissão  | Descrição                                       
-----------+-----------------------------------------------
SELECT     | Permite ler dados                             
INSERT     | Permite inserir dados                        
UPDATE     | Permite modificar dados existentes          
DELETE     | Permite excluir dados                        
EXECUTE    | Permite executar procedures e funções       
ALTER      | Permite alterar um objeto (tabela, view, etc.)
CONTROL    | Permite controle total sobre um objeto      
*/

Consulta para listar todas as permissões concedidas no banco:

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
ORDER BY dp.name, obj.name, pe.permission_name;

==============================
Concedendo Permissões e Roles
==============================

Para adicionar um usuário a uma role de banco:

ALTER ROLE db_datareader ADD MEMBER [NOME_DO_USUARIO];

Para adicionar um usuário a uma role de servidor:

ALTER SERVER ROLE sysadmin ADD MEMBER [NOME_DO_USUARIO];

Para remover um usuário de uma role:

ALTER ROLE db_datareader DROP MEMBER [NOME_DO_USUARIO];

