locals {
  # Create a new local variable by flattening the complex type given in the variable "cognito_users"
  flatten_user_data = flatten([
    for user in keys(var.cognito_users) : [
      for group in var.cognito_users[user].group_membership : {
        username   = var.cognito_users[user].username
        group_name = group
      }
    ]
  ])

  users_and_their_groups = {
    for s in local.flatten_user_data : format("%s_%s", s.username, s.group_name) => s
  }
}
