variable "region" {
  type    = string
  default = null
}

variable "project_name" {
  type    = string
  default = "ivs-inspector"
}

variable "environment" {
  type    = string
  default = "ivs"
}

variable "repository" {
  type        = string
  description = "Web Application Repo"
  default     = null
}

variable "token" {
  type        = string
  description = "github token to connect github repo"
  default     = null
  sensitive   = true
}

variable "branch_name" {
  type        = string
  description = "IVS Branch"
  default     = "main"
}

variable "domain_name" {
  type        = string
  default     = "awsivsinspector.com"
  description = "AWS Amplify Domain Name"
}

variable "path_to_build_spec" {
  type    = string
  default = "../amplify.yml"
}


# - Cognito -
# User Pool
variable "user_pool_name" {
  type        = string
  default     = "user_pool"
  description = "The name of the Cognito User Pool created"
}
variable "user_pool_client_name" {
  type        = string
  default     = "user_pool_client"
  description = "The name of the Cognito User Pool Client created"
}
variable "identity_pool_name" {
  type        = string
  default     = "identity_pool"
  description = "The name of the Cognito Identity Pool created"
}

variable "identity_pool_allow_unauthenticated_identites" {
  type    = bool
  default = false
}

variable "identity_pool_allow_classic_flow" {
  type    = bool
  default = false

}

variable "email_verification_message" {
  type        = string
  default     = <<-EOF

  Thank you for registering with the IVS Inspector. This is your email confirmation.
  Verification Code: {####}

  EOF
  description = "The Cognito email verification message"
}

variable "email_verification_subject" {
  type        = string
  default     = "IVS Inspector Verification"
  description = "The Cognito email verification subject"
}

variable "invite_email_message" {
  type    = string
  default = <<-EOF
    You have been invited to the IVS Inspector App! Your username is "{username}" and
    temporary password is "{####}". Please reach out to an admin if you have issues signing in.
  EOF
}

variable "invite_email_subject" {
  type    = string
  default = <<-EOF
  Welcome to the IVS Inspector!
  EOF
}

variable "invite_sms_message" {
  type    = string
  default = <<-EOF
    You have been invited to the IVS Inspector! Your username is "{username}" and
    temporary password is "{####}".
  EOF
}

# General Schema
variable "schemas" {
  description = "A container with the schema attributes of a user pool. Maximum of 50 attributes"
  type        = list(any)
  default     = []
}

# Schema (String)
variable "string_schemas" {
  description = "A container with the string schema attributes of a user pool. Maximum of 50 attributes"
  type        = list(any)
  default = [{
    name                     = "email"
    attribute_data_type      = "String"
    required                 = true
    mutable                  = false
    developer_only_attribute = false

    string_attribute_constraints = {
      min_length = 7
      max_length = 60
    }
    },
    {
      name                     = "given_name"
      attribute_data_type      = "String"
      required                 = true
      mutable                  = true
      developer_only_attribute = false

      string_attribute_constraints = {
        min_length = 1
        max_length = 25
      }
    },
    {
      name                     = "family_name"
      attribute_data_type      = "String"
      required                 = true
      mutable                  = true
      developer_only_attribute = false

      string_attribute_constraints = {
        min_length = 1
        max_length = 25
      }
    },
    {
      name                     = "IAC_PROVIDER"
      attribute_data_type      = "String"
      required                 = false
      mutable                  = true
      developer_only_attribute = false

      string_attribute_constraints = {
        min_length = 1
        max_length = 10
      }
    },
  ]
}

# Schema (number)
variable "number_schemas" {
  description = "A container with the number schema attributes of a user pool. Maximum of 50 attributes"
  type        = list(any)
  default     = []
}

# Groups
variable "cognito_groups" {
  type = map(object({
    name        = string,
    description = optional(string, ""),
  }))
  description = "Collection of AWS IVS User Pool Groups you wish to create."
  default = {
    Admin : {
      name        = "Admin"
      description = "Admin users"
    },
    Streamers : {
      name        = "Streamers"
      description = "IVS Streamers"
    },
  }

}

# Users
variable "cognito_users" {
  type = map(object({
    username         = string,
    given_name       = string,
    family_name      = string,
    email            = string,
    password         = string,
    email_verified   = optional(bool, true),
    group_membership = optional(list(string), ["admin"])

  }))
  description = "Collection of Amazon Cognito Users you wish to create"
  default = {
    Admin : {
      username         = "admin"
      given_name       = "ivs inspector"
      family_name      = "aws"
      email            = "admin@ivs-inspector.com"
      password         = "123Qwe,./"
      email_verified   = true
      group_membership = ["Admin", "Streamers"]
    },
  }
}

# IAM
variable "create_restricted_access_roles" {
  type        = bool
  default     = true
  description = "Conditional creation of restricted access roles"
}

variable "tags" {
  type        = map(any)
  description = "Tags to apply to resources"
  default = {
    "IAC_PROVIDER" = "Terraform"
  }
}
