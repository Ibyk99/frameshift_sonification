variable "app_name" {
  description = "Application name for resource naming"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where cluster will be deployed"
  type        = string
}

variable "public_subnet_id" {
  description = "Public subnet ID for app load balancer"
  type        = string
}

variable "private_subnet_id" {
  description = "Private subnet ID for ECS tasks"
  type        = string
}

variable "container_image" {
  description = "URI of the container image from ECR that will be used to deploy the container"
  type        = string
}

variable "container_port" {
  description = "Port inside the container to map to"
  type        = number
  default     = 5001
}
