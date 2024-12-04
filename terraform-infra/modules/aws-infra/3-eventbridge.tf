# EventBridge
resource "aws_cloudwatch_event_rule" "rule" {
  for_each    = { for rule in var.rules : rule.name => rule }
  name        = "${var.project_name}-${each.value.name}"
  description = each.value.description
  event_pattern = jsonencode({
    "source" : ["${each.value.source}"],
    "detail-type" : ["${each.value.detail-type}"]
  })
  tags = {
    key   = each.key
    value = each.value.name
  }
}

resource "aws_cloudwatch_event_target" "target" {
  for_each = { for rule in var.rules : rule.name => rule }
  arn      = aws_lambda_function.lambda_function["eventbridge-triggers"].arn
  rule     = "${var.project_name}-${each.value.name}"
  depends_on = [
    aws_lambda_function.lambda_function
  ]
}
