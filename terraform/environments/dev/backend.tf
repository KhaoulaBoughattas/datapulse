# Remote state backend — bootstrap the state bucket/lock table manually
# first, then uncomment:
# terraform {
#   backend "s3" {
#     bucket         = "datapulse-terraform-state"
#     key            = "dev/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "datapulse-terraform-locks"
#     encrypt        = true
#   }
# }
