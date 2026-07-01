resource "aws_ecs_cluster" "app_cluster" {
  name = "${var.app_name}-cluster"
}

resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/aws/ecs/${var.app_name}"
  retention_in_days = 5
}

resource "aws_iam_role" "ecs_role" {
  name = "ecs_task_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
    ]
  })

}

resource "aws_iam_policy_attachment" "ecs_policy" {
  name       = "ecs_task_policy_attachment"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  roles      = [aws_iam_role.ecs_role.name]
}

resource "aws_security_group" "alb_sg" {
  name   = "${var.app_name}-alb-sg"
  vpc_id = var.vpc_id

}

resource "aws_security_group" "cluster_sg" {
  name   = "${var.app_name}-cluster-sg"
  vpc_id = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "cluster_to_alb" {
  security_group_id            = aws_security_group.cluster_sg.id
  referenced_security_group_id = aws_security_group.alb_sg.id
  from_port                    = 5001
  ip_protocol                  = "tcp"
  to_port                      = 5001
}

resource "aws_vpc_security_group_ingress_rule" "allow_https" {
  security_group_id = aws_security_group.alb_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}
resource "aws_vpc_security_group_ingress_rule" "allow_http" {
  security_group_id = aws_security_group.alb_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  ip_protocol       = "tcp"
  to_port           = 80
}

resource "aws_vpc_security_group_egress_rule" "alb_to_cluster" {
  security_group_id            = aws_security_group.alb_sg.id
  referenced_security_group_id = aws_security_group.cluster_sg.id
  from_port                    = 5001
  ip_protocol                  = "tcp"
  to_port                      = 5001
}

resource "aws_vpc_security_group_egress_rule" "cluster_egress" {
  security_group_id = aws_security_group.cluster_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

resource "aws_lb" "app_lb" {
  name               = "${var.app_name}-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = false
  tags = {
    Environment = "production"
  }
}

resource "aws_lb_target_group" "app_tg" {
  name        = "${var.app_name}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  # health_check {
  #   healthy_threshold   = 2
  #   unhealthy_threshold = 3
  #   timeout             = 5
  #   interval            = 10
  #   path                = "/"
  #   matcher             = "200-399"
  # }
}

resource "aws_lb_listener" "app_listener" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}

resource "aws_ecs_task_definition" "app_definition" {
  family                   = "${var.app_name}-family"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.ecs_role.arn
  container_definitions = jsonencode([
    {
      name      = "${var.app_name}-container"
      image     = var.container_image
      essential = true
      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = 5001
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app_logs.name
          "awslogs-region"        = "eu-west-2"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "app_service" {
  name                 = "${var.app_name}-service"
  cluster              = aws_ecs_cluster.app_cluster.id
  task_definition      = aws_ecs_task_definition.app_definition.arn
  desired_count        = 1
  launch_type          = "FARGATE"
  force_new_deployment = true
  health_check_grace_period_seconds = 60
  network_configuration {
    assign_public_ip = false
    subnets = var.private_subnet_ids
    security_groups = [aws_security_group.cluster_sg.id]
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.app_tg.arn
    container_name   = "${var.app_name}-container"
    container_port   = var.container_port
  }


}