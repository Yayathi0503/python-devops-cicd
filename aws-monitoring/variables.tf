variable "aws_region" {
  description = "Region containing the existing EC2 instance."
  type        = string
  default     = "ap-south-1"

  validation {
    condition     = can(regex("^[a-z]{2}(-[a-z]+)+-[0-9]+$", var.aws_region))
    error_message = "Supply a valid AWS region name."
  }
}

variable "instance_id" {
  description = "Existing EC2 instance to monitor; this module creates no EC2 resources."
  type        = string

  validation {
    condition     = can(regex("^i-([0-9a-f]{8}|[0-9a-f]{17})$", var.instance_id))
    error_message = "Use an EC2 instance ID (i- followed by 8 or 17 hexadecimal characters)."
  }
}

variable "project_name" {
  description = "Unique name prefix for the dashboard, log group and alarms."
  type        = string
  default     = "task-api"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,39}$", var.project_name))
    error_message = "Use 2-40 lowercase letters, digits or hyphens, starting with a letter."
  }
}

variable "cpu_threshold" {
  description = "CPU percentage that triggers the high-CPU alarm for two five-minute periods."
  type        = number
  default     = 80

  validation {
    condition     = var.cpu_threshold > 0 && var.cpu_threshold <= 100
    error_message = "CPU threshold must be greater than 0 and at most 100."
  }
}

variable "alarm_actions" {
  description = "Optional existing SNS topic ARNs for alarm and recovery notifications."
  type        = list(string)
  default     = []

  validation {
    condition = alltrue([
      for arn in var.alarm_actions : can(regex("^arn:[a-z-]+:sns:[a-z0-9-]+:[0-9]{12}:[A-Za-z0-9_-]+(\\.fifo)?$", arn))
    ])
    error_message = "Each notification target must be an SNS topic ARN."
  }
}
