show processlist

select allow_enable_nexti_club_by_company from customer_configuration limit 1

SELECT Id, User, Host, db, Command, Time, State, Info 
FROM INFORMATION_SCHEMA.PROCESSLIST 
WHERE Command = 'Query' -- AND Time > 60
AND user not in('rdsadmin', 'rdsrepladmin', 'system user', 'event_scheduler')
AND state = 'executing'


CALL mysql.rds_kill(381032)
/*
381032
380672
381384
381633
381305
381466
378482
381386
381626
381387
381451
381468
 */

SELECT
  dw.REQUESTING_ENGINE_TRANSACTION_ID AS waiting_trx_id,
  dw.REQUESTING_THREAD_ID             AS waiting_thread,
  dl.LOCK_MODE,
  dl.LOCK_TYPE,
  dl.OBJECT_SCHEMA,
  dl.OBJECT_NAME,
  dl.INDEX_NAME,
  dw.BLOCKING_ENGINE_TRANSACTION_ID  AS blocking_trx_id,
  dw.BLOCKING_THREAD_ID              AS blocking_thread
FROM
  performance_schema.data_lock_waits AS dw
INNER JOIN performance_schema.data_locks   AS dl ON dl.ENGINE_LOCK_ID = dw.REQUESTING_ENGINE_LOCK_ID;

SELECT * 
FROM sys.innodb_lock_waits;


SELECT
  t.trx_id,
  t.trx_mysql_thread_id   AS thread_id,      
  t.trx_state,
  t.trx_started,
  t.trx_wait_started,
  t.trx_rows_locked,
  t.trx_rows_modified,
  t.trx_query,
  p.ID                    AS processlist_id,   
  p.USER                  AS trx_user,
  p.HOST                  AS trx_host,
  p.COMMAND               AS trx_command,
  p.TIME                  AS trx_time,
  p.STATE                 AS trx_state_in_processlist,
  p.INFO                  AS trx_info
FROM information_schema.innodb_trx AS t
LEFT JOIN information_schema.processlist AS p ON p.ID = t.trx_mysql_thread_id
ORDER BY
  t.trx_started;



SELECT
  etc.THREAD_ID            AS thread_id,
  t.PROCESSLIST_ID        AS processlist_id,
  t.PROCESSLIST_USER      AS trx_user,
  t.PROCESSLIST_HOST      AS trx_host,
  etc.STATE               AS trx_state,
  etc.ACCESS_MODE         AS access_mode,
  etc.ISOLATION_LEVEL     AS isolation_level,
  etc.AUTOCOMMIT          AS autocommit,
  etc.TIMER_START         AS timer_start,
  t.PROCESSLIST_INFO      AS trx_query
FROM
  performance_schema.events_transactions_current AS etc
JOIN
  performance_schema.threads                  AS t
  ON t.THREAD_ID = etc.THREAD_ID
WHERE
  etc.STATE = 'ACTIVE'
ORDER BY
  etc.TIMER_START;


SELECT
  t.trx_id,
  t.trx_state,
  t.trx_started,
  t.trx_wait_started,
  t.trx_rows_locked,
  t.trx_rows_modified,
  t.trx_query,
  p.USER       AS trx_user,
  p.HOST       AS trx_host,
  p.COMMAND    AS trx_command,
  p.TIME       AS trx_time,
  p.STATE      AS trx_state_in_processlist,
  p.INFO       AS trx_info
FROM
  information_schema.innodb_trx AS t
LEFT JOIN
  information_schema.processlist AS p
    ON p.ID = t.trx_mysql_thread_id
ORDER BY
  t.trx_started;




