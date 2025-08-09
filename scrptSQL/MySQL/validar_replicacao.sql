SELECT 
    rss.thread_id
    , channel_name AS Channel_Name,
    smi.host AS Master_Host,
    smi.user_name AS Master_User,
    smi.port AS Master_Port,
    rcs.service_state AS Slave_IO_Running,
    rss.service_state AS Slave_SQL_Running,
    t.processlist_time AS Seconds_Behind_Master,
    rcs.last_error_number AS Last_IO_Errno,
    rcs.last_error_message AS Last_IO_Error,
    rss.last_error_number AS Last_SQL_Errno,
    rss.last_error_message AS Last_SQL_Error,
    tc.processlist_state AS  Slave_IO_State,
    t.processlist_state AS  Slave_SQL_Running_State,
    smi.master_log_name AS Master_Log_File,
    smi.master_log_pos AS Read_Master_Log_Pos,
    ssi.master_log_pos AS Exec_Master_Log_Pos,
    ssi.Relay_log_name AS Relay_log_name,
    ssi.Relay_log_pos AS Relay_log_pos,
    ssi.Number_of_lines AS ssi_Number_of_Lines
    , t.PROCESSLIST_INFO
    , esc.SQL_TEXT
--    ,'---' AS "---"
--    , smi.*
--    ,'---' AS "---"
--    , ssi.*
--    ,'---' AS "---"
--    , rcs.*
--    ,'---' AS "---"
--    , t.*
--    ,'---' AS "---"
--    , tc.*
FROM mysql.slave_master_info smi 
JOIN mysql.slave_relay_log_info ssi USING (channel_name)
JOIN performance_schema.replication_connection_status rcs USING (channel_name)
LEFT JOIN performance_schema.replication_applier_status_by_worker rss USING (channel_name)
LEFT JOIN performance_schema.threads t ON (rss.thread_id = t.thread_id)
LEFT JOIN performance_schema.threads tc ON (rcs.thread_id = tc.thread_id)
LEFT JOIN performance_schema.events_statements_current esc ON t.THREAD_ID = esc.THREAD_ID
;