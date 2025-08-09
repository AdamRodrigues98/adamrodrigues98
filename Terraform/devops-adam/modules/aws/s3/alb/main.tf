resource "aws_s3_bucket" "alb-logs" {
  bucket = var.bucket
}

resource "aws_s3_bucket_versioning" "alb-logs" {
  bucket = aws_s3_bucket.alb-logs.bucket
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_ownership_controls" "alb-logs" {
  bucket = var.bucket
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "alb-logs" {
  depends_on = [aws_s3_bucket_ownership_controls.alb-logs]
  bucket = aws_s3_bucket.alb-logs.id
  acl    = var.acl
}
resource "aws_s3_bucket_public_access_block" "alb-logs" {
  bucket = var.bucket

  block_public_acls       = var.block_public_acls
  block_public_policy     = var.block_public_policy
  ignore_public_acls      = var.ignore_public_acls
  restrict_public_buckets = var.restrict_public_buckets
}