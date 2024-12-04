variable "account_id" {
  type = string
}

variable "region" {
  type = string
}

variable "project_name" {
  type = string
}

variable "cognito_user_pool_id" {
  type = string
}

variable "cognito_identity_pool_id" {
  type = string
}

variable "cognito_region" {
  type = string
}

variable "environment" {
  type    = string
  default = "ivs"
}

variable "task_family" {
  type        = string
  description = "ECS task family"
  default     = "ingest-metrics-task-definition"
}

variable "vpc_id" {
  type        = string
  description = "VPC id for ECS"
  default     = null
}

variable "network_mode" {
  type        = string
  description = "ECS network mode"
  default     = "awsvpc"
}

variable "launch_type" {
  type = object({
    type   = string
    cpu    = number
    memory = number
  })
  default = {
    type   = "FARGATE"
    cpu    = 1024
    memory = 2048
  }
}

variable "cidr_block" {
  type        = string
  description = "Range of IP address with the VPC"
  default     = "172.17.0.0/16"
}

variable "ecs_auto_scale_role_name" {
  description = "ECS auto scale role name"
  default     = "myEcsAutoScaleRole"
}

variable "az_count" {
  description = "Number of AZs to cover in a given region"
  default     = "2"
}

variable "app_port" {
  description = "Port exposed by the docker image to redirect traffic to"
  default     = 3000
}

variable "health_check_path" {
  default = "/"
}

variable "rest_apis" {
  description = "list of api to create"
  type = list(object({
    name        = string
    http_method = string
  }))

  default = [
    {
      name        = "get-metrics"
      http_method = "GET"
    },
    {
      name        = "list-channels"
      http_method = "GET"
    },
    {
      name        = "list-streams"
      http_method = "GET"
    },
    {
      name        = "list-stream-sessions"
      http_method = "GET"
    },
    {
      name        = "get-quotas"
      http_method = "GET"
    },
    {
      name        = "get-channel"
      http_method = "GET"
    },
    {
      name        = "get-stream"
      http_method = "GET"
    },
    {
      name        = "get-session"
      http_method = "GET"
    },
    {
      name        = "get-ingest-metrics"
      http_method = "GET"
    },
  ]
}

variable "wss_apis" {
  description = "list of websocket api to create"
  type        = set(string)
  default     = ["get-session-events", "get-live-streams"]
}

variable "wss_api_routes" {
  description = "list of websocket api route to create"
  type = list(object({
    name      = string
    route_key = string
    parent_id = string
  }))

  default = [
    {
      name      = "get-session-events-connect"
      route_key = "$connect"
      parent_id = "get-session-events"
    },
    {
      name      = "get-session-events-disconnect"
      route_key = "$disconnect"
      parent_id = "get-session-events"
    },
    {
      name      = "get-session-events"
      route_key = "get-session-events"
      parent_id = "get-session-events"
    },
    {
      name      = "get-live-streams-connect"
      route_key = "$connect"
      parent_id = "get-live-streams"
    },
    {
      name      = "get-live-streams-disconnect"
      route_key = "$disconnect"
      parent_id = "get-live-streams"
    },
  ]
}

variable "lambdas" {
  description = "list of lambda to create"
  type = list(object({
    name    = string
    timeout = number
  }))

  default = [
    {
      name    = "get-metrics"
      timeout = 120
    },
    {
      name    = "list-channels"
      timeout = 120
    },
    {
      name    = "list-streams"
      timeout = 120
    },
    {
      name    = "list-stream-sessions"
      timeout = 120
    },
    {
      name    = "get-quotas"
      timeout = 120
    },
    {
      name    = "get-channel"
      timeout = 120
    },
    {
      name    = "get-stream"
      timeout = 120
    },
    {
      name    = "get-session"
      timeout = 120
    },
    {
      name    = "get-ingest-metrics"
      timeout = 120
    },
    {
      name    = "eventbridge-triggers"
      timeout = 300
    },
    {
      name    = "get-session-events-connect"
      timeout = 120
    },
    {
      name    = "get-session-events-disconnect"
      timeout = 120
    },
    {
      name    = "get-session-events"
      timeout = 120
    },
    {
      name    = "get-live-streams-connect"
      timeout = 120
    },
    {
      name    = "get-live-streams-disconnect"
      timeout = 120
    }
  ]
}

variable "assume_roles" {
  description = "list of roles to create"
  type = list(object({
    name        = string
    assume_role = list(string)
  }))

  default = [
    {
      name        = "get-metrics"
      assume_role = ["lambda.amazonaws.com"]
    },
    {
      name        = "list-channels"
      assume_role = ["lambda.amazonaws.com"]
    },
    {
      name        = "list-streams"
      assume_role = ["lambda.amazonaws.com"]
    },
    {
      name        = "list-stream-sessions"
      assume_role = ["lambda.amazonaws.com"]
    },
    {
      name        = "get-quotas"
      assume_role = ["lambda.amazonaws.com"]
    },
    {
      name        = "get-channel"
      assume_role = ["lambda.amazonaws.com"]
    },
    {
      name        = "get-stream"
      assume_role = ["lambda.amazonaws.com"]
    },
    {
      name        = "get-session"
      assume_role = ["lambda.amazonaws.com"]
    },
    {
      name        = "get-ingest-metrics"
      assume_role = ["lambda.amazonaws.com"]
    },
    {
      name        = "eventbridge-triggers"
      assume_role = ["lambda.amazonaws.com", "ecs.amazonaws.com", "ecs-tasks.amazonaws.com"]
    },
    {
      name        = "ingest-metrics-ecs-task"
      assume_role = ["lambda.amazonaws.com", "ecs.amazonaws.com", "ecs-tasks.amazonaws.com"]
    },
    {
      name        = "get-session-events-connect"
      assume_role = ["lambda.amazonaws.com", "apigateway.amazonaws.com"]
    },
    {
      name        = "get-session-events-disconnect"
      assume_role = ["lambda.amazonaws.com", "apigateway.amazonaws.com"]
    },
    {
      name        = "get-session-events"
      assume_role = ["lambda.amazonaws.com", "apigateway.amazonaws.com"]
    },
    {
      name        = "get-live-streams-connect"
      assume_role = ["lambda.amazonaws.com", "apigateway.amazonaws.com"]
    },
    {
      name        = "get-live-streams-disconnect"
      assume_role = ["lambda.amazonaws.com", "apigateway.amazonaws.com"]
    },
  ]
}

variable "rules" {
  description = "IVS EventBridge Rules"
  type = list(object({
    name        = string
    description = string
    source      = string
    detail-type = string
  }))

  default = [
    {
      name        = "limit-breach"
      description = "receive alert when ingest metrics limit breaches"
      source      = "aws.ivs"
      detail-type = "IVS Limit Breach"
    },
    {
      name        = "health-state-change"
      description = "receive alert when ingest health state changes"
      source      = "aws.ivs"
      detail-type = "IVS Stream Health Change"
    },
    {
      name        = "stream-state-change"
      description = "receive alert when stream state changes"
      source      = "aws.ivs"
      detail-type = "IVS Stream State Change"
    },
    {
      name        = "recording-state-change"
      description = "receive alert when recording state changes"
      source      = "aws.ivs"
      detail-type = "IVS Recording State Change"
    },
  ]
}

variable "dynamodb_tables_with_range" {
  description = "Tables with range"
  type = list(object({
    name         = string
    billing_mode = string
    hash_key     = string
    range_key    = string
  }))

  default = [
    {
      name         = "state-events"
      billing_mode = "PAY_PER_REQUEST"
      hash_key     = "streamId"
      range_key    = "channelArn"
    },
    {
      name         = "ingest-metrics"
      billing_mode = "PAY_PER_REQUEST"
      hash_key     = "streamId"
      range_key    = "channelId"
    },
    {
      name         = "stream-sessions"
      billing_mode = "PAY_PER_REQUEST"
      hash_key     = "streamId"
      range_key    = "channelArn"
    }
  ]
}

variable "dynamodb_tables" {
  description = "Tables without range"
  type = list(object({
    name         = string
    billing_mode = string
    hash_key     = string
  }))

  default = [
    {
      name         = "live-stream-session-connection-ids"
      billing_mode = "PAY_PER_REQUEST"
      hash_key     = "connectionId"
    },
  ]
}

