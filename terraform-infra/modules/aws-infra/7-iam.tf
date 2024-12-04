# IAM role
resource "aws_iam_role" "iam_role" {
  for_each           = { for role in var.assume_roles : role.name => role }
  name               = "${var.project_name}-${var.region}-${each.key}-role"
  assume_role_policy = data.aws_iam_policy_document.trust_policy[each.key].json
}

resource "aws_iam_policy" "iam_policy" {
  for_each    = { for policy in local.policies : policy.name => policy }
  name        = "${var.project_name}-${var.region}-${each.key}-policy"
  description = "${each.key} policy to be attached to the role"
  policy      = data.aws_iam_policy_document.service_policy[each.key].json
}

resource "aws_iam_policy_attachment" "iam_policy_attachment" {
  for_each   = { for policy in local.policies : policy.name => policy }
  name       = each.key
  roles      = [aws_iam_role.iam_role[each.key].name]
  policy_arn = aws_iam_policy.iam_policy[each.key].arn
}

resource "aws_iam_role" "iam_role_ecs_task_execution" {
  name               = "${var.project_name}-${var.region}-ecs-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_trust_policy.json
}

resource "aws_iam_policy" "iam_policy_ecs_task_execution" {
  name        = "${var.project_name}-${var.region}-ecs-task-execution-policy"
  description = "ecs-task-execution policy to be attached to the role"
  policy      = data.aws_iam_policy_document.ecs_task_service_policy["${var.project_name}-${var.region}-ecs-task-execution-policy"].json
}

resource "aws_iam_policy_attachment" "iam_policy_attachment_ecs_task_execution" {
  name       = "ecs_task_execution_policy"
  roles      = [aws_iam_role.iam_role_ecs_task_execution.name]
  policy_arn = aws_iam_policy.iam_policy_ecs_task_execution.arn
}

