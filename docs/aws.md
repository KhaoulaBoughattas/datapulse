# DataPulse — AWS Architecture

## What's provisioned vs. not
Provisioned: VPC (2 AZs, public/private split), RDS Postgres, S3, ECS
Fargate + ALB, IAM least-privilege roles, CloudWatch alarms.
NOT provisioned: MSK, EMR/Spark-on-EKS, MWAA, Superset, Prometheus/
Grafana as ECS services, HTTPS/ACM — same patterns already built here,
not new concepts, but real additional work.

## Why private subnets for RDS/ECS, public only for ALB
Minimum necessary exposure — only the load balancer needs an internet route.

## Teardown (avoid runaway billing)
```
cd terraform/environments/dev
terraform destroy
```
NAT Gateways and RDS bill hourly even fully idle.
