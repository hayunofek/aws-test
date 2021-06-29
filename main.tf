terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}

provider "aws" {
  profile = "default"
  region  = "eu-west-1"
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "2.77.0"

  name                 = "basic"
  cidr                 = "10.0.0.0/16"  
  azs                  = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
  private_subnets      = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
#  public_subnets       = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]  
  enable_dns_hostnames = true  
  enable_dns_support   = true
}

resource "aws_db_subnet_group" "basic" {
  name       = "basic"  
  subnet_ids = module.vpc.private_subnets
  tags = {
    Name = "Basic"
  }
}

resource "aws_security_group" "rds" {
  name   = "basic_rds"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "basic_rds"
  }
}

#resource "aws_db_parameter_group" "basic" {
#  name   = "basic"
#  family = "postgres13"
#
#  parameter {
#    name  = "log_connections"
#    value = "1"
#  }
#}

resource "aws_db_instance" "basic" {
  identifier             = "basic"  
  instance_class         = "db.t3.micro"  
  allocated_storage      = 5  
  engine                 = "postgres"  
  engine_version         = "13.1"  
  username               = "basic"  
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.basic.name  
  vpc_security_group_ids = [aws_security_group.rds.id]  
#  parameter_group_name   = aws_db_parameter_group.basic.name  
  # TODO maybe change to publicly_accessible
  publicly_accessible    = false  
  skip_final_snapshot    = true
}

#
#resource "aws_ecs_cluster" "basic" {
#  name = "basic-cluster"
#
#  setting {
#    name  = "containerInsights"
#    value = "enabled"
#  }
#}
