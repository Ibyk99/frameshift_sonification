output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.app_vpc.id
}

output "private_subnet_id" {
  description = "Private subnet ID"
  value       = aws_subnet.private_subnet.id
}

output "public_subnet_id" {
  description = "Public subnet ID"
  value       = aws_subnet.public_subnet.id
}

output "nat_gateway_id" {
  description = "NAT gateway ID"
  value       = aws_nat_gateway.nat_gw.id
}

output "internet_gateway_id" {
  description = "Internet gateway ID"
  value       = aws_internet_gateway.internet_gw.id
}
