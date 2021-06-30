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
  public_subnets       = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]  
  enable_dns_hostnames = true  
  enable_dns_support   = true
}

resource "aws_db_subnet_group" "basic" {
  name       = "basic"  
  subnet_ids = module.vpc.public_subnets
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
resource "aws_ecs_cluster" "basic" {
  name = "basic-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_cloudwatch_log_group" "book_manager" {
  name = "book_manager"
}

resource "aws_ecs_task_definition" "book_manager" {
  family = "simple-python-application"

  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu = 256
  memory = 512
  container_definitions = <<EOF
[
  {
    "name": "simple-python-application",
    "image": "docker.io/hayunofek/aws_test:latest",
    "portMappings": [
        {
          "containerPort": 5000,
          "hostPort": 5000
        }
    ],
    "cpu": 256,
    "memory": 512,
    "environment": [
      { "name": "DB_USER", "value": "${aws_db_instance.basic.username}" },
      { "name": "DB_PASSWORD", "value": "${var.db_password}" },
      { "name": "DB_HOST", "value": "${aws_db_instance.basic.address}" },
      { "name": "DB_PORT", "value": "${aws_db_instance.basic.port}" }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-region": "eu-west-1",
        "awslogs-group": "book_manager"
      }
    }
  }
]
EOF
}

# { "name": "DB_DB", "value": "${aws_db_instance.basic.port}" }

resource "aws_alb" "application_load_balancer" {
  name               = "book-manager-lb"
  load_balancer_type = "application"
  subnets =  module.vpc.public_subnets
  security_groups = [aws_security_group.load_balancer_security_group.id]
}

resource "aws_security_group" "load_balancer_security_group" {
  vpc_id = module.vpc.vpc_id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb_target_group" "target_group" {
  name        = "target-group"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = module.vpc.vpc_id
}

resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_alb.application_load_balancer.arn
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target_group.arn
  }
}


resource "aws_ecs_service" "book_manager" {
  name            = "book_manager"
  cluster         = aws_ecs_cluster.basic.id
  task_definition = aws_ecs_task_definition.book_manager.arn

  desired_count = 1

  launch_type     = "FARGATE"
  deployment_maximum_percent         = 100
  deployment_minimum_healthy_percent = 0

  load_balancer {
    target_group_arn = aws_lb_target_group.target_group.arn
    container_name   = aws_ecs_task_definition.book_manager.family
    container_port   = 5000
  }

  network_configuration {
    subnets = module.vpc.public_subnets
    assign_public_ip = true
    security_groups  = [aws_security_group.service_security_group.id]
  }
}


resource "aws_security_group" "service_security_group" {
  vpc_id = module.vpc.vpc_id
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    security_groups = [aws_security_group.load_balancer_security_group.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
