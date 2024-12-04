resource "local_file" "tf_outputs" {
  filename = "${path.root}/${var.project_name}/.env"
  content  = <<-EOF
    VITE_REGION=${data.aws_region.current.name}
    VITE_IDENTITY_POOL_ID=${aws_cognito_identity_pool.identity_pool.id}
    VITE_USER_POOL_ID=${aws_cognito_user_pool.user_pool.id}
    VITE_APP_CLIENT_ID=${aws_cognito_user_pool_client.user_pool_client.id}
    EOF
}
