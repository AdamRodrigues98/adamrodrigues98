resource "aws_db_parameter_group" "mysql_84" {
  name   = "db-prod-84"
  description = "Parameter Group for Master 8.4 Managed by Terraform"
  family = "mysql8.4"

  parameter {
    name = "binlog_format"
    value = "ROW"
  }

  parameter {
    name = "character_set_client"
    value = "latin1"
  }

  parameter {
    name = "character_set_connection"
    value = "latin1"
  }

  parameter {
    name = "character_set_database"
    value = "latin1"
  }

  parameter {
    name = "character_set_server"
    value = "latin1"
  }

  parameter {
    name = "collation_connection"
    value = "latin1_swedish_ci"
  }

  parameter {
    name = "collation_server"
    value = "latin1_swedish_ci"
  }

  parameter {
    name  = "event_scheduler"
    value = "ON"
  }

  parameter {
    name = "innodb_buffer_pool_size"
    value = "{DBInstanceClassMemory*3/4}"
  }

  parameter {
    name = "innodb_io_capacity"
    value = "1000"
  }

  parameter {
    name = "innodb_io_capacity_max"
    value = "3000"
  }

  parameter {
    name = "innodb_log_buffer_size"
    value = "39452672"
  }

  parameter {
    name = "innodb_redo_log_capacity"
    value = "2147483648"
  }

  parameter {
    name = "innodb_stats_persistent_sample_pages"
    value = "128"
  }

  parameter {
    name = "innodb_use_fdatasync"
    value = "1"
  }

  parameter {
    name = "key_buffer_size"
    value = "16777216"
  }

    parameter {
    name = "log_output"
    value = "TABLE"
  }

  parameter {
    name = "max_allowed_packet"
    value = "1073741824"
  }

  parameter {
    name = "max_connect_errors"
    value = "10000000000"
  }    

  parameter {
    name = "max_digest_length"
    value = "4096"
    apply_method = "pending-reboot"
  }

  parameter {
    name = "performance_schema"
    value = "1"
    apply_method = "pending-reboot"
  }

  parameter {
    name = "performance_schema_max_digest_length"
    value = "4096"
    apply_method = "pending-reboot"
  }

  parameter {
    name = "performance_schema_max_sql_text_length"
    value = "4096"
    apply_method = "pending-reboot"
  }

  parameter {
    name = "replicate-ignore-table"
    value = "table.temp_clocking_summary,dba.global_status"
  }  

  parameter {
    name = "table_open_cache"
    value = "8000"
  }  

  parameter {
    name = "temptable_max_ram"
    value = "1073741824"
  }  

  parameter {
    name = "thread_stack"
    value = "262144"
    apply_method = "pending-reboot"
  }    

  tags = {
    Environment = local.account_name
  }

}

resource "aws_db_parameter_group" "read_mysql_84" {
  name   = "db-read-84"
  description = "Parameter Group for Read 8.4 Managed by Terraform"
  family = "mysql8.4"

  parameter {
    name = "binlog_format"
    value = "ROW"
  }

  parameter {
    name = "character_set_client"
    value = "latin1"
  }

  parameter {
    name = "character_set_connection"
    value = "latin1"
  }

  parameter {
    name = "character_set_database"
    value = "latin1"
  }

  parameter {
    name = "character_set_server"
    value = "latin1"
  }

  parameter {
    name = "character_set_results"
    value = "latin1"
  }
  
  parameter {
    name = "collation_connection"
    value = "latin1_swedish_ci"
  }

  parameter {
    name = "collation_server"
    value = "latin1_swedish_ci"
  }

  parameter {
    name  = "event_scheduler"
    value = "OFF"
  }

  parameter {
    name = "innodb_buffer_pool_size"
    value = "{DBInstanceClassMemory*3/4}"
  }

  parameter {
    name = "innodb_io_capacity"
    value = "1000"
  }

  parameter {
    name = "innodb_io_capacity_max"
    value = "3000"
  }

  parameter {
    name = "innodb_log_buffer_size"
    value = "39452672"
  }

  parameter {
    name = "innodb_deadlock_detect"
    value = "0"
  }

  parameter {
    name = "innodb_print_all_deadlocks"
    value = "0"
  }

  parameter {
    name = "innodb_parallel_read_threads"
    value = "8"
  }

  parameter {
    name = "innodb_redo_log_capacity"
    value = "2147483648"
  }

  parameter {
    name = "innodb_stats_persistent_sample_pages"
    value = "128"
  }

  parameter {
    name = "innodb_use_fdatasync"
    value = "1"
  }

  parameter {
    name = "key_buffer_size"
    value = "16777216"
  }

    parameter {
    name = "log_output"
    value = "TABLE"
  }

  parameter {
    name = "max_allowed_packet"
    value = "1073741824"
  }

  parameter {
    name = "max_digest_length"
    value = "4096"
    apply_method = "pending-reboot"
  }

  parameter {
    name = "performance_schema"
    value = "1"
    apply_method = "pending-reboot"
  }

  parameter {
    name = "performance_schema_max_digest_length"
    value = "4096"
    apply_method = "pending-reboot"
  }

  parameter {
    name = "performance_schema_max_sql_text_length"
    value = "4096"
    apply_method = "pending-reboot"
  }

  parameter {
    name = "replicate-ignore-table"
    value = "table.temp_clocking_summary,dba.global_status"
  }  

  parameter {
    name = "table_open_cache"
    value = "8000"
  }  

  parameter {
    name = "temptable_max_ram"
    value = "1073741824"
  }  

  parameter {
    name = "thread_stack"
    value = "262144"
    apply_method = "pending-reboot"
  }    

  tags = {
    Environment = local.account_name
  }
  
}

