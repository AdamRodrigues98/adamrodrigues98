/**********************
    Info das Querys
 ********************/
SELECT 
      THREAD_ID
    , DIGEST_TEXT
    , SQL_TEXT
    , (TIMER_END - TIMER_START) / 1000000000000 AS EXECUTION_TIME_SECONDS  -- Tempo de execução em segundos
    , ROWS_EXAMINED
    , ROWS_SENT
    , ROWS_AFFECTED
    , LOCK_TIME
    , LOCK_TIME / 1000000000000 AS LOCK_TIME_SECONDS
    , TIMER_WAIT
    , TIMER_WAIT / 1000000000000 AS EXECUTION_TIME_SECONDS
FROM 
    performance_schema.events_statements_history
WHERE 
    SQL_TEXT LIKE '%select 
  per.id as adam, 
  mar.sequence, 
  case when wsi.marking is not null %'
    AND SQL_TEXT NOT LIKE '%SELECT  THREAD_ID
	, DIGEST_TEXT
	, SQL_TEXT
	, ROWS_EXAMINED%'
ORDER BY 
    EVENT_ID DESC 
LIMIT 10;

