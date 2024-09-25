resource "aws_apigatewayv2_api" "wss_api" {
  for_each                   = var.wss_apis
  name                       = "${var.project_name}-wss-api-${each.key}"
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"
}

# integrate with Lambda
resource "aws_apigatewayv2_integration" "integration" {
  for_each                  = { for api in var.wss_api_routes : api.name => api }
  api_id                    = aws_apigatewayv2_api.wss_api[each.value.parent_id].id
  integration_type          = "AWS_PROXY"
  integration_method        = "POST"
  integration_uri           = aws_lambda_function.lambda_function[each.key].invoke_arn
  credentials_arn           = aws_iam_role.iam_role[each.key].arn
  content_handling_strategy = "CONVERT_TO_TEXT"
  passthrough_behavior      = "WHEN_NO_MATCH"
}

# integration response from Lambda
resource "aws_apigatewayv2_integration_response" "integration_response" {
  for_each                 = { for api in var.wss_api_routes : api.name => api }
  api_id                   = aws_apigatewayv2_api.wss_api[each.value.parent_id].id
  integration_id           = aws_apigatewayv2_integration.integration[each.key].id
  integration_response_key = "/200/"
}

# route
resource "aws_apigatewayv2_route" "route" {
  for_each  = { for api in var.wss_api_routes : api.name => api }
  api_id    = aws_apigatewayv2_api.wss_api[each.value.parent_id].id
  route_key = each.value.route_key
  target    = "integrations/${aws_apigatewayv2_integration.integration[each.key].id}"
}

resource "aws_apigatewayv2_route_response" "route_response" {
  for_each           = { for api in var.wss_api_routes : api.name => api }
  api_id             = aws_apigatewayv2_api.wss_api[each.value.parent_id].id
  route_id           = aws_apigatewayv2_route.route[each.key].id
  route_response_key = "$default"
}

# stage the API
resource "aws_apigatewayv2_stage" "stage" {
  for_each    = var.wss_apis
  api_id      = aws_apigatewayv2_api.wss_api[each.key].id
  name        = "ivs"
  auto_deploy = true
  default_route_settings {
    throttling_rate_limit  = 9999
    throttling_burst_limit = 4999
  }
}
