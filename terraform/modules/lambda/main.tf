resource "aws_security_group" "lambda" {
  name_prefix = "${var.environment}-lambda-"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-lambda-sg"
    }
  )
}

resource "aws_iam_role" "lambda" {
  name = "${var.environment}-parking-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy" "lambda_msk" {
  name = "${var.environment}-lambda-msk-policy"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kafka:DescribeCluster",
          "kafka:GetBootstrapBrokers",
          "kafka:ListScramSecrets"
        ]
        Resource = [var.msk_cluster_arn]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_bucket}",
          "arn:aws:s3:::${var.s3_bucket}/*"
        ]
      }
    ]
  })
}

resource "aws_lambda_function" "parking_processor" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.environment}-parking-processor"
  role            = aws_iam_role.lambda.arn
  handler         = "index.handler"
  runtime         = "python3.9"
  timeout         = 300
  memory_size     = 256

  vpc_config {
    subnet_ids         = var.private_subnets
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      TOPIC_NAME = var.kafka_topic
      S3_BUCKET = var.s3_bucket
    }
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-parking-processor"
    }
  )
}

resource "aws_lambda_event_source_mapping" "msk" {
  event_source_arn  = var.msk_cluster_arn
  function_name     = aws_lambda_function.parking_processor.arn
  topics           = [var.kafka_topic]
  starting_position = "LATEST"

  scaling_config {
    maximum_concurrency = 10
  }
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../../lambda/ingestion"
  output_path = "${path.module}/lambda.zip"
} 