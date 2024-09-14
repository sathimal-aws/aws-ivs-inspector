# - USER POOL -
resource "aws_cognito_user_pool" "user_pool" {
  name = "${var.project_name}-${var.user_pool_name}"
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  alias_attributes         = ["email"] // alows users to sign-in with either username or email address
  auto_verified_attributes = ["email"] // disable this if you set email_verification_message and subject

  admin_create_user_config {
    allow_admin_create_user_only = false
    invite_message_template {
      email_message = var.invite_email_message
      email_subject = var.invite_email_subject
      sms_message   = var.invite_sms_message
    }
  }
  password_policy {
    minimum_length    = 6
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  # General Schema
  dynamic "schema" {
    for_each = var.schemas == null ? [] : var.schemas
    content {
      name                     = lookup(schema.value, "name")
      attribute_data_type      = lookup(schema.value, "attribute_data_type")
      required                 = lookup(schema.value, "required")
      mutable                  = lookup(schema.value, "mutable")
      developer_only_attribute = lookup(schema.value, "developer_only_attribute")
    }
  }

  # Schema (String)
  dynamic "schema" {
    for_each = var.string_schemas == null ? [] : var.string_schemas
    content {
      name                     = lookup(schema.value, "name")
      attribute_data_type      = lookup(schema.value, "attribute_data_type")
      required                 = lookup(schema.value, "required")
      mutable                  = lookup(schema.value, "mutable")
      developer_only_attribute = lookup(schema.value, "developer_only_attribute")

      # string_attribute_constraints
      dynamic "string_attribute_constraints" {
        for_each = length(lookup(schema.value, "string_attribute_constraints")) == 0 ? [] : [lookup(schema.value, "string_attribute_constraints", {})]
        content {
          min_length = lookup(string_attribute_constraints.value, "min_length", 0)
          max_length = lookup(string_attribute_constraints.value, "max_length", 0)
        }
      }
    }
  }

  # Schema (Number)
  dynamic "schema" {
    for_each = var.number_schemas == null ? [] : var.number_schemas
    content {
      name                     = lookup(schema.value, "name")
      attribute_data_type      = lookup(schema.value, "attribute_data_type")
      required                 = lookup(schema.value, "required")
      mutable                  = lookup(schema.value, "mutable")
      developer_only_attribute = lookup(schema.value, "developer_only_attribute")

      # number_attribute_constraints
      dynamic "number_attribute_constraints" {
        for_each = length(lookup(schema.value, "number_attribute_constraints")) == 0 ? [] : [lookup(schema.value, "number_attribute_constraints", {})]
        content {
          min_value = lookup(number_attribute_constraints.value, "min_value", 0)
          max_value = lookup(number_attribute_constraints.value, "max_value", 0)
        }
      }
    }
  }

  tags = merge(
    {
      "AppName" = var.project_name
    },
    var.tags,
  )
}

# Cognito User Pool Client
resource "aws_cognito_user_pool_client" "user_pool_client" {
  name                                 = var.user_pool_client_name
  user_pool_id                         = aws_cognito_user_pool.user_pool.id
  supported_identity_providers         = ["COGNITO"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code", "implicit"]
  allowed_oauth_scopes                 = ["aws.cognito.signin.user.admin"]
  explicit_auth_flows                  = ["ADMIN_NO_SRP_AUTH", "USER_PASSWORD_AUTH"]
  callback_urls                        = ["https://main.${aws_amplify_app.app.id}.amplifyapp.com"]
  prevent_user_existence_errors        = "ENABLED"
  depends_on                           = [aws_amplify_app.app]
}

# Cognito Identity Pool
resource "aws_cognito_identity_pool" "identity_pool" {
  identity_pool_name               = var.identity_pool_name
  allow_unauthenticated_identities = var.identity_pool_allow_unauthenticated_identites
  allow_classic_flow               = var.identity_pool_allow_classic_flow

  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.user_pool_client.id
    provider_name           = "cognito-idp.${data.aws_region.current.name}.amazonaws.com/${aws_cognito_user_pool.user_pool.id}"
    server_side_token_check = false
  }
}

# Cognito Identity Pool Roles Attachments
resource "aws_cognito_identity_pool_roles_attachment" "identity_pool_auth_roles_attachment" {
  identity_pool_id = aws_cognito_identity_pool.identity_pool.id

  role_mapping {
    identity_provider         = "cognito-idp.${data.aws_region.current.id}.amazonaws.com/${aws_cognito_user_pool.user_pool.id}:${aws_cognito_user_pool_client.user_pool_client.id}"
    ambiguous_role_resolution = "Deny"
    type                      = "Rules"

    mapping_rule {
      claim = "cognito:groups" // claim that is in token for cognito users in groups
      # Set this to "Contains" if users will potentially be in more than one group
      match_type = "Contains" // Valid values are "Equals", "Contains", "StartsWith", and "NotEqual"
      # role_arn   = var.create_full_access_roles ? aws_iam_role.cognito_admin_group_full_access[0].arn : aws_iam_role.cognito_admin_group_restricted_access[0].arn
      role_arn = aws_iam_role.cognito_admin_group_restricted_access[0].arn
      value    = "Admin" // group name. Claim/value = cognito:groups/Admin
    }
    mapping_rule {
      claim = "cognito:groups" // claim that is in token for cognito users in groups
      # Set this to "Contains" if users will potentially be in more than one group
      match_type = "Contains" // Valid values are "Equals", "Contains", "StartsWith", and "NotEqual"
      role_arn   = aws_iam_role.cognito_standard_group_restricted_access[0].arn
      value      = "Standard" // group name. Claim/value = cognito:groups/Standard
    }
  }

  # IAM Roles for users who are not in any groups
  roles = {
    "authenticated"   = aws_iam_role.cognito_authrole_restricted_access[0].arn
    "unauthenticated" = aws_iam_role.cognito_unauthrole_restricted_access[0].arn
  }
}

# - COGNITO USERS -
# Users
resource "aws_cognito_user" "cognito_users" {
  for_each     = var.cognito_users != null ? var.cognito_users : {}
  user_pool_id = aws_cognito_user_pool.user_pool.id

  # username = each.value.email
  username = each.value.username
  password = each.value.password

  attributes = {
    email          = each.value.email
    given_name     = each.value.given_name
    family_name    = each.value.family_name
    email_verified = true
  }
}

# Groups
resource "aws_cognito_user_group" "cognito_user_groups" {
  for_each     = var.cognito_groups == null ? {} : var.cognito_groups
  user_pool_id = aws_cognito_user_pool.user_pool.id
  name         = each.value.name
  description  = each.value.description
  precedence   = 1
  role_arn     = each.value.name == "Admin" ? aws_iam_role.cognito_admin_group_restricted_access[0].arn : aws_iam_role.cognito_standard_group_restricted_access[0].arn
}

# Admin User Group Association
resource "aws_cognito_user_in_group" "cognito_user_group_memberships" {
  for_each     = local.users_and_their_groups
  user_pool_id = aws_cognito_user_pool.user_pool.id
  group_name   = each.value.group_name
  username     = each.value.username
  depends_on = [
    aws_cognito_user.cognito_users,
    aws_cognito_user_group.cognito_user_groups,
  ]
}




