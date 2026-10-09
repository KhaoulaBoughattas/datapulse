resource "aws_cloudwatch_metric_alarm" "ecs_high_cpu" {
  alarm_name          = "${var.project_name}-${var.environment}-ecs-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ECS service CPU above 80% for 3 consecutive minutes"
  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }
  alarm_actions = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []
}
