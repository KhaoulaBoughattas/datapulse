variable "project_name" { type = string }
variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "public_subnet_ids" { type = list(string) }
variable "private_subnet_ids" { type = list(string) }
variable "alb_security_group_id" { type = string }
variable "ecs_security_group_id" { type = string }
variable "ecs_execution_role_arn" { type = string }
variable "ecs_task_role_arn" { type = string }
variable "db_secret_arn" { type = string }
variable "jwt_secret_arn" { type = string }
variable "backend_image" { type = string }
variable "frontend_image" { type = string }
variable "backend_cpu" {
  type    = number
  default = 256
}
variable "backend_memory" {
  type    = number
  default = 512
}
variable "backend_desired_count" {
  type    = number
  default = 1
}
