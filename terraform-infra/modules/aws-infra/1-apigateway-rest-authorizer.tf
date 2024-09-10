# # authorize api requests
# resource "aws_api_gateway_authorizer" "authorizer" {
#   name                   = "${var.project_name}-request-authorizer"
#   rest_api_id            = aws_api_gateway_rest_api.rest_api_authorizer.id
#   authorizer_uri         = aws_lambda_function.lambda_function["user-authorizer"].invoke_arn
#   authorizer_credentials = aws_iam_role.iam_role["api-gateway-auth-invocation"].arn
# }

# # create api
# resource "aws_api_gateway_rest_api" "rest_api_authorizer" {
#   name        = "${var.project_name}-rest-authorizer-api"
#   description = "${var.project_name} REST API for authorization"
#   endpoint_configuration {
#     types = ["REGIONAL"]
#   }
# }

# # create resource (path)
# resource "aws_api_gateway_resource" "resource_authorizer" {
#   rest_api_id = aws_api_gateway_rest_api.rest_api_authorizer.id
#   parent_id   = aws_api_gateway_rest_api.rest_api_authorizer.root_resource_id
#   path_part   = "user-authorizer"
# }

# # create method
# resource "aws_api_gateway_method" "method_authorizer" {
#   rest_api_id   = aws_api_gateway_rest_api.rest_api_authorizer.id
#   resource_id   = aws_api_gateway_resource.resource_authorizer.id
#   http_method   = "GET"
#   authorization = "NONE"
# }

# # integrate with Lambda
# resource "aws_api_gateway_integration" "integration_authorizer" {
#   rest_api_id             = aws_api_gateway_rest_api.rest_api_authorizer.id
#   resource_id             = aws_api_gateway_resource.resource_authorizer.id
#   http_method             = aws_api_gateway_method.method_authorizer.http_method
#   integration_http_method = "POST"
#   type                    = "AWS_PROXY"
#   timeout_milliseconds    = 29000
#   uri                     = aws_lambda_function.lambda_function["user-authorizer"].invoke_arn
#   depends_on = [
#     aws_api_gateway_method.method_authorizer,
#     aws_lambda_function.lambda_function
#   ]
# }

# # integration response from Lambda
# resource "aws_api_gateway_integration_response" "integration_response_authorizer" {
#   rest_api_id = aws_api_gateway_rest_api.rest_api_authorizer.id
#   resource_id = aws_api_gateway_resource.resource_authorizer.id
#   http_method = aws_api_gateway_method.method_authorizer.http_method
#   status_code = aws_api_gateway_method_response.method_response_authorizer.status_code
#   depends_on = [
#     aws_api_gateway_method.method_authorizer,
#     aws_api_gateway_integration.integration_authorizer
#   ]
# }

# # method response from Lambda that passes back to Client application
# resource "aws_api_gateway_method_response" "method_response_authorizer" {
#   rest_api_id = aws_api_gateway_rest_api.rest_api_authorizer.id
#   resource_id = aws_api_gateway_resource.resource_authorizer.id
#   http_method = aws_api_gateway_method.method_authorizer.http_method
#   status_code = "200"
#   response_parameters = {
#     "method.response.header.Access-Control-Allow-Origin" = true
#   }
#   depends_on = [
#     aws_api_gateway_method.method_authorizer,
#     aws_api_gateway_integration.integration_authorizer
#   ]
# }

# # deploy the API
# resource "aws_api_gateway_deployment" "deployment_authorizer" {
#   rest_api_id = aws_api_gateway_rest_api.rest_api_authorizer.id
#   stage_name  = var.environment
#   triggers = {
#     redeployment = sha1(jsonencode(aws_api_gateway_rest_api.rest_api_authorizer.body))
#   }
#   lifecycle {
#     create_before_destroy = true
#   }
#   description = "Deployed at ${timestamp()}"

#   depends_on = [
#     aws_api_gateway_method.method_authorizer,
#     aws_api_gateway_method_response.method_response_authorizer,
#     aws_api_gateway_integration.integration_authorizer,
#     aws_api_gateway_integration_response.integration_response_authorizer,
#     aws_lambda_function.lambda_function,
#   ]
# }

# # assign API request throttle limits
# resource "aws_api_gateway_method_settings" "method_settings_authorizer" {
#   rest_api_id = aws_api_gateway_rest_api.rest_api_authorizer.id
#   stage_name  = aws_api_gateway_deployment.deployment_authorizer.stage_name
#   method_path = "*/*"
#   settings {
#     throttling_burst_limit = 4999
#     throttling_rate_limit  = 9999
#   }
# }

# # # lambda function to authorize
# # resource "aws_lambda_function" "lambda_function_authorizer" {
# #   filename      = "lambda-function.zip"
# #   function_name = "api_gateway_authorizer"
# #   role          = aws_iam_role.lambda.arn
# #   handler       = "exports.example"

# #   source_code_hash = filebase64sha256("lambda-function.zip")
# # }

# # # deploy lambda function
# # resource "aws_lambda_function" "lambda_function_authorizer" {
# #   function_name    = "${var.project_name}-${var.region}-user-authorizer"
# #   filename         = "./functions/user-authorizer.zip"
# #   runtime          = "python3.9"
# #   handler          = "user-authorizer.lambda_handler"
# #   timeout          = 30
# #   memory_size      = 2048
# #   role             = aws_iam_role.iam_role["user-authorizer"].arn
# #   source_code_hash = data.archive_file.lambda_archive_file["user-authorizer"].output_base64sha256

# #   depends_on = [
# #     aws_iam_role.iam_role,
# #   ]
# # }
