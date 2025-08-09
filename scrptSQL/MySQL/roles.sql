/*===============================================================
 	Criar role atribuir permissão remover acessos individuais 
 ===============================================================*/

CREATE ROLE dba_role; -- Criação
GRANT SELECT ON `nexti`.* TO `dba_role`@`%`; -- Permissão na Role
GRANT EXECUTE ON PROCEDURE `mysql`.`rds_kill` TO 'dba_role'@'%';
REVOKE ALL PRIVILEGES ON *.* FROM 'adam.rodrigues'@'%'; -- Removendo privilegios individuais
GRANT dba_role TO 'adam.rodrigues'@'%';  -- Permissão para utilizar a role
SET DEFAULT ROLE dba_role TO 'adam.rodrigues'@'%'; -- Atribuir a role ao usuario
FLUSH PRIVILEGES; -- Recarregar permissões


