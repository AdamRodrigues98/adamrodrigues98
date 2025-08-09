select user
	,account_locked
	,mysql.`user`.password_last_changed 
	,CONCAT("ALTER USER '", user, "'@'%' ACCOUNT LOCK;") AS Bloqueio
	,CONCAT("ALTER USER '", user, "'@'%' ACCOUNT UNLOCK;") AS Desbloqueio
from mysql.user
where user in ('user'
)
AND account_locked = 'Y'
