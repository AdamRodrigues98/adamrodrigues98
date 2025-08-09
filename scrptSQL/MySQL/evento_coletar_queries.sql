DELIMITER $$

CREATE PROCEDURE `dba`.`sp_collect_querys`()
BEGIN
    INSERT INTO long_queries (user, query, time, host, DB)
    SELECT user, info, time, host, DB FROM INFORMATION_SCHEMA.PROCESSLIST 
    WHERE info IS NOT NULL 
    AND time < 60
    AND user NOT IN ('adam.rodrigues', 'rdsadmin', 'root'); 
END $$

DELIMITER ;


CALL sp_collect_querys()


CREATE EVENT IF NOT EXISTS colect_all_queries
ON SCHEDULE 
    EVERY 1 SECOND
STARTS CURRENT_TIMESTAMP
DO
    CALL dba.sp_collect_querys();

show events

select * from long_queries

DROP EVENT colect_all_queries