resource "aws_security_group" "msk" {
  name_prefix = "${var.environment}-msk-"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 9092
    to_port     = 9092
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.selected.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-msk-sg"
    }
  )
}

resource "aws_msk_cluster" "main" {
  cluster_name           = "${var.environment}-parking-cluster"
  kafka_version         = var.kafka_version
  number_of_broker_nodes = var.broker_nodes

  broker_node_group_info {
    instance_type   = var.instance_type
    client_subnets  = var.private_subnets
    security_groups = [aws_security_group.msk.id]

    storage_info {
      ebs_storage_info {
        volume_size = 100
      }
    }
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }

  configuration_info {
    arn      = aws_msk_configuration.main.arn
    revision = aws_msk_configuration.main.latest_revision
  }

  logging_info {
    broker_logs {
      cloudwatch_logs {
        enabled   = true
        log_group = aws_cloudwatch_log_group.msk.name
      }
    }
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-msk-cluster"
    }
  )
}

resource "aws_msk_configuration" "main" {
  name              = "${var.environment}-parking-config"
  kafka_versions    = [var.kafka_version]
  server_properties = <<PROPERTIES
auto.create.topics.enable=true
delete.topic.enable=true
default.replication.factor=2
min.insync.replicas=2
num.partitions=6
PROPERTIES
}

resource "aws_cloudwatch_log_group" "msk" {
  name              = "/aws/msk/${var.environment}-parking-cluster"
  retention_in_days = 7

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-msk-logs"
    }
  )
}

data "aws_vpc" "selected" {
  id = var.vpc_id
} 