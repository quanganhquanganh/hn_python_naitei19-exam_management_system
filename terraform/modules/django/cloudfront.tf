# Attach CloudFront to the API Gateway
# xyz.cloudfront.net -> xyz.execute-api.us-east-1.amazonaws.com/0/
# xyz.cloudfront.net/[dist_manifest_key] -> xyz.execute-api.us-east-1.amazonaws.com/[dist_manifest_key]

resource "aws_cloudfront_distribution" "main" {
  count = var.create_lambda_function ? 1 : 0

  origin {
    domain_name = "${aws_apigatewayv2_api.lambda[0].id}.execute-api.${var.aws_region}.amazonaws.com"
    origin_id   = "django"
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "CloudFront distribution for ${var.lambda_function_name}"
  default_root_object = "0"

  aliases = [
    local.domain_name,
  ]

  default_cache_behavior {
    target_origin_id       = "django"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    forwarded_values {
      query_string = false
      headers = ["Accept", "Origin", "Referer", "Authorization", "Content-Type"]
			cookies {
				forward = "whitelist"
          whitelisted_names = [
            "csrftoken",
            "_app_session",
            "_app_session.sig",
            "sessionid",
            "sessionid.sig",
            "messages",
            "messages.sig",
            "django_language",
            "django_language.sig",
          ]
			}
    }
    compress = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.default.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1"
  }

  wait_for_deployment = false
}
