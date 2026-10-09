resource "aws_db_subnet_group" "this" {
  name       = "${var.project_name}-${var.environment}-db-subnets"
  subnet_ids = var.private_subnet_ids
  tags       = { Name = "${var.project_name}-${var.environment}-db-subnets" }
}

resource "random_password" "db_master" {
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret" "db_credentials" {
  name = "${var.project_name}/${var.environment}/rds/master-credentials"
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.master_username
    password = random_password.db_master.result
    host     = aws_db_instance.this.address
    port     = 5432
    dbname   = var.db_name
  })
}

resource "aws_db_instance" "this" {
  identifier              = "${var.project_name}-${var.environment}-postgres"
  engine                  = "postgres"
  engine_version          = "16.4"
  instance_class          = var.instance_class
  allocated_storage       = var.allocated_storage
  storage_encrypted       = true
  db_name                 = var.db_name
  username                = var.master_username
  password                = random_password.db_master.result
  db_subnet_group_name    = aws_db_subnet_group.this.name
  vpc_security_group_ids  = [var.rds_security_group_id]
  multi_az                = var.multi_az
  publicly_accessible     = false
  skip_final_snapshot     = var.environment == "dev"
  backup_retention_period = var.environment == "prod" ? 7 : 1
  deletion_protection     = var.environment == "prod"
  tags                    = { Name = "${var.project_name}-${var.environment}-postgres", Environment = var.environment }
}
