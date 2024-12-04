# ApiGateway rest api execution permission to Lambda
resource "aws_lambda_permission" "apigw_execute_lambda" {
  for_each      = { for api in var.rest_apis : api.name => api }
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function[each.key].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.rest_api.execution_arn}/*"
}

# ApiGateway websock api execution permission to Lambda
resource "aws_lambda_permission" "apigw_wss_execute_lambda" {
  for_each      = { for api in var.wss_api_routes : api.name => api }
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function[each.key].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${aws_apigatewayv2_api.wss_api[each.value.parent_id].id}/*/*"
  depends_on    = [aws_lambda_function.lambda_function]
}

# EventBridge execution permission to Lambda
resource "aws_lambda_permission" "eventbridge_execute_lambda" {
  for_each      = { for rule in var.rules : rule.name => rule }
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function["eventbridge-triggers"].function_name
  principal     = "events.amazonaws.com"
  source_arn    = "arn:aws:events:${var.region}:${var.account_id}:rule/${var.project_name}-${each.value.name}"
  depends_on    = [aws_cloudwatch_event_rule.rule]
}

# deploy lambda function
resource "aws_lambda_function" "lambda_function" {
  for_each         = { for lambda in var.lambdas : lambda.name => lambda }
  function_name    = "${var.project_name}-${var.region}-${each.key}"
  filename         = "./functions/${each.key}.zip"
  runtime          = "python3.9"
  handler          = "${each.key}.lambda_handler"
  timeout          = each.value.timeout
  memory_size      = 2048
  role             = aws_iam_role.iam_role[each.key].arn
  source_code_hash = data.archive_file.lambda_archive_file[each.key].output_base64sha256

  environment {
    variables = {
      project_name                  = var.project_name
      region                        = var.region
      wss_get_live_streams_api_id   = aws_apigatewayv2_stage.stage["get-live-streams"].api_id
      wss_get_session_events_api_id = aws_apigatewayv2_stage.stage["get-session-events"].api_id
      vpc_subnets                   = jsonencode(aws_subnet.private[*].id)
      vpc_security_groups           = aws_security_group.ecs_tasks.id
      ecs_task_definition_revision  = aws_ecs_task_definition.task.revision
    }
  }
  depends_on = [
    aws_iam_role.iam_role,
    aws_subnet.private,
    aws_ecs_task_definition.task,
    aws_apigatewayv2_stage.stage
  ]
}
