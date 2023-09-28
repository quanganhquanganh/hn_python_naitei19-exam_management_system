locals {
  domain_name = "${var.app_name}.${var.hosted_zone}"
}

data "aws_route53_zone" "domain_name" {
  name         = var.hosted_zone
  private_zone = false
}

resource "aws_acm_certificate" "default" {
  domain_name               = var.hosted_zone
  subject_alternative_names = ["*.${var.hosted_zone}"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }

}

# Update the Route53 Records with the Certificate details for validation
resource "aws_route53_record" "default" {
  for_each = {
    for dvo in aws_acm_certificate.default.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.domain_name.zone_id

}

# Generate Certificate Validation
resource "aws_acm_certificate_validation" "default" {
  certificate_arn         = aws_acm_certificate.default.arn
  validation_record_fqdns = [for record in aws_route53_record.default : record.fqdn]
}

resource "aws_route53_record" "route53_record" {
  depends_on = [
    aws_cloudfront_distribution.main,
  ]

  zone_id = data.aws_route53_zone.domain_name.zone_id
  name    = local.domain_name
  type    = "A"

  alias {
    name    = aws_cloudfront_distribution.main[0].domain_name
    zone_id = "Z2FDTNDATAQYW2"

    //HardCoded value for CloudFront
    evaluate_target_health = false
  }
}
