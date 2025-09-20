# API Gateway endpoint
output "api_endpoint" {
    value = aws_apigatewayv2_api.list_service_http_api.api_endpoint
    description = "The HTTP API endpoint for the ListService API"
}
