#########################
# Database security group
#########################
module "mysql_security_group" {
  source  = "terraform-aws-modules/security-group/aws//modules/mysql"
  version = "~> 5.0"

  name = "database_sg"
  vpc_id = module.vpc.vpc_id

  ingress_cidr_blocks = ["0.0.0.0/0"]
}

####################################
# Variables common to both instnaces
####################################
locals {
  port              = "3306"
  engine            = "mysql"
  engine_version    = "8.0.34"
  instance_class    = "db.t3.micro"
  allocated_storage = 5
}


###########
# Master DB
###########
resource "random_password" "password" {
  length  = 16
  special = false
}

module "db" {
  source = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "lambda-mysql"

  engine             = local.engine
  engine_version     = local.engine_version
  instance_class     = local.instance_class
  create_db_instance = var.create_db_instance
  allocated_storage  = local.allocated_storage
  manage_master_user_password = false

  db_name  = "lambda"
  username = "lambda"
  password = random_password.password.result
  port     = local.port

  vpc_security_group_ids = [module.mysql_security_group.security_group_id]

  maintenance_window     = "Mon:00:00-Mon:03:00"
  backup_window          = "03:00-06:00"

  # Backups are required in order to create a replica
  backup_retention_period = 1

  # DB subnet group
  db_subnet_group_name = module.vpc.database_subnet_group_name
  subnet_ids = module.vpc.database_subnets

  storage_encrypted = false

  create_db_option_group    = false
  create_db_parameter_group = false
}
