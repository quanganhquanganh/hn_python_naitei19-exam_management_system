resource "aws_ses_domain_identity" "identity" {
  domain = "${var.app_name}.${var.hosted_zone}"
}

resource "aws_route53_record" "domain_verification" {
  zone_id = data.aws_route53_zone.zone.zone_id
  name    = aws_ses_domain_identity.identity.domain
  type    = "TXT"
  ttl     = "600"

  records = [
    aws_ses_domain_identity.identity.verification_token
  ]
}
