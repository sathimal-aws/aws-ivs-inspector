# Fetch AZs in the current region
data "aws_availability_zones" "available" {
}

# create vpc
resource "aws_vpc" "ecs_task_vpc" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true
  lifecycle {
    create_before_destroy = true
  }
  tags = {
    Name = "${var.project_name}-${var.region}-ecs-task-vpc"
  }
}

# Create var.az_count private subnets, each in a different AZ
resource "aws_subnet" "private" {
  count                   = var.az_count
  vpc_id                  = aws_vpc.ecs_task_vpc.id
  cidr_block              = cidrsubnet(aws_vpc.ecs_task_vpc.cidr_block, 8, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = false
  tags = {
    Name = "${var.project_name}-${var.region}-${aws_vpc.ecs_task_vpc.id}-private-${count.index}"
  }
}

resource "aws_security_group" "ecs_tasks" {
  name        = "${local.service_name}-ecs-tasks"
  description = "${local.service_name} associated to ECR/S3 VPC Endpoints"
  vpc_id      = aws_vpc.ecs_task_vpc.id
  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = [aws_vpc.ecs_task_vpc.cidr_block]
  }
  egress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }
  lifecycle {
    create_before_destroy = true
  }
  tags = {
    Name = "${local.service_name}-ecs-secgrp"
  }
}

# Create a new route table for the private subnets, make it route non-local traffic through the NAT gateway to the internet
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.ecs_task_vpc.id
  tags = {
    Name = "${var.project_name}-rt-private"
  }
}

# Explicitly associate the newly created route tables to the private subnets (so they don't default to the main route table)
resource "aws_route_table_association" "private" {
  count          = var.az_count
  subnet_id      = element(aws_subnet.private.*.id, count.index)
  route_table_id = aws_route_table.private.id
}

resource "aws_vpc_endpoint" "s3_vpc_endpoint" {
  vpc_id            = aws_vpc.ecs_task_vpc.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]
  tags = {
    "Name" = "${var.project_name}-${var.region}-s3"
  }
}

resource "aws_vpc_endpoint" "cw_vpc_endpoint" {
  vpc_id              = aws_vpc.ecs_task_vpc.id
  service_name        = "com.amazonaws.${var.region}.logs"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.ecs_tasks.id]
  subnet_ids          = aws_subnet.private.*.id
  tags = {
    "Name" = "${var.project_name}-${var.region}-cw-logs"
  }
}

resource "aws_vpc_endpoint" "dynamodb_vpc_endpoint" {
  vpc_id            = aws_vpc.ecs_task_vpc.id
  service_name      = "com.amazonaws.${var.region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]
  tags = {
    "Name" = "${var.project_name}-${var.region}-dynamodb"
  }
}

resource "aws_vpc_endpoint_route_table_association" "dynamodb_route_table_association" {
  vpc_endpoint_id = aws_vpc_endpoint.dynamodb_vpc_endpoint.id
  route_table_id  = aws_route_table.private.id
}

resource "aws_vpc_endpoint" "cloudwatch_vpc_endpoint" {
  vpc_id              = aws_vpc.ecs_task_vpc.id
  service_name        = "com.amazonaws.${var.region}.monitoring"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.ecs_tasks.id]
  subnet_ids          = aws_subnet.private.*.id
  tags = {
    "Name" = "${var.project_name}-${var.region}-cw-monitoring"
  }
}

resource "aws_vpc_endpoint" "ecr_dkr_endpoint" {
  vpc_id              = aws_vpc.ecs_task_vpc.id
  service_name        = "com.amazonaws.${var.region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.ecs_tasks.id]
  subnet_ids          = aws_subnet.private.*.id
  tags = {
    "Name" = "${var.project_name}-${var.region}-ecr-dkr"
  }
}

resource "aws_vpc_endpoint" "ecr_api_endpoint" {
  vpc_id              = aws_vpc.ecs_task_vpc.id
  service_name        = "com.amazonaws.${var.region}.ecr.api"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.ecs_tasks.id]
  subnet_ids          = aws_subnet.private.*.id
  tags = {
    "Name" = "${var.project_name}-${var.region}-ecr-api"
  }
}
