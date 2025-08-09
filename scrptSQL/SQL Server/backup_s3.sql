-- Realizar o backup de um banco SQL SERVER para o S3
EXEC msdb.dbo.rds_backup_database 
    @source_db_name = 'sapiens',
    @s3_arn_to_backup_to = 'arn:aws:s3:::db-name-internal-s3-mssql/adam.bkp.bak',
    @overwrite_S3_backup_file = 1;

-- Validar como esta a task informando o task id
EXEC msdb.dbo.rds_task_status @task_id = 6;


-- Realizar o backup de um banco SQL SERVER para o S3
EXEC msdb.dbo.rds_restore_database 
    @restore_db_name = 'sapiens_hml',
    @s3_arn_to_restore_from = 'arn:aws:s3:::db-name-internal-s3-mssql/adam.bkp.bak';

