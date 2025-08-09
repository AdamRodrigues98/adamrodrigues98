Use StackOverflow2013
go

Declare @tabela varchar(500) = 'Users'

SELECT 
     COLUMN_NAME	AS	[Coluna]					
    ,DATA_TYPE  AS [Tipo]
    ,CHARACTER_MAXIMUM_LENGTH  AS [Tamanho Maximo]
    ,NUMERIC_PRECISION 
    ,NUMERIC_SCALE
FROM 
    INFORMATION_SCHEMA.COLUMNS
WHERE 
    TABLE_NAME = @tabela