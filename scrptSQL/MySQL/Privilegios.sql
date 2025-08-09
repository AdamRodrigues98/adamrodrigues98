CREATE USER 'adam.rodrigues'@'%' IDENTIFIED BY '99999999';
GRANT ALL PRIVILEGES ON *.* TO 'adam.rodrigues'@'%';
GRANT SELECT ON `db_name`.* TO `adam.rodrigues`@`%`
REVOKE ALL PRIVILEGES ON *.* FROM 'adam.rodrigues'@'%';

SHOW GRANTS FOR 'adam.rodruges'@'%';

REVOKE DROP ON tbc.* FROM 'adam.rodrigues';

DROP USER 'adam.rodrigues'@'%';

ALTER USER 'adam.rodrigues'@'%' IDENTIFIED BY '888888888';


FLUSH PRIVILEGES;  