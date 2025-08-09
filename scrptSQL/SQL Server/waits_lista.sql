--verificar a lista
https://learn.microsoft.com/pt-br/sql/relational-databases/system-dynamic-management-views/sys-dm-os-wait-stats-transact-sql?view=sql-server-ver15

select * from sys.dm_os_wait_stats 
    order by wait_time_ms desc


DBCC SQLPERF ('sys.dm_os_wait_stats', CLEAR);  
    GO 
