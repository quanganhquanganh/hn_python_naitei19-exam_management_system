data "aws_iam_policy_document" "lambda" {
  statement {
    effect = "Allow"
    actions = [
      "sts:AssumeRole",
    ]

    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.lambda_function_name}_${var.stage}_role"
  assume_role_policy = data.aws_iam_policy_document.lambda.json
}

module "lambda_security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name = "lambda_sg"
  vpc_id = module.vpc.vpc_id

  computed_egress_with_source_security_group_id = [
    {
      rule                     = "mysql-tcp"
      source_security_group_id = module.mysql_security_group.security_group_id
    }
  ]
  number_of_computed_egress_with_source_security_group_id = 1
}

/* Define IAM permissions for the Lambda functions. */

data "aws_iam_policy_document" "lambda_basic_execution" {
  statement {
    sid = "AWSLambdaBasicExecutionRole"

    actions = [
      # AWSLambdaVPCAccessExecutionRole
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface",
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "lambda_basic_execution" {
  name   = "${var.lambda_function_name}_${var.stage}_policy"
  policy = data.aws_iam_policy_document.lambda_basic_execution.json
}

resource "aws_iam_role_policy_attachment" "attach_base_policy" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda_basic_execution.arn
}

data "aws_iam_policy_document" "ses" {
  count = var.enable_ses_endpoint ? 1 : 0
  statement {
    actions   = ["ses:SendRawEmail"]
    resources = ["*"]
    effect    = "Allow"
  }
}

resource "aws_iam_user" "ses" {
  count = var.enable_ses_endpoint ? 1 : 0
  name          = "ses"
}

# Defines a user that should be able to send send emails
resource "aws_iam_user_policy" "ses" {
  count = var.enable_ses_endpoint ? 1 : 0
  name   = aws_iam_user.ses[0].name
  user   = aws_iam_user.ses[0].name
  policy = data.aws_iam_policy_document.ses[0].json
}

# Generate API credentials
resource "aws_iam_access_key" "ses" {
  count = var.enable_ses_endpoint ? 1 : 0
  user  = aws_iam_user.ses[0].name
}

locals {
  ses_config = {
    enabled = {
      ENABLE_SMTP_EMAIL_BACKEND = "True"
      EMAIL_HOST = "email-smtp.${var.aws_region}.amazonaws.com"
      EMAIL_PORT = "587"
      EMAIL_HOST_USER = var.enable_ses_endpoint ? aws_iam_access_key.ses[0].id : ""
      EMAIL_HOST_PASSWORD = var.enable_ses_endpoint ? aws_iam_access_key.ses[0].ses_smtp_password_v4 : ""
      EMAIL_USE_TLS = "True"
      DEFAULT_FROM_EMAIL  = "noreply@${var.app_name}.${var.hosted_zone}"
    }
    disabled = {}
  }
}

resource "aws_lambda_function" "function" {
  count = var.create_lambda_function ? length(keys(local.dist_manifest)) : 0

  function_name = "${var.lambda_function_name}_${keys(local.dist_manifest)[count.index]}"
  handler = var.lambda_handler
  role    = aws_iam_role.lambda.arn
  runtime = var.lambda_runtime

  memory_size = 256
  timeout = 30

  s3_bucket = module.s3_bucket_app.bucket_id
  s3_key = values(local.dist_manifest)[count.index].file
  source_code_hash = values(local.dist_manifest)[count.index].filebase64sha256
  publish = true

  vpc_config {
    subnet_ids = module.vpc.private_subnets
    security_group_ids = [data.aws_security_group.default.id, module.lambda_security_group.security_group_id, module.mysql_security_group.security_group_id]
  }

  environment {
    variables = merge(
      {
        DJANGO_SECRET_KEY = var.django_secret_key
        DJANGO_ALLOWED_HOSTS = "*"
        DJANGO_DEBUG = "False"
        DB_USER = module.db.db_instance_username
        DB_PASSWORD = random_password.password.result
        DB_HOST = module.db.db_instance_address
        DB_PORT = module.db.db_instance_port
        DB_NAME = "${var.lambda_function_name}_${keys(local.dist_manifest)[count.index]}"
        FORCE_SCRIPT_NAME = "/${keys(local.dist_manifest)[count.index]}/"
        DJANGO_SUPERUSER_USERNAME="admin"
        DJANGO_SUPERUSER_EMAIL=var.admin_email
        DJANGO_SUPERUSER_PASSWORD=var.admin_password
        ENABLE_MANIFEST_STORAGE = "True"
        AWS_ACCESS_KEY_ID_UPLOAD = module.s3_user_upload.access_key_id
        AWS_SECRET_ACCESS_KEY_UPLOAD = module.s3_user_upload.secret_access_key
        AWS_REGION_UPLOAD = var.aws_region
        AWS_S3_BUCKET_NAME_UPLOAD = module.s3_bucket_upload.bucket_id
        STATIC_URL = "https://${module.staticfiles.cf_domain_name}/${keys(local.dist_manifest)[count.index]}/"
        STATIC_ROOT = "/var/task/"
        LOGGING_LEVEL = "DEBUG"
        CSRF_TRUSTED_ORIGINS = "https://${var.app_name}.${var.hosted_zone}"
      },
      local.ses_config[var.enable_ses_endpoint == true ? "enabled" : "disabled"]
    )
  }
}

data "aws_lambda_invocation" "createdb" {
  count = length(keys(local.dist_manifest))
  function_name = "${var.lambda_function_name}_${keys(local.dist_manifest)[count.index]}"
  depends_on = [aws_lambda_function.function]

  input = jsonencode(
    {
      manage = ["createdb", "${var.lambda_function_name}_${keys(local.dist_manifest)[count.index]}", "--exist_ok"]
    }
  )
}

data "aws_lambda_invocation" "migrate" {
  count = length(keys(local.dist_manifest))
  function_name = "${var.lambda_function_name}_${keys(local.dist_manifest)[count.index]}"
  depends_on = [
    aws_lambda_function.function,
    data.aws_lambda_invocation.createdb
  ]

  input = jsonencode(
    {
      manage = ["migrate", "--noinput"]
    }
  )
}

data "aws_lambda_invocation" "createsuperuser" {
  count = length(keys(local.dist_manifest))
  function_name = "${var.lambda_function_name}_${keys(local.dist_manifest)[count.index]}"
  depends_on = [
    aws_lambda_function.function,
    data.aws_lambda_invocation.migrate
  ]

  input = jsonencode(
    {
      manage = ["createsuperuser_or_update", "--from-env"]
    }
  )
}

resource "aws_lambda_permission" "apigwv2" {
  count = var.create_lambda_function ? length(aws_lambda_function.function) : 0

  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.function[count.index].function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_apigatewayv2_api.lambda[0].execution_arn}/*/*"
}

resource "aws_lambda_provisioned_concurrency_config" "main" {
  count = var.create_lambda_provisioned_concurrency == "true" ? 1 : 0

  function_name                     = aws_lambda_function.function[0].function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.function[0].version
}
