# ListService

A **serverless AWS Lambda** application providing a simple REST API to perform list operations (**head** and **tail**) on arrays of strings. The infrastructure is defined using **Terraform** and the Lambda is written in **Python 3.13**.

## Features

- Head: Returns the first item of a list.
- Tail: Returns all items except the first one.
- Method: Only supports ```POST``` requests.
- Validation: Ensures that the method is ```POST``` and that the input is a non-empty list of strings.
- Serverless Architecture: Lambda + API Gateway HTTP API.

## Prerequisites (macOS)

### AWS CLI

AWS CLI Installation:
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

If installing via Homebrew:\
```brew install awscli```

Configure credentials:\
```aws configure```

Verify configuration:\
```aws sts get-caller-identity```

### Terraform

```
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

### Python (3.10+ recommended)

```python3 --version```

https://www.python.org/downloads/

### pip
```python3 -m pip install --upgrade pip```

### pytest (for local testing)
```python3 -m pip install --upgrade pytest```

# Setup

### Clone Repository:
```git clone https://github.com/juunis/ListService.git```

# Local Testing

Run tests with pytest:

```pytest -v tests/```

Tests cover /head and /tail routes, empty lists, empty strings, invalid types and invalid methods.

# Terraform Deployment

AWS deployment region can be set by changing the **aws_region** variable in ``terraform.tfvars``.

1. Initialize Terraform\
```cd terraform```\
```terraform init```

2. Validate:\
```terraform validate```

3. Plan deployment:\
```terraform plan```

4. Apply deployment:\
```terraform apply```

5. After applying Terraform, note the ```api_endpoint``` output — this is the base URL for API calls.

# API Usage

### Using with HTTP/API Client (Insomnia, Postman etc)

The API Gateway endpoint can be retrieved from the ```api_endpoint``` Terraform output.

### POST /head

#### Request Body:
```
{
  "data": ["a", "b", "c"]
}
```
#### Response (200 OK):
```
{
  "head": "a"
}
```

### POST /tail

#### Request Body:
```
{
  "data": ["a", "b", "c"]
}
```

#### Response (200 OK):
```
{
  "tail": ["b", "c"]
}
```

## Example Requests Using Curl

Replace ``<api_endpoint>`` with the API Gateway endpoint from the ```api_endpoint``` Terraform output.

#### POST /head

Request:
```
curl -X POST <api_endpoint>/head \
     -H "Content-Type: application/json" \
     -d '{"data": ["a", "b", "c"]}'
```

### POST /tail

Request:
```
curl -X POST <api_endpoint>/tail \
     -H "Content-Type: application/json" \
     -d '{"data": ["a", "b", "c"]}'
```

# Errors

| Scenario | Status Code | Example Response |
| -------- | ----------- | ---------------- |
| Empty list | 400 | ```{"ERROR": "Data must be a non-empty list of strings"}``` |
| Empty string in list| 400 | ```{"ERROR": "List cannot contain empty or whitespace strings"}``` |
| Invalid string in list | 400 | ```{"ERROR": "All items in list must be strings"}``` |
| Unsupported HTTP method | 405 | ```{"ERROR": Invalid method. Only POST is supported.}``` |
| Unknown route | 404 | ```{"ERROR": Route not found}``` |

# Resource Cleanup

Remove all resources created by Terraform when finished testing:

```terraform destroy```

# Ideas for Further Development

- Testing improvements: Improve the testing with integration tests using pytest and local API Gateway/Lambda mocks.

- Error monitoring: Integrate with CloudWatch Alarms for monitoring.

- CI/CD pipeline: Automate deployments with GitHub Actions.

- Authentication: Restrict API access with JWT authorizer (such as AWS Cognito).

- Custom domain name: Map the API Gateway endpoint to a custom domain with AWS Route 53 and SSL certificates.