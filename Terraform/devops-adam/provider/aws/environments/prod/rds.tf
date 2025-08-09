resource "random_password" "rds-passwords" {
  count            = 2
  length           = 20
  override_special = "!#$%^&*()-_=+[]{}<>:?"
  min_numeric      = 4
  min_special      = 6
  min_upper        = 6
}

resource "aws_db_subnet_group" "cluster_vpc_subnet_group" {
  name       = "rds-subnet-group"
  subnet_ids = data.aws_subnets.main-private-vpc.ids

  tags = {
    Environment = local.account_name
    Tenant      = local.organization_name
  }
}

resource "aws_db_subnet_group" "cluster_vpc_subnet_group-prod" {
  name       = "rds-subnet-group-prod"
  subnet_ids = module.vpc_prod.private_subnets

  tags = {
    Environment = local.account_name
    Tenant      = local.organization_name
    Application = "prod"
  }
}

resource "aws_ssm_parameter" "rds-adam-prod" {
  name  = "rds-adam-prod"
  type  = "SecureString"
  value = random_password.rds-passwords[0].result
}

resource "aws_ssm_parameter" "rds-master-prod" {
  name  = "rds-master-prod"
  type  = "SecureString"
  value = random_password.rds-passwords[1].result
}

module "rds-master-prod-master" {
  source                      = "../../../../modules/aws/rds/v1"
  environment                 = local.account_name
  organization_name           = local.organization_name
  allocated_storage           = 100
  max_allocated_storage       = 1000
  identifier                  = "master"
  engine                      = "mysql"
  engine_version              = "8.4.5"
  instance_class              = "db.m8g.24xlarge"
  db_name                     = "adam"
  username                    = "root"
  password                    = aws_ssm_parameter.rds-master-prod.value
  storage_type                = "gp3"
  iops                        = null
  vpc_security_group_ids      = aws_security_group.this_rds_prod_prod.id
  db_subnet_group_name        = aws_db_subnet_group.cluster_vpc_subnet_group-prod.name
  publicly_accessible         = local.rds.publicly_accessible
  deletion_protection         = local.rds.deletion_protection
  multi_az                    = false
  storage_encrypted           = local.rds.storage_encrypted
  kms_deletion_window_in_days = local.kms.kms_deletion_window_in_days
  enable_key_rotation         = local.kms.enable_key_rotation
  backup_retention_period     = local.rds.backup_retention_period
  apply_immediately           = local.rds.apply_immediately
  parameter_group_name        = aws_db_parameter_group.master-prod-80.name
}