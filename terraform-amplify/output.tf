output "amplify_app_id" {
  value = aws_amplify_app.app.id
}

output "cognito_identity_pool_id" {
  value = aws_cognito_identity_pool.identity_pool.id
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.user_pool.id
}

output "cognito_ids" {
  value = jsonencode({
    IDENTITY_POOL_ID : aws_cognito_identity_pool.identity_pool.id,
    USER_POOL_ID : aws_cognito_user_pool.user_pool.id,
    APP_CLIENT_ID : aws_cognito_user_pool_client.user_pool_client.id,
    REGION : var.region
  })
}
