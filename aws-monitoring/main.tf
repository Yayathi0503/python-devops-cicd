locals {
  log_group_name = "/portfolio/${var.project_name}"
  instance       = ["InstanceId", var.instance_id]
  metric_base = {
    region  = var.aws_region
    period  = 300
    view    = "timeSeries"
    stacked = false
  }

  dashboard = {
    start          = "-PT6H"
    periodOverride = "inherit"
    widgets = [
      {
        type = "text", x = 0, y = 0, width = 24, height = 2
        properties = {
          markdown = "# ${var.project_name} | EC2 and container operations\nInstance: `${var.instance_id}` | Region: `${var.aws_region}`. Five-minute EC2 metrics; logs appear after the container uses the awslogs driver."
        }
      },
      {
        type = "metric", x = 0, y = 2, width = 12, height = 6
        properties = merge(local.metric_base, {
          title   = "EC2 CPU utilization (%)"
          stat    = "Average"
          metrics = [concat(["AWS/EC2", "CPUUtilization"], local.instance)]
          yAxis   = { left = { min = 0, max = 100 } }
        })
      },
      {
        type = "metric", x = 12, y = 2, width = 12, height = 6
        properties = merge(local.metric_base, {
          title = "EC2 network traffic (bytes per 5 minutes)"
          stat  = "Sum"
          metrics = [
            concat(["AWS/EC2", "NetworkIn"], local.instance),
            concat(["AWS/EC2", "NetworkOut"], local.instance)
          ]
        })
      },
      {
        type = "metric", x = 0, y = 8, width = 12, height = 6
        properties = merge(local.metric_base, {
          title = "EC2 status checks (0 = healthy, 1 = failed)"
          stat  = "Maximum"
          metrics = [
            concat(["AWS/EC2", "StatusCheckFailed_Instance"], local.instance),
            concat(["AWS/EC2", "StatusCheckFailed_System"], local.instance)
          ]
          yAxis = { left = { min = 0, max = 1 } }
        })
      },
      {
        type = "alarm", x = 12, y = 8, width = 12, height = 6
        properties = {
          title  = "CPU and instance health alarms"
          alarms = [aws_cloudwatch_metric_alarm.cpu.arn, aws_cloudwatch_metric_alarm.status.arn]
        }
      },
      {
        type = "log", x = 0, y = 14, width = 24, height = 6
        properties = {
          title  = "Recent container logs"
          region = var.aws_region
          view   = "table"
          query  = "SOURCE '${aws_cloudwatch_log_group.app.name}' | fields @timestamp, @logStream, @message | sort @timestamp desc | limit 50"
        }
      }
    ]
  }
}

resource "aws_cloudwatch_log_group" "app" {
  name              = local.log_group_name
  retention_in_days = 7
  tags              = { Project = var.project_name, ManagedBy = "Terraform" }
}

resource "aws_cloudwatch_metric_alarm" "cpu" {
  alarm_name          = "${var.project_name}-high-cpu"
  alarm_description   = "EC2 average CPU exceeds ${var.cpu_threshold}% for 10 minutes."
  namespace           = "AWS/EC2"
  metric_name         = "CPUUtilization"
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 2
  datapoints_to_alarm = 2
  comparison_operator = "GreaterThanThreshold"
  threshold           = var.cpu_threshold
  treat_missing_data  = "missing"
  dimensions          = { InstanceId = var.instance_id }
  alarm_actions       = var.alarm_actions
  ok_actions          = var.alarm_actions
  tags                = { Project = var.project_name, ManagedBy = "Terraform" }
}

resource "aws_cloudwatch_metric_alarm" "status" {
  alarm_name          = "${var.project_name}-status-check-failed"
  alarm_description   = "An EC2 instance or system status check failed."
  namespace           = "AWS/EC2"
  metric_name         = "StatusCheckFailed"
  statistic           = "Maximum"
  period              = 300
  evaluation_periods  = 1
  datapoints_to_alarm = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  threshold           = 1
  treat_missing_data  = "missing"
  dimensions          = { InstanceId = var.instance_id }
  alarm_actions       = var.alarm_actions
  ok_actions          = var.alarm_actions
  tags                = { Project = var.project_name, ManagedBy = "Terraform" }
}

resource "aws_cloudwatch_dashboard" "operations" {
  dashboard_name = "${var.project_name}-operations"
  dashboard_body = jsonencode(local.dashboard)
}
