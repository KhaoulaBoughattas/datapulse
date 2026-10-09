locals {
  project_name = "datapulse"
  environment  = "dev"
}

module "networking" {
  source       = "../../modules/networking"
  project_name = local.project_name
  environment  = local.environment
  azs          = var.azs
}

module "s3" {
  source        = "../../modules/s3"
  project_name  = local.project_name
  environment   = local.environment
  force_destroy = true
}

module "rds" {
  source                = "../../modules/rds"
  project_name          = local.project_name
  environment           = local.environment
  vpc_id                = module.networking.vpc_id
  private_subnet_ids    = module.networking.private_subnet_ids
  rds_security_group_id = module.networking.rds_security_group_id
  instance_class        = "db.t4g.micro"
  multi_az              = false
}

resource "random_password" "jwt_secret" {
  length  = 48
  special = false
}

resource "aws_secretsmanager_secret" "jwt_secret" {
  name = "${local.project_name}/${local.environment}/jwt-secret"
}

resource "aws_secretsmanager_secret_version" "jwt_secret" {
  secret_id     = aws_secretsmanager_secret.jwt_secret.id
  secret_string = jsonencode({ jwt_secret = random_password.jwt_secret.result })
}

module "iam" {
  source         = "../../modules/iam"
  project_name   = local.project_name
  environment    = local.environment
  s3_bucket_arn  = module.s3.bucket_arn
  db_secret_arn  = module.rds.secret_arn
  jwt_secret_arn = aws_secretsmanager_secret.jwt_secret.arn
}

module "ecs" {
  source                 = "../../modules/ecs"
  project_name           = local.project_name
  environment            = local.environment
  vpc_id                 = module.networking.vpc_id
  public_subnet_ids      = module.networking.public_subnet_ids
  private_subnet_ids     = module.networking.private_subnet_ids
  alb_security_group_id  = module.networking.alb_security_group_id
  ecs_security_group_id  = module.networking.ecs_security_group_id
  ecs_execution_role_arn = module.iam.ecs_execution_role_arn
  ecs_task_role_arn      = module.iam.ecs_task_role_arn
  db_secret_arn          = module.rds.secret_arn
  jwt_secret_arn         = aws_secretsmanager_secret.jwt_secret.arn
  backend_image          = var.backend_image
  frontend_image         = var.frontend_image
  backend_desired_count  = 1
}

module "monitoring" {
  source           = "../../modules/monitoring"
  project_name     = local.project_name
  environment      = local.environment
  ecs_cluster_name = module.ecs.cluster_name
  ecs_service_name = "${local.project_name}-${local.environment}-backend"
}
