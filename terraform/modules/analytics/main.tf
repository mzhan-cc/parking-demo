resource "aws_glue_catalog_database" "parking" {
  name = "${var.environment}_${var.database_name}"
}

resource "aws_glue_crawler" "parking" {
  database_name = aws_glue_catalog_database.parking.name
  name          = "${var.environment}-parking-crawler"
  role          = aws_iam_role.glue.arn

  s3_target {
    path = "s3://${var.s3_bucket}/parking-data/"
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  configuration = jsonencode({
    Version = 1.0
    CrawlerOutput = {
      Partitions = { AddOrUpdateBehavior = "InheritFromTable" }
    }
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-parking-crawler"
    }
  )
}

resource "aws_iam_role" "glue" {
  name = "${var.environment}-glue-crawler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy" "glue_s3" {
  name = "${var.environment}-glue-s3-policy"
  role = aws_iam_role.glue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
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

resource "aws_athena_workgroup" "parking" {
  name = "${var.environment}-parking-analytics"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${var.s3_bucket}/athena-results/"
    }
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-parking-analytics"
    }
  )
} 