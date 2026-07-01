provider "aws" {
  region = "eu-west-2"
}

module "vpc" {
  source = "./modules/vpc"

  app_name              = var.app_name
  vpc_cidr              = var.vpc_cidr
  public_subnet_cidr    = var.public_subnet_cidr
  public_subnet_cidr_2  = var.public_subnet_cidr_2
  private_subnet_cidr   = var.private_subnet_cidr
}

module "ecs" {
  source = "./modules/ecs"

  app_name           = var.app_name
  container_image    = var.container_image
  container_port     = var.container_port
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids
}
