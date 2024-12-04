# create cloudwatch log group for lambda
resource "aws_cloudwatch_log_group" "cloudwatch_logs" {
  for_each          = { for lambda in var.lambdas : lambda.name => lambda }
  name              = "/aws/lambda/${aws_lambda_function.lambda_function[each.key].function_name}"
  retention_in_days = 14
}
