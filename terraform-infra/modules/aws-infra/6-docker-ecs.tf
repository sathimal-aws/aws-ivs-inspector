# Build docker images and push to ECR
resource "docker_registry_image" "ingest_metrics" {
  name = "${aws_ecr_repository.repository.repository_url}:latest"
  build {
    context = "${path.cwd}/applications/ingestMetrics"
  }
}

# Create ECR repository
resource "aws_ecr_repository" "repository" {
  name = "${var.project_name}-ingest-metrics"
}

resource "aws_cloudwatch_log_group" "log" {
  name              = "/aws/ecs/${var.project_name}-${var.region}-ingest-metrics"
  retention_in_days = 14
}


# ECS
resource "aws_ecs_cluster" "cluster" {
  name = local.cluster_name
}

resource "aws_ecs_task_definition" "task" {
  family                   = "${var.project_name}-${var.task_family}"
  task_role_arn            = aws_iam_role.iam_role["ingest-metrics-ecs-task"].arn
  execution_role_arn       = aws_iam_role.iam_role["ingest-metrics-ecs-task"].arn
  network_mode             = var.network_mode
  requires_compatibilities = [var.launch_type.type]
  cpu                      = var.launch_type.cpu
  memory                   = var.launch_type.memory
  container_definitions    = local.ecs_task_definition
  depends_on               = [aws_iam_role.iam_role]
}


locals {
  ecs_task_definition = templatefile("./task-definitions/ingest-metrics-task-definition.json.tftpl", {
    project_name   = var.project_name
    account_id     = var.account_id
    region         = var.region
    app_port       = var.app_port
    fargate_cpu    = var.launch_type.cpu
    fargate_memory = var.launch_type.memory
    aws_region     = var.region
  })
}
