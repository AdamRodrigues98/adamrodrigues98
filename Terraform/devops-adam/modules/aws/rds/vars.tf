variable "allocated_storage" {
  description = "Initial allocated storage"
}

variable "max_allocated_storage" {
  description = "Max storage allowed"
}

variable "identifier" {
  description = "Name of RDS instance"
}

variable "engine" {
  description = "Engine to be used[Postgres]"
}

variable "engine_version" {}

variable "instance_class" {
  description = "Instance type and size to be used"
}

variable "db_name" {
  description = "Name of the Database"
}

variable "username" {
  description = "Principal database username"
}

variable "password" {
  description = "Principal user password"
}

variable "publicly_accessible" {
  description = "If true, will require a db subnet group with public subnets"
  default     = false
}

variable "multi_az" {
  default = true
}

variable "storage_encrypted" {
  type    = bool
  default = true
}

variable "storage_type" {}

variable "skip_final_snapshot" {
  description = "Skip final snapshot when deleting RDS instance"
  type        = bool
  default     = true
}

variable "deletion_protection" {
  type = bool
}

variable "kms_deletion_window_in_days" {
  description = "KMS key deletion time"
}

variable "enable_key_rotation" {
  description = "Enable KMS key rotation. Valid values: true or false"
  type        = bool
}

variable "environment" {}
variable "db_subnet_group_name" {}
variable "vpc_security_group_ids" {}
variable "backup_retention_period" {}
variable "organization_name" {
  default = null
}
variable "project" {
  type    = string
  default = null
}
variable "automation" {
  type    = string
  default = null
}
variable "apply_immediately" {
  type = bool
}
variable iops {
  type        = string
  default     = "1000"
}

variable auto_minor_version_upgrade {
  type        = bool
  default     = false
}

variable "allow_major_version_upgrade" {
  type        = bool
  default     = false
}

variable "performance_insights_enabled" {
  description = "Enable Performance Insights RDS"
  type        = bool
  default     = false
}

variable "performance_insights_retention_period" {
  description = "Performance Insights retention period (in days)"
  type        = number
  default     = 7
}
