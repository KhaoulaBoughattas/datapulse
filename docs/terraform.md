# DataPulse — Terraform Usage

```
cd terraform/environments/dev
terraform init
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
```

Module structure: `terraform/modules/{networking,s3,rds,iam,ecs,monitoring}`,
composed identically by `environments/{dev,prod}` — differences are
variable values only, not structural rewrites.
