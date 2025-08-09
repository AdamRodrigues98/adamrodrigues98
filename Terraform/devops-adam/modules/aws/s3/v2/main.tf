resource "aws_s3_bucket" "this" {
  bucket = "${var.organization_account_name}-${var.bucket}"
}

resource "aws_s3_bucket_versioning" "this" {
  count  = var.enable_versioning ? 1 : 0
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
  bucket = aws_s3_bucket.this.bucket
  rule {
    object_ownership = var.object_ownership
  }
}

resource "aws_s3_bucket_acl" "this" {
  bucket = aws_s3_bucket.this.id
  acl    = var.acl
  count = var.object_ownership != "BucketOwnerEnforced" ? 1 : 0
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.bucket

  block_public_acls       = var.block_public_acls
  block_public_policy     = var.block_public_policy
  ignore_public_acls      = var.ignore_public_acls
  restrict_public_buckets = var.restrict_public_buckets
}
