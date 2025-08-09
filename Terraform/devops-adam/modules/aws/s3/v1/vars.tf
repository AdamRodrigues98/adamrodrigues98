variable bucket {}
variable acl {
  default     = "private"
}
variable block_public_acls {
    default = true
}
variable block_public_policy {
    default = true
}
variable ignore_public_acls {
    default = true
}
variable restrict_public_buckets {
    default = true
}
variable transfer_accelerate {
    default = "Enabled"
}
variable bucket_versioning {
    default = "Enabled"
}
variable enable_accelerate {
  default     = "true"
}
variable object_ownership {
    default = "BucketOwnerEnforced"
}

variable "create_ownership_controls" {
    default = "false"
}