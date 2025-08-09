/****************************
  	KILL Consultas
 ***************************/

-- Visualizar 

SELECT Id, User, Host, db, Command, Time, State, Info 
FROM INFORMATION_SCHEMA.PROCESSLIST 
WHERE Command = 'Query' AND Time > 60;

SELECT Id, User, Host, db, Command, Time, State, Info 
FROM INFORMATION_SCHEMA.PROCESSLIST 
WHERE Command = 'Query' 
AND user not in('rdsadmin', 'rdsrepladmin', 'system user', 'event_scheduler')
AND state = 'executing'

-- MySQL
SELECT CONCAT('KILL ', Id, ';') AS kill_command
FROM INFORMATION_SCHEMA.PROCESSLIST
WHERE Command = 'Query' AND Time > 60;


-- RDS
SELECT CONCAT('CALL mysql.rds_kill', + '(', Id, + ')', ';') AS kill_command
FROM INFORMATION_SCHEMA.PROCESSLIST
WHERE Command = 'Query' AND Time > 1000
AND user not in('rdsadmin', 'rdsrepladmin', 'system user', 'event_scheduler')


SELECT Id, User, Host, db, Command, Time, State, Info 
FROM INFORMATION_SCHEMA.PROCESSLIST 
WHERE Command = 'Query' AND Time > 60;

/*******************************
	Kill Sleep connections
*******************************/
          
SELECT CONCAT('KILL ', Id, ';') AS kill_command
FROM INFORMATION_SCHEMA.PROCESSLIST
WHERE Command = 'sleep' AND Time > 300;   


-- RDS
SELECT CONCAT('CALL mysql.rds_kill', + '(', Id, + ')', ';') AS kill_command
FROM INFORMATION_SCHEMA.PROCESSLIST
WHERE Command = 'Query' AND Time > 60;






 




