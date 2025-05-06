terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    # Configure your S3 backend here
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  environment     = var.environment
  vpc_cidr        = var.vpc_cidr
  azs             = var.availability_zones
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets
}

# MSK Module
module "msk" {
  source = "./modules/msk"
  
  environment      = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnet_ids
  kafka_version   = "3.4.0"
  broker_nodes    = 2
  instance_type   = "kafka.t3.small"
}

# Lambda Module
module "lambda" {
  source = "./modules/lambda"
  
  environment      = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnet_ids
  msk_cluster_arn = module.msk.cluster_arn
  kafka_topic     = var.kafka_topic
}

# Glue and Athena Module
module "analytics" {
  source = "./modules/analytics"
  
  environment    = var.environment
  database_name = "parking_analytics"
  s3_bucket     = var.s3_bucket
  msk_cluster_arn = module.msk.cluster_arn
} 