locals {
  s3 = { 
    lakehouse = {
      acl                     = "private"
      block_public_acls       = true
      block_public_policy     = true
      ignore_public_acls      = true
      restrict_public_buckets = true
      enable_accelerate       = false
      enable_versioning       = false
    }

   }

}

module "aws-s3" {
  source                    = "../../../../modules/aws/s3/v2"
  for_each                  = local.s3
  bucket                    = each.key
  acl                       = each.value.acl
  block_public_acls         = each.value.block_public_acls
  block_public_policy       = each.value.block_public_policy
  ignore_public_acls        = each.value.ignore_public_acls
  restrict_public_buckets   = each.value.restrict_public_buckets
  enable_accelerate         = each.value.enable_accelerate
  enable_versioning         = each.value.enable_versioning
  organization_account_name = local.organization_account_name
}

resource "aws_s3_bucket_lifecycle_configuration" "bp_log_lifecycle_rule" {
  bucket = module.aws-s3["bp-log"].id

  rule {
    id     = "expire-objects-bp-log"
    status = "Enabled"
    expiration {
      days                         = 30
      expired_object_delete_marker = false
    }
  }
}