provider "aws" {
  region = "eu-west-2"
}


resource "aws_default_vpc" "default" {
  tags = {
    Name = "Default VPC"
  }
}