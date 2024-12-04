data "aws_caller_identity" "current" {}

data "aws_ecr_authorization_token" "token" {}

data "aws_iam_policy_document" "trust_policy" {
  for_each = { for role in var.assume_roles : role.name => role }
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = each.value.assume_role
    }
  }
}

# Dynamic IAM policies and attach to lambda functions
data "aws_iam_policy_document" "service_policy" {
  for_each = { for policy in local.policies : policy.name => policy }
  dynamic "statement" {
    for_each = { for idx, statement in each.value.statements : idx => statement }
    content {
      effect    = statement.value["effect"]
      actions   = statement.value["actions"]
      resources = statement.value["resources"]
    }
  }
}

# ECS task trust & service policy
data "aws_iam_policy_document" "ecs_task_trust_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "ecs_task_service_policy" {
  for_each = { for policy in local.ecs_task_execution_policy : policy.name => policy }
  dynamic "statement" {
    for_each = { for idx, statement in each.value.statements : idx => statement }
    content {
      effect    = statement.value["effect"]
      actions   = statement.value["actions"]
      resources = statement.value["resources"]
    }
  }
}

data "aws_vpc" "vpc" {
  count = var.vpc_id == null ? 0 : 1
  id    = var.vpc_id
}

# archive (zip) the lambda function
data "archive_file" "lambda_archive_file" {
  for_each    = { for lambda in var.lambdas : lambda.name => lambda }
  type        = "zip"
  source_file = "./functions/${each.key}.py"
  output_path = "./functions/${each.key}.zip"
}
