output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.app_vpc.id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = [aws_subnet.private_subnet.id, aws_subnet.private_subnet_2.id]
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = [aws_subnet.public_subnet.id, aws_subnet.public_subnet_2.id]
}

output "nat_gateway_id" {
  description = "NAT gateway ID"
  value       = aws_nat_gateway.nat_gw.id
}

output "internet_gateway_id" {
  description = "Internet gateway ID"
  value       = aws_internet_gateway.internet_gw.id
}
