resource "aws_db_instance" "rds" {
  allocated_storage                     = var.allocated_storage
  max_allocated_storage                 = var.max_allocated_storage
  identifier                            = var.identifier
  engine                                = var.engine
  engine_version                        = var.engine_version
  instance_class                        = var.instance_class
  db_name                               = var.db_name
  username                              = var.username
  password                              = var.password
  vpc_security_group_ids                = [var.vpc_security_group_ids]
  db_subnet_group_name                  = var.db_subnet_group_name
  publicly_accessible                   = var.publicly_accessible
  multi_az                              = var.multi_az
  storage_encrypted                     = var.storage_encrypted
  kms_key_id                            = aws_kms_key.rds.arn
  storage_type                          = var.storage_type
  iops                                  = var.iops
  skip_final_snapshot                   = var.skip_final_snapshot
  deletion_protection                   = var.deletion_protection
  backup_retention_period               = var.backup_retention_period
  parameter_group_name                  = var.parameter_group_name
  copy_tags_to_snapshot                 = true
  apply_immediately                     = var.apply_immediately
  auto_minor_version_upgrade            = var.auto_minor_version_upgrade
  allow_major_version_upgrade           = var.allow_major_version_upgrade
  performance_insights_enabled          = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_enabled ? var.performance_insights_retention_period : null

  tags = {
    Environment = "${var.environment}"
    Tenant = var.organization_name
    Project     = "${var.project}"
    automation  = "${var.automation}"
  }

}

resource "aws_kms_key" "rds" {
  description             = "KMS key for DB ${var.identifier} encryption"
  deletion_window_in_days = var.kms_deletion_window_in_days
  enable_key_rotation     = var.enable_key_rotation

  tags = {
    Name        = "${var.identifier}"
    Environment = "${var.environment}"
  }
}
