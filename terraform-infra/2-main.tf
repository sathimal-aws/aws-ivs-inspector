module "aws-infra" {
  source                   = "./modules/aws-infra"
  project_name             = var.project_name
  environment              = var.environment
  account_id               = var.account_id
  region                   = var.region
  cognito_user_pool_id     = var.cognito_user_pool_id
  cognito_identity_pool_id = var.cognito_identity_pool_id
  cognito_region           = var.cognito_region
}
