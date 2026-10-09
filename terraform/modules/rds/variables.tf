variable "project_name" { type = string }
variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "rds_security_group_id" { type = string }
variable "instance_class" {
  type    = string
  default = "db.t4g.micro"
}
variable "allocated_storage" {
  type    = number
  default = 20
}
variable "multi_az" {
  type    = bool
  default = false
}
variable "db_name" {
  type    = string
  default = "datapulse"
}
variable "master_username" {
  type    = string
  default = "datapulse_admin"
}
