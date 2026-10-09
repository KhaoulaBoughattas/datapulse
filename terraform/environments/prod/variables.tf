variable "aws_region" {
  type    = string
  default = "us-east-1"
}
variable "azs" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}
variable "backend_image" {
  type = string
}
variable "frontend_image" {
  type = string
}
