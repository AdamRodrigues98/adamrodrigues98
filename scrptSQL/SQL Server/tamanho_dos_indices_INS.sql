IF (OBJECT_ID('tempdb..#tamanho_indices') IS NOT NULL) DROP TABLE #tamanho_indices
CREATE TABLE #tamanho_indices (
    [database]   NVARCHAR(256),
    [schema]     NVARCHAR(256),
    [table_name] NVARCHAR(256),
    [index_name] NVARCHAR(256),
    [index_type] NVARCHAR(50),
    [row_count]  BIGINT,
    [size_mb]    DECIMAL(36, 2),
    [used_mb]    DECIMAL(36, 2),
    [unused_mb]  DECIMAL(36, 2)
)
 
INSERT INTO #tamanho_indices
EXEC sys.[sp_MSforeachdb] '
IF (''?'' NOT IN (''model'', ''master'', ''tempdb'', ''msdb''))
BEGIN
 
    SELECT TOP(100)
        ''?'' AS [database],
        s.[name] AS [schema],
        t.[name] AS [table_name],
        i.[name] AS [index_name],
        i.[type_desc],
        p.[rows] AS [row_count],
        CAST(ROUND(((SUM(a.total_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS [size_mb],
        CAST(ROUND(((SUM(a.used_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS [used_mb], 
        CAST(ROUND(((SUM(a.total_pages) - SUM(a.used_pages)) * 8) / 1024.00, 2) AS NUMERIC(36, 2)) AS [unused_mb]
    FROM
        [?].sys.tables t
        JOIN [?].sys.indexes i ON t.[object_id] = i.[object_id]
        JOIN [?].sys.partitions p ON i.[object_id] = p.[object_id] AND i.index_id = p.index_id
        JOIN [?].sys.allocation_units a ON p.[partition_id] = a.container_id
        LEFT JOIN [?].sys.schemas s ON t.[schema_id] = s.[schema_id]
    WHERE 
        t.is_ms_shipped = 0
        AND i.[object_id] > 255 
    GROUP BY
        t.[name], 
        s.[name],
        i.[name],
        i.[type_desc],
        p.[rows]
    ORDER BY
        7 DESC
        
END'
 
SELECT TOP 100 * 
FROM [#tamanho_indices]
ORDER BY [size_mb] DESC