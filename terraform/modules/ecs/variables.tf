variable "app_name" {
  description = "Application name for resource naming"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where cluster will be deployed"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs for app load balancer"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for ECS tasks"
  type        = list(string)
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
