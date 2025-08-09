WITH mts_summary_trx AS ( 
SELECT T.THREAD_ID AS THREAD_ID
    , T.COUNT_STAR AS COUNT_STAR
FROM performance_schema.events_transactions_summary_by_thread_by_event_name T
WHERE 1=1
    AND T.THREAD_ID IN (SELECT RASBW.THREAD_ID
                        FROM performance_schema.replication_applier_status_by_worker RASBW)
)
SELECT ROUND(100.0 * (T.COUNT_STAR / (SELECT SUM(T2.count_star) FROM mts_summary_trx T2))) AS PCT_USAGE
FROM mts_summary_trx T
ORDER BY PCT_USAGE DESC