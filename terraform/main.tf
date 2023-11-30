terraform {
  backend "remote" {
    organization = "exammanagement"

    workspaces {
      name = "prod"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
