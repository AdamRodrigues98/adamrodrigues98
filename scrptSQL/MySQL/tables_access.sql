/********************
 	UPDATE
 *******************/
SELECT user,
       host
FROM mysql.db
WHERE Db = 'db_name'
      AND Update_priv = 'Y'

UNION

SELECT user,
       host
FROM mysql.tables_priv
WHERE Db = 'db_name'
      AND Table_name = 'table_name'
      AND Table_priv LIKE '%Update%'

UNION

SELECT grantee AS user,
       '' AS host
FROM information_schema.USER_PRIVILEGES
WHERE PRIVILEGE_TYPE = 'UPDATE'
      AND grantee LIKE '%db_name%';
       
     

/********************
 	INSERT
 *******************/     
     
SELECT user,
       host
FROM mysql.db
WHERE Db = 'db_name'
      AND Insert_priv = 'Y'
UNION
SELECT user,
       host
FROM mysql.tables_priv
WHERE Db = 'db_name'
      AND Table_name = 'table_name'
      AND Table_priv LIKE '%Insert%'

UNION
SELECT grantee AS user,
       '' AS host
FROM information_schema.USER_PRIVILEGES
WHERE PRIVILEGE_TYPE = 'INSERT'
      AND grantee LIKE '%db_name%';
     
/********************
 	DELETE 
 *******************/
SELECT user,
       host
FROM mysql.db
WHERE Db = 'db_name'
      AND Delete_priv = 'Y'
UNION
SELECT user,
       host
FROM mysql.tables_priv
WHERE Db = 'db_name'
      AND Table_name = 'table_name'
      AND Table_priv LIKE '%Delete%'

UNION
SELECT grantee AS user,
       '' AS host
FROM information_schema.USER_PRIVILEGES
WHERE PRIVILEGE_TYPE = 'DELETE'
      AND grantee LIKE '%db_name%';   
     
/********************
 	SELECT
 *******************/     
SELECT user,
       host
FROM mysql.db
WHERE Db = 'db_name'
      AND Select_priv = 'Y'
UNION
SELECT user,
       host
FROM mysql.tables_priv
WHERE Db = 'db_name'
      AND Table_name = 'table_name'
      AND Table_priv LIKE '%Select%'

UNION
SELECT grantee AS user,
       '' AS host
FROM information_schema.USER_PRIVILEGES
WHERE PRIVILEGE_TYPE = 'SELECT'
      AND grantee LIKE '%db_name%';       
     
