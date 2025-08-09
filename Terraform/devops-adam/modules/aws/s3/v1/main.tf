resource "aws_s3_bucket" "this" {
  bucket = var.bucket
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.bucket
  versioning_configuration {
    status = var.bucket_versioning
  }
}

resource "aws_s3_bucket_accelerate_configuration" "this" {
  bucket = aws_s3_bucket.this.bucket
  status = var.transfer_accelerate
  count  = var.enable_accelerate ? 1 : 0
}

resource "aws_s3_bucket_ownership_controls" "this" {
  count = var.create_ownership_controls ? 1 : 0
  
  bucket = aws_s3_bucket.this.bucket
  rule {
    object_ownership = var.object_ownership
  }

  lifecycle {
    ignore_changes = [
      rule,
    ]
  }

}

resource "aws_s3_bucket_acl" "this" {
  bucket = aws_s3_bucket.this.id
  acl    = var.acl
}
resource "aws_s3_bucket_public_access_block" "this" {
  bucket = var.bucket

  block_public_acls       = var.block_public_acls
  block_public_policy     = var.block_public_policy
  ignore_public_acls      = var.ignore_public_acls
  restrict_public_buckets = var.restrict_public_buckets
}