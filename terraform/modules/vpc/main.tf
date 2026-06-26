resource "aws_vpc" "app_vpc" {
  cidr_block = var.vpc_cidr
  tags = {
    Name = "${var.app_name}-vpc"
  }
}

resource "aws_subnet" "private_subnet" {
  vpc_id     = aws_vpc.app_vpc.id
  cidr_block = var.private_subnet_cidr
  tags = {
    Name = "${var.app_name}-private-subnet"
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id     = aws_vpc.app_vpc.id
  cidr_block = var.public_subnet_cidr
  tags = {
    Name = "${var.app_name}-public-subnet"
  }
}

resource "aws_internet_gateway" "internet_gw" {
  vpc_id = aws_vpc.app_vpc.id
  tags = {
    Name = "${var.app_name}-igw"
  }
}

resource "aws_eip" "nat_eip" {
  domain     = "vpc"
  depends_on = [aws_internet_gateway.internet_gw]
}

resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public_subnet.id

  tags = {
    Name = "${var.app_name}-nat"
  }
  depends_on = [aws_internet_gateway.internet_gw]
}

resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.app_vpc.id
  route = {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.internet_gw.id
  }
}

resource "aws_route_table" "private_route_table" {
  vpc_id = aws_vpc.app_vpc.id
  route = {
    cidr_block = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gw.id
  }
}

resource "aws_route_table_association" "private_association" {
  subnet_id      = aws_subnet.private_subnet.id
  route_table_id = aws_route_table.private_route_table.id
}

resource "aws_route_table_association" "public_association" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_route_table.id
}
