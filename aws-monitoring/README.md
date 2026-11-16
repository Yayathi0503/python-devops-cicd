# AWS CloudWatch operations dashboard

Terraform creates a six-widget dashboard for an **existing EC2 instance**, a
seven-day container log group and two CloudWatch alarms. It adds no compute,
networking or public endpoints. Configure the instance ID and region yourself.

- CPU utilization, inbound/outbound network bytes and instance/system status.
- High CPU alarm: average above 80% for two five-minute periods.
- Status alarm: any failed EC2 status check in one five-minute period.
- Alarm state widget and recent container logs with CloudWatch Logs Insights.
- Optional SNS alarm and recovery notifications using an existing topic.

The graphs use AWS/EC2 metrics available without a CloudWatch Agent. Memory,
filesystem usage and application latency require additional instrumentation and
are not included. Terraform tests use a mocked provider: they never create AWS
resources and do not establish that a dashboard is live in an AWS account.

## Validate without AWS credentials

Requires Terraform 1.7+ and network access to install the AWS provider:

```sh
cd aws-monitoring
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
terraform test
```

## Deploy to your AWS account

1. Authenticate with an authorized AWS CLI profile or workload role; do not put
   access keys in this repository. Confirm `aws sts get-caller-identity`.
2. Copy `terraform.tfvars.example` to `terraform.tfvars`. Replace the example
   instance ID with a real EC2 ID in the selected region. Choose a project name
   unique in the account because dashboard names are account-wide.
3. Run `terraform plan` and inspect the four resources. Run `terraform apply` to
   create the dashboard, two alarms and log group, then open the link returned by
   `terraform output -raw dashboard_url`.
4. If supplying an SNS ARN, confirm its subscriptions and allow CloudWatch to
   publish to the topic. With the default empty list, alarms change state but
   send no notifications. Stopped instances or missing samples may produce
   `INSUFFICIENT_DATA`; they are not marked healthy automatically.

The Terraform execution identity needs CloudWatch dashboard and alarm management
and CloudWatch Logs group/tag/retention management for these resources. Scope
permissions to your project; this module does not grant account permissions.
The console viewer also needs CloudWatch read access and Logs Insights query
permissions. Existing resources with the same names must be imported or renamed
before applying. Preserve Terraform state outside version control.

## Send container logs from EC2

After applying, build the Task API image on your EC2 Linux Docker host. Attach
an instance role that allows `logs:CreateLogStream` and `logs:PutLogEvents` for
streams under this module's log group. The Docker daemon obtains credentials
from that role; never pass static AWS keys to the container.

Example for the default region and project name:

```sh
docker build -t task-api:aws task-management-api
docker run -d --name task-api \
  --publish 127.0.0.1:8080:8080 \
  --mount type=volume,source=task-api-data,target=/data \
  --log-driver awslogs \
  --log-opt awslogs-region=ap-south-1 \
  --log-opt awslogs-group=/portfolio/task-api \
  --log-opt awslogs-stream=task-api \
  task-api:aws
curl --fail http://127.0.0.1:8080/ready
```

Change both log options when changing the Terraform region/project name. The
driver sends container stdout/stderr, including server startup/errors; this is
not per-request access logging. The log widget remains empty until messages
arrive. The API binds to loopback on the EC2 host; use an SSH tunnel for a demo.
This sample API has no authentication and is not a public production service.

## Inspect and clean up

After apply, verify the instance dimensions, wait for EC2 data, inspect alarm
states and check incoming logs. Keep actual screenshots or AWS receipts only
after these live checks. To remove resources created here:

```sh
terraform plan -destroy
terraform destroy
```

Destroy removes the dashboard, alarms and collected logs. It does not terminate
the existing EC2 instance, stop a container or remove its data volume. CloudWatch
dashboards, alarms, log ingestion/storage and queries may incur charges; consult
your account pricing and remove demo resources when finished.

References: [CloudWatch dashboard JSON](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Dashboard-Body-Structure.html),
[EC2 metrics](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/viewing_metrics_with_cloudwatch.html),
[Docker awslogs driver](https://docs.docker.com/engine/logging/drivers/awslogs/).
