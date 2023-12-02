data "aws_caller_identity" "current" {}

resource "aws_apigatewayv2_api" "lambda" {
  count = var.create_lambda_function ? 1 : 0
  name          = "${var.lambda_function_name}_${var.stage}_gatewayv2"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda" {
  count = var.create_lambda_function ? 1 : 0
  api_id           = aws_apigatewayv2_api.lambda[0].id
  integration_type = "AWS_PROXY"

  connection_type           = "INTERNET"
  # https://github.com/amazon-archives/aws-apigateway-importer/issues/9#issuecomment-129651005
  integration_method        = "POST"
  integration_uri           = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:$${stageVariables.lambdaFunctionName}/invocations"
  payload_format_version    = "2.0"
}

resource "aws_apigatewayv2_route" "lambda" {
  count = var.create_lambda_function ? 1 : 0
  api_id    = aws_apigatewayv2_api.lambda[0].id
  route_key = "$default"

  target = "integrations/${aws_apigatewayv2_integration.lambda[0].id}"
}

resource "aws_apigatewayv2_stage" "lambda" {
  count = var.create_lambda_function ? length(keys(local.dist_manifest)) : 0
  api_id = aws_apigatewayv2_api.lambda[0].id
  name   = keys(local.dist_manifest)[count.index]
  auto_deploy = true
  stage_variables = {
    lambdaFunctionName = "${var.lambda_function_name}_${keys(local.dist_manifest)[count.index]}"
  }
}

resource "aws_apigatewayv2_domain_name" "lambda" {
  count = var.create_lambda_function ? 1 : 0
  domain_name = local.domain_name
  domain_name_configuration {
    certificate_arn = aws_acm_certificate.default.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_apigatewayv2_api_mapping" "lambda" {
  count = var.create_lambda_function ? 1 : 0
  api_id      = aws_apigatewayv2_api.lambda[0].id
  domain_name = aws_apigatewayv2_domain_name.lambda[0].id
  stage       = aws_apigatewayv2_stage.lambda[0].id
}

resource "aws_apigatewayv2_api_mapping" "lambda_default" {
  count = var.create_lambda_function ? length(keys(local.dist_manifest)) - 1 : 0
  api_id      = aws_apigatewayv2_api.lambda[0].id
  domain_name = aws_apigatewayv2_domain_name.lambda[0].id
  stage       = aws_apigatewayv2_stage.lambda[count.index + 1].id
  api_mapping_key = "${keys(local.dist_manifest)[count.index + 1]}"
}

resource "aws_apigatewayv2_deployment" "lambda" {
  count = var.create_lambda_function ? 1 : 0
  api_id      = aws_apigatewayv2_api.lambda[0].id

  lifecycle {
    create_before_destroy = true
  }
}
