module "django" {
  source                 = "./modules/django"
  lambda_function_name   = "exammanagement"
  lambda_handler         = "exammanagement.lgi.application"
  stage                  = "dev"
  aws_region             = var.aws_region
  app_name               = var.app_name
  hosted_zone            = var.hosted_zone
  create_lambda_function = true
  django_secret_key      = var.django_secret_key
  admin_email            = var.admin_email
  admin_password         = var.admin_password
  default_from_email     = var.default_from_email
}
