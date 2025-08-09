locals {
  audit_users = [
        "adam.rodrigues"
  ]
}

resource "aws_db_option_group" "mysql_audit_plugin" {
  name                     = "audit-mariadb-plugin"  
  engine_name              = "mysql"
  major_engine_version     = "8.4"
  option_group_description = "Option Group for Master MySQL 8.4 managed by Terraform"

  option {
    option_name = "MARIADB_AUDIT_PLUGIN"

    option_settings {
      name  = "SERVER_AUDIT_EVENTS"
      value = "QUERY_DDL,QUERY_DCL,QUERY_DML_NO_SELECT"
    }

    option_settings {
      name  = "SERVER_AUDIT_FILE_ROTATE_SIZE"
      value = "104857600"   
    }

    option_settings {
      name  = "SERVER_AUDIT_FILE_ROTATIONS"
      value = "5"
    }

    option_settings {
      name  = "SERVER_AUDIT_INCL_USERS"
      value = join(",", local.audit_users)
    }

    option_settings {
      name  = "SERVER_AUDIT_QUERY_LOG_LIMIT"
      value = "4096"
    }
  }

  tags = {
    Environment = local.account_name
  }

}


