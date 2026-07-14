terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # backend "s3" {
  #   bucket = "tsubo-terraform-state"
  #   key    = "aws/main.tfstate"
  #   region = "ap-northeast-1"
  # }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region for Tsubo infrastructure"
  type        = string
  default     = "ap-northeast-1"
}

variable "environment" {
  description = "Deployment environment (staging, production)"
  type        = string
  default     = "staging"
}

variable "project" {
  description = "Project name used for resource naming"
  type        = string
  default     = "tsubo"
}

locals {
  name_prefix = "${var.project}-${var.environment}"
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# --- Networking (reference skeleton) ---

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-vpc"
  })
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-${count.index}"
  })
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index + 10)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-${count.index}"
  })
}

data "aws_availability_zones" "available" {
  state = "available"
}

# --- RDS PostgreSQL (reference skeleton) ---

resource "aws_db_subnet_group" "main" {
  name       = "${local.name_prefix}-db"
  subnet_ids = aws_subnet.private[*].id

  tags = local.common_tags
}

resource "aws_security_group" "rds" {
  name        = "${local.name_prefix}-rds"
  description = "RDS access for Tsubo API and worker"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

resource "aws_db_instance" "postgres" {
  identifier             = "${local.name_prefix}-postgres"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = "db.t4g.medium"
  allocated_storage      = 50
  storage_encrypted      = true
  db_name                = "tsubo"
  username               = "tsubo"
  manage_master_user_password = true
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  skip_final_snapshot    = var.environment != "production"
  publicly_accessible    = false

  tags = local.common_tags
}

# --- ECS Fargate (reference skeleton) ---

resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"

  tags = local.common_tags
}

resource "aws_ecr_repository" "api" {
  name                 = "${local.name_prefix}/api"
  image_tag_mutability = "MUTABLE"
  force_delete         = var.environment != "production"

  tags = local.common_tags
}

resource "aws_ecr_repository" "worker" {
  name                 = "${local.name_prefix}/worker"
  image_tag_mutability = "MUTABLE"
  force_delete         = var.environment != "production"

  tags = local.common_tags
}

# --- OpenSearch (reference skeleton) ---

resource "aws_opensearch_domain" "main" {
  domain_name    = "${local.name_prefix}-search"
  engine_version = "OpenSearch_2.11"

  cluster_config {
    instance_type  = "t3.small.search"
    instance_count = 1
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 20
  }

  tags = local.common_tags
}

# --- Outputs ---

output "vpc_id" {
  value = aws_vpc.main.id
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.endpoint
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "opensearch_endpoint" {
  value = aws_opensearch_domain.main.endpoint
}
