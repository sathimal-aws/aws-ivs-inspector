variable "account_id" {
  type    = string
  default = null
}

variable "region" {
  type    = string
  default = null
}

variable "project_name" {
  type    = string
  default = "ivs-inspector"
}

variable "cognito_user_pool_id" {
  type = string
}

variable "cognito_identity_pool_id" {
  type = string
}

variable "cognito_region" {
  type = string
}

variable "environment" {
  type    = string
  default = "ivs"
}
