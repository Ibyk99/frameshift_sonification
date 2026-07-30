variable "app_name" {
  description = "Application name"
  type        = string
  default     = "frameshift"
}

variable "container_image" {
  description = "Container image URI from ECR"
  type        = string
  default = "433289389071.dkr.ecr.eu-west-2.amazonaws.com/sonification/sonification_app:latest"
}

variable "container_port" {
  description = "Port exposed by container"
  type        = number
  default     = 5001
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for first public subnet"
  type        = string
  default     = "10.0.2.0/24"
}

variable "public_subnet_cidr_2" {
  description = "CIDR block for second public subnet"
  type        = string
  default     = "10.0.3.0/24"
}

variable "private_subnet_cidr" {
  description = "CIDR block for private subnet"
  type        = string
  default     = "10.0.1.0/24"
}
