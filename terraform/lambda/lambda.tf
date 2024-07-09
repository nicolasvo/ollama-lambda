resource "aws_cloudwatch_log_group" "ollama" {
  name = "/aws/lambda/${aws_lambda_function.ollama.function_name}"

  retention_in_days = 7
}

resource "aws_lambda_function" "ollama" {
  function_name = "ollama"
  memory_size   = 10240
  timeout       = 900
  package_type  = "Image"
  architectures = ["x86_64"]
  image_uri     = "${data.terraform_remote_state.ecr.outputs.repository_url_ollama}:${var.image_tag_ollama}"

  role = aws_iam_role.lambda.arn

  ephemeral_storage {
    size = 1000
  }
}

resource "aws_lambda_function_url" "ollama" {
  function_name      = aws_lambda_function.ollama.function_name
  authorization_type = "NONE"
  invoke_mode        = "RESPONSE_STREAM"
}

data "aws_iam_policy_document" "lambda" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "ollama"
  assume_role_policy = data.aws_iam_policy_document.lambda.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
  ]
}
