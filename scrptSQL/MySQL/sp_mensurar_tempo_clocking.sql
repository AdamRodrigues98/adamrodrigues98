/****************************************
   criação da tabela table_name_temp
 ****************************************/
CREATE TABLE table_name_temp LIKE table_name

/****************************************
 	Criar tabela para guardar Duração
 ****************************************/
CREATE TABLE IF NOT EXISTS dba.table_name_time_measurement(
    id INT AUTO_INCREMENT PRIMARY KEY,
    start_time DATETIME,
    end_time DATETIME
);

/****************************************
 	select validar informação
 ****************************************/
SELECT  start_time 
	 ,end_time 
	 ,TIMEDIFF(end_time, start_time) AS duration
FROM dba.table_name_time_measurement;


/****************************************
 	Proc carga table_name_temp
 ****************************************/
DELIMITER $$

CREATE PROCEDURE MeasureInsertTime()
BEGIN

    START TRANSACTION;

    INSERT INTO dba.table_name_time_measurement (start_time)
    VALUES (NOW());

    INSERT INTO db_name.table_name_temp
    SELECT *
    FROM db_name.table_name
    WHERE table_name_date >= CURDATE() - INTERVAL 6 MONTH
      AND table_name_date < CURDATE();

    UPDATE dba.table_name_time_measurement
    SET end_time = NOW()
    WHERE id = (SELECT MAX(id) FROM dba.table_name_time_measurement);


    COMMIT;
END$$

DELIMITER ;

/****************************************
   Chamar a procedure
 ****************************************/
CALL sp_mensure_time_table_name()



/****************************************
 	Proc 2.0 carga table_name_temp
 ****************************************/
DELIMITER $$

CREATE PROCEDURE sp_mensure_time_table_name()
BEGIN
    DECLARE last_id INT;


    INSERT INTO dba.table_name_time_measurement (start_time)
    VALUES (NOW());


    SET last_id = LAST_INSERT_ID();


    INSERT INTO db_name.table_name_temp
    SELECT *
    FROM db_name.table_name
    WHERE table_name_date >= CURDATE() - INTERVAL 6 MONTH 
      AND table_name_date < CURDATE();


    UPDATE dba.table_name_time_measurement
    SET end_time = NOW()
    WHERE id = last_id;

END$$

DELIMITER ;


DROP PROCEDURE





