# create api
resource "aws_api_gateway_rest_api" "rest_api" {
  name        = "${var.project_name}-rest-api"
  description = "All ${var.project_name} get methods fans out from this single APIs"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# create resource (path)
resource "aws_api_gateway_resource" "resource" {
  for_each    = { for api in var.rest_apis : api.name => api }
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  parent_id   = aws_api_gateway_rest_api.rest_api.root_resource_id
  path_part   = each.key
}

# create method
resource "aws_api_gateway_method" "method" {
  for_each      = { for api in var.rest_apis : api.name => api }
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  resource_id   = aws_api_gateway_resource.resource[each.key].id
  http_method   = each.value.http_method
  authorization = "NONE"
}

# integrate with Lambda
resource "aws_api_gateway_integration" "integration" {
  for_each                = { for api in var.rest_apis : api.name => api }
  rest_api_id             = aws_api_gateway_rest_api.rest_api.id
  resource_id             = aws_api_gateway_resource.resource[each.key].id
  http_method             = aws_api_gateway_method.method[each.key].http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  timeout_milliseconds    = 29000
  uri                     = aws_lambda_function.lambda_function[each.key].invoke_arn
  depends_on = [
    aws_api_gateway_method.method,
    aws_lambda_function.lambda_function
  ]
}

# integration response from Lambda
resource "aws_api_gateway_integration_response" "integration_response" {
  for_each    = { for api in var.rest_apis : api.name => api }
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  resource_id = aws_api_gateway_resource.resource[each.key].id
  http_method = aws_api_gateway_method.method[each.key].http_method
  status_code = aws_api_gateway_method_response.method_response[each.key].status_code
  depends_on = [
    aws_api_gateway_method.method,
    aws_api_gateway_integration.integration
  ]
}

# method response from Lambda that passes back to Client application
resource "aws_api_gateway_method_response" "method_response" {
  for_each    = { for api in var.rest_apis : api.name => api }
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  resource_id = aws_api_gateway_resource.resource[each.key].id
  http_method = aws_api_gateway_method.method[each.key].http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
  depends_on = [
    aws_api_gateway_method.method,
    aws_api_gateway_integration.integration
  ]
}

# deploy the API
resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  stage_name  = var.environment
  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.rest_api.body))
  }
  lifecycle {
    create_before_destroy = true
  }
  description = "Deployed at ${timestamp()}"

  depends_on = [
    aws_api_gateway_method.method,
    aws_api_gateway_method_response.method_response,
    aws_api_gateway_integration.integration,
    aws_api_gateway_integration_response.integration_response,
    aws_lambda_function.lambda_function,
  ]
}

resource "aws_api_gateway_method_settings" "method_settings" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  stage_name  = aws_api_gateway_deployment.deployment.stage_name
  method_path = "*/*"
  settings {
    throttling_burst_limit = 4999
    throttling_rate_limit  = 9999
  }
}
