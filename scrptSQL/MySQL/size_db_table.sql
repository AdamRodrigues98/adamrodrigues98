-- Memoria
SELECT * FROM sys.innodb_buffer_stats_by_table 

-- Tabelas
SELECT
    table_name,
    table_rows AS 'Rows',
    CONCAT(
        CASE 
            WHEN data_length >= 1024 * 1024 * 1024 THEN CONCAT(ROUND(data_length / (1024 * 1024 * 1024), 1), 'GB')
            WHEN data_length >= 1024 * 1024 THEN CONCAT(ROUND(data_length / (1024 * 1024), 2), 'MB')
            ELSE CONCAT(ROUND(data_length / 1024, 2), 'KB')
        END
    ) AS 'Data',
    ROUND(data_length / table_rows, 0) AS 'DataRow',
    CONCAT(
        CASE 
            WHEN index_length >= 1024 * 1024 * 1024 THEN CONCAT(ROUND(index_length / (1024 * 1024 * 1024), 1), 'GB')
            WHEN index_length >= 1024 * 1024 THEN CONCAT(ROUND(index_length / (1024 * 1024), 2), 'MB')
            ELSE CONCAT(ROUND(index_length / 1024, 2), 'KB')
        END
    ) AS 'idx',
    ROUND(index_length / table_rows, 0) AS 'IdxRow',
    CONCAT(
        CASE 
            WHEN (data_length + index_length + data_free) >= 1024 * 1024 * 1024 THEN CONCAT(ROUND((data_length + index_length + data_free) / (1024 * 1024 * 1024), 1), 'GB')
            WHEN (data_length + index_length + data_free) >= 1024 * 1024 THEN CONCAT(ROUND((data_length + index_length + data_free) / (1024 * 1024), 2), 'MB')
            ELSE CONCAT(ROUND((data_length + index_length + data_free) / 1024, 2), 'KB')
        END
    ) AS 'Total Size',
    CONCAT(
        CASE 
            WHEN data_free >= 1024 * 1024 * 1024 THEN CONCAT(ROUND(data_free / (1024 * 1024 * 1024), 2), 'GB')
            WHEN data_free >= 1024 * 1024 THEN CONCAT(ROUND(data_free / (1024 * 1024), 2), 'MB')
            ELSE CONCAT(ROUND(data_free / 1024, 2), 'KB')
        END
    ) AS 'Data Free'
FROM
    information_schema.tables
WHERE
    table_schema = 'audit'
    AND table_name = 'auditoria'
ORDER BY data_length DESC;

-- Base

SELECT
    table_schema AS 'DB Name',
    CONCAT(
        CASE 
            WHEN (SUM(data_length + index_length + data_free)) >= 1024 * 1024 * 1024 THEN CONCAT(ROUND(SUM(data_length + index_length + data_free) / (1024 * 1024 * 1024), 1), ' GB')
            WHEN (SUM(data_length + index_length + data_free)) >= 1024 * 1024 THEN CONCAT(ROUND(SUM(data_length + index_length + data_free) / (1024 * 1024), 2), ' MB')
            ELSE CONCAT(ROUND(SUM(data_length + index_length + data_free) / 1024, 2), ' KB')
        END
    ) AS 'Total Size',
    SUM(data_length) AS 'Data Length',
    SUM(index_length) AS 'Index Length',
    SUM(data_free) AS 'Data Free'
FROM
    information_schema.tables
WHERE
    table_schema IN ('db_name', 'direct', 'university')
GROUP BY
    table_schema
ORDER BY
    index_length DESC;

-- V2

SELECT
    table_name,
    table_rows AS 'Rows',
    CONCAT(
        CASE 
            WHEN data_length >= 1024 * 1024 * 1024 THEN CONCAT(ROUND(data_length / (1024 * 1024 * 1024), 1), 'GB')
            WHEN data_length >= 1024 * 1024 THEN CONCAT(ROUND(data_length / (1024 * 1024), 2), 'MB')
            ELSE CONCAT(ROUND(data_length / 1024, 2), 'KB')
        END
    ) AS 'Data',
    ROUND(data_length / (1024 * 1024), 2) AS 'Data_MB',
    ROUND(data_length / (1024 * 1024 * 1024), 2) AS 'Data_GB',
    ROUND(data_length / table_rows, 0) AS 'DataRow',
    CONCAT(
        CASE 
            WHEN index_length >= 1024 * 1024 * 1024 THEN CONCAT(ROUND(index_length / (1024 * 1024 * 1024), 1), 'GB')
            WHEN index_length >= 1024 * 1024 THEN CONCAT(ROUND(index_length / (1024 * 1024), 2), 'MB')
            ELSE CONCAT(ROUND(index_length / 1024, 2), 'KB')
        END
    ) AS 'Idx',
    ROUND(index_length / (1024 * 1024), 2) AS 'Idx_MB',
    ROUND(index_length / (1024 * 1024 * 1024), 2) AS 'Idx_GB',
    ROUND(index_length / table_rows, 0) AS 'IdxRow',
    CONCAT(
        CASE 
            WHEN (data_length + index_length + data_free) >= 1024 * 1024 * 1024 THEN CONCAT(ROUND((data_length + index_length + data_free) / (1024 * 1024 * 1024), 1), 'GB')
            WHEN (data_length + index_length + data_free) >= 1024 * 1024 THEN CONCAT(ROUND((data_length + index_length + data_free) / (1024 * 1024), 2), 'MB')
            ELSE CONCAT(ROUND((data_length + index_length + data_free) / 1024, 2), 'KB')
        END
    ) AS 'Total Size',
    ROUND((data_length + index_length + data_free) / (1024 * 1024), 2) AS 'TotalSize_MB',
    ROUND((data_length + index_length + data_free) / (1024 * 1024 * 1024), 2) AS 'TotalSize_GB',
    CONCAT(
        CASE 
            WHEN data_free >= 1024 * 1024 * 1024 THEN CONCAT(ROUND(data_free / (1024 * 1024 * 1024), 2), 'GB')
            WHEN data_free >= 1024 * 1024 THEN CONCAT(ROUND(data_free / (1024 * 1024), 2), 'MB')
            ELSE CONCAT(ROUND(data_free / 1024, 2), 'KB')
        END
    ) AS 'Data Free'
FROM information_schema.tables
WHERE table_schema = 'db_name'
AND table_name = 'pontos'
ORDER BY data_length DESC;

