output "this_createdb" {
  description = "Result of createdb Lambda execution"
  value       = "${data.aws_lambda_invocation.createdb.*.result}"
}

output "this_migrate" {
  description = "Result of migration Lambda execution"
  value       = "${data.aws_lambda_invocation.migrate.*.result}"
}

output "staticfiles_access_key_id" {
  description = "The access key ID with access to staticfiles s3 bucket."
  value       = module.s3_user_staticfiles.access_key_id
}

output "staticfiles_secret_access_key" {
  description = "The secret access key with access to staticfiles s3 bucket. Note that this will be written to the state file."
  value       = module.s3_user_staticfiles.secret_access_key
}

output "staticfiles_bucket" {
  description = "Name of staticfiles S3 bucket."
  value       = module.staticfiles.s3_bucket
}

output "dist_access_key_id" {
  description = "The access key ID with access to dist s3 bucket."
  value       = module.s3_bucket_app.access_key_id
}

output "dist_secret_access_key" {
  description = "The secret access key with access to dist s3 bucket. Note that this will be written to the state file."
  value       = module.s3_bucket_app.secret_access_key
}

output "dist_bucket" {
  description = "Name of dist S3 bucket."
  value       = module.s3_bucket_app.bucket_id
}
