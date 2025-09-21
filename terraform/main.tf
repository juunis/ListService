terraform {
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
}

provider "aws" {
    region = var.aws_region
}

# IAM Role for Lambda
resource "aws_iam_role" "listservice_lambda_role" {
    name = "listservice-lambda-role"

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [{
            Action    = "sts:AssumeRole"
            Effect    = "Allow"
            Principal = { Service = "lambda.amazonaws.com" }
        }]
    })
}

# Lambda Logging Policy
resource "aws_iam_role_policy" "listservice_lambda_logs_policy" {
    name = "listservice-lambda-logs"
    role = aws_iam_role.listservice_lambda_role.id

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Action = [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ]
                Resource = "arn:aws:logs:*:*:log-group:/aws/lambda/ListService:*"
            }
        ]
    })
}

# Lambda Log Group
resource "aws_cloudwatch_log_group" "listservice_log_group" {
    name = "/aws/lambda/ListService"
}

# Zip Lambda Code
data "archive_file" "list_service_lambda_zip" {
    type = "zip"
    source_file = "../lambda/list_service.py"
    output_path = "list_service.zip"
}

# ListService Lambda Function
resource "aws_lambda_function" "list_service_lambda" {
    function_name = "ListService"
    filename      = data.archive_file.list_service_lambda_zip.output_path
    role          = aws_iam_role.listservice_lambda_role.arn
    handler       = "list_service.lambda_handler"
    runtime       = "python3.13"

    depends_on = [
        aws_cloudwatch_log_group.listservice_log_group
    ]
}

# API Gateway HTTP API
resource "aws_apigatewayv2_api" "list_service_http_api" {
    name          = "ListServiceAPI"
    protocol_type = "HTTP"
}

# Lambda Integration
resource "aws_apigatewayv2_integration" "lambda_integration" {
    api_id                 = aws_apigatewayv2_api.list_service_http_api.id
    integration_type       = "AWS_PROXY"
    integration_uri        = aws_lambda_function.list_service_lambda.invoke_arn
    payload_format_version = "2.0"
}

# Routes
resource "aws_apigatewayv2_route" "head_route" {
    api_id    = aws_apigatewayv2_api.list_service_http_api.id
    route_key = "POST /head"
    target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "tail_route" {
    api_id    = aws_apigatewayv2_api.list_service_http_api.id
    route_key = "POST /tail"
    target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Default Stage
resource "aws_apigatewayv2_stage" "default" {
    api_id      = aws_apigatewayv2_api.list_service_http_api.id
    name        = "$default"
    auto_deploy = true
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "apigw_invoke_lambda_permission" {
    statement_id  = "AllowAPIGatewayInvoke"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.list_service_lambda.function_name
    principal     = "apigateway.amazonaws.com"
    source_arn    = "${aws_apigatewayv2_api.list_service_http_api.execution_arn}/*/*"
}
