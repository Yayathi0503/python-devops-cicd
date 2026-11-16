mock_provider "aws" {}

variables {
  instance_id = "i-0123456789abcdef0"
  aws_region  = "ap-south-1"
}

run "dashboard_and_alarms" {
  command = apply

  assert {
    condition     = length(jsondecode(aws_cloudwatch_dashboard.operations.dashboard_body).widgets) == 6
    error_message = "The dashboard must contain its header and five operational widgets."
  }

  assert {
    condition = alltrue([
      for widget in jsondecode(aws_cloudwatch_dashboard.operations.dashboard_body).widgets :
      widget.x >= 0 && widget.y >= 0 && widget.width > 0 && widget.height > 0 && widget.x + widget.width <= 24
    ])
    error_message = "Widgets must stay inside CloudWatch's 24-column grid."
  }

  assert {
    condition = alltrue([
      for widget in jsondecode(aws_cloudwatch_dashboard.operations.dashboard_body).widgets :
      widget.properties.region == var.aws_region && widget.properties.period == 300 && alltrue([
        for metric in widget.properties.metrics : metric[0] == "AWS/EC2" && metric[2] == "InstanceId" && metric[3] == var.instance_id
      ]) if widget.type == "metric"
    ])
    error_message = "EC2 widgets must use the selected instance, region and basic-monitoring period."
  }

  assert {
    condition     = aws_cloudwatch_metric_alarm.cpu.threshold == 80 && aws_cloudwatch_metric_alarm.cpu.evaluation_periods == 2 && aws_cloudwatch_metric_alarm.status.metric_name == "StatusCheckFailed"
    error_message = "CPU and status alarms must monitor the documented conditions."
  }

  assert {
    condition     = aws_cloudwatch_metric_alarm.cpu.treat_missing_data == "missing" && aws_cloudwatch_metric_alarm.status.treat_missing_data == "missing"
    error_message = "Missing data must not silently look healthy."
  }

  assert {
    condition     = length(aws_cloudwatch_metric_alarm.cpu.alarm_actions) == 0 && aws_cloudwatch_log_group.app.retention_in_days == 7 && strcontains(jsondecode(aws_cloudwatch_dashboard.operations.dashboard_body).widgets[5].properties.query, aws_cloudwatch_log_group.app.name)
    error_message = "Logs must use the managed group with seven-day retention and notifications must be opt-in."
  }
}

run "custom_configuration" {
  command = apply

  variables {
    instance_id   = "i-abcdef01234567890"
    aws_region    = "us-east-1"
    project_name  = "portfolio-prod"
    cpu_threshold = 90
    alarm_actions = ["arn:aws:sns:us-east-1:123456789012:operations"]
  }

  assert {
    condition     = aws_cloudwatch_dashboard.operations.dashboard_name == "portfolio-prod-operations" && aws_cloudwatch_metric_alarm.cpu.threshold == 90 && aws_cloudwatch_metric_alarm.cpu.dimensions["InstanceId"] == var.instance_id
    error_message = "Custom names, thresholds and instance selection must be respected."
  }

  assert {
    condition     = toset(aws_cloudwatch_metric_alarm.cpu.alarm_actions) == toset(var.alarm_actions) && toset(aws_cloudwatch_metric_alarm.status.ok_actions) == toset(var.alarm_actions)
    error_message = "Both alarms must deliver notifications and recovery events to the selected SNS topic."
  }
}

run "reject_invalid_instance" {
  command = plan
  variables { instance_id = "not-an-instance" }
  expect_failures = [var.instance_id]
}

run "reject_invalid_threshold" {
  command = plan
  variables { cpu_threshold = 101 }
  expect_failures = [var.cpu_threshold]
}
