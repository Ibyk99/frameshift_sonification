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
  roles      = aws_iam_role.ecs_role.name
}

resource "aws_security_group" "alb_sg" {
    name = "${var.app_name}-alb-sg"
    vpc_id = var.vpc_id

    ingress {
        from_port = 443
        to_port   = 443
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port = 80
        to_port   = 80
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port   = 5001
        to_port     = 5001
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_alb" "app_alb" {
        

}
