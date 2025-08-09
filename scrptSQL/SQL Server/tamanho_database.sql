/*********************************
 	  Tamanho Por Database
 ********************************/
WITH fs AS
(
    SELECT 
        database_id, 
        type, 
        size * 8.0 / 1024 AS size
    FROM 
        sys.master_files
)
SELECT
    db.name AS NomeDoBanco,
    (SELECT SUM(size) FROM fs WHERE type = 0 AND fs.database_id = db.database_id) AS DataFileSizeMB, 
    (SELECT SUM(size) FROM fs WHERE type = 1 AND fs.database_id = db.database_id) AS LogFileSizeMB,  
    (
        (SELECT SUM(size) FROM fs WHERE type = 0 AND fs.database_id = db.database_id) + 
        (SELECT SUM(size) FROM fs WHERE type = 1 AND fs.database_id = db.database_id)
    ) AS Total 
FROM 
    sys.databases db;

/*********************************
 		Tamanho Total
 ********************************/
   
WITH fs AS
(
    SELECT 
        database_id, 
        type, 
        size * 8.0 / 1024 AS size -- Converte o tamanho de páginas para MB
    FROM 
        sys.master_files
),
DatabaseSizes AS
(
    SELECT
        db.database_id,
        SUM(CASE WHEN fs.type = 0 THEN fs.size ELSE 0 END) AS DataFileSizeMB, -- Tamanho dos arquivos de dados
        SUM(CASE WHEN fs.type = 1 THEN fs.size ELSE 0 END) AS LogFileSizeMB   -- Tamanho dos arquivos de log
    FROM 
        sys.databases db
    LEFT JOIN 
        fs ON fs.database_id = db.database_id
    GROUP BY 
        db.database_id
)
SELECT
    SUM(DataFileSizeMB) AS TotalDataFileSizeMB, -- Soma total dos tamanhos dos arquivos de dados
    SUM(LogFileSizeMB) AS TotalLogFileSizeMB,   -- Soma total dos tamanhos dos arquivos de log
    SUM(DataFileSizeMB + LogFileSizeMB) AS TotalFileSizeMB 
FROM 
    DatabaseSizes;

   


