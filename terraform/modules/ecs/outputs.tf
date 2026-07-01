output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.app_lb.dns_name
}

output "target_group_arn" {
  description = "ARN of the target group"
  value       = aws_lb_target_group.app_tg.arn
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.app_service.name
}
