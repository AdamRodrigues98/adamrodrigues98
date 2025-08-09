USE [StackOverflow2013];


DECLARE @TableName NVARCHAR(128) = 'Votes';

SELECT 
    i.name AS NomeIndice,
    i.type_desc AS TipoIndice,
    c.name AS NomeColuna,
    ic.key_ordinal AS OrdemColuna
FROM 
    sys.indexes i
INNER JOIN 
    sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
INNER JOIN 
    sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE 
    i.object_id = OBJECT_ID(@TableName);

GO
sp_helpindex Votes