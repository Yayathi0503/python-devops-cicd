output "dashboard_name" {
  description = "Created CloudWatch dashboard name."
  value       = aws_cloudwatch_dashboard.operations.dashboard_name
}

output "dashboard_url" {
  description = "AWS console link; sign in to the account used for apply."
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.operations.dashboard_name}"
}

output "log_group_name" {
  description = "Log group to configure on the Docker awslogs driver."
  value       = aws_cloudwatch_log_group.app.name
}

output "dashboard_body" {
  description = "Dashboard JSON for inspection or export with terraform output -raw dashboard_body."
  value       = aws_cloudwatch_dashboard.operations.dashboard_body
}
