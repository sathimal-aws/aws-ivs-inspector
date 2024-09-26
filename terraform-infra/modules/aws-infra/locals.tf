locals {
  tags = {
    created_by = "aws_ivs"
  }
  aws_ecr_url = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com"

  azs_names = data.aws_availability_zones.available.names

  cluster_name    = "${var.project_name}-ingest-metrics-cluster"
  service_name    = "${var.project_name}-ingest-metrics-service"
  task_definition = "${var.project_name}-ingest-metrics-task-definition"

  policies = [
    {
      name = "get-metrics"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "cloudwatch:GetMetricStatistics",
          ],

          resources = ["*"]
        }
      ]
    },
    {
      name = "list-channels"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "ivs:ListChannels"
          ]
          resources = ["arn:aws:ivs:${var.region}:${var.account_id}:channel/*"]
        }
      ]
    },
    {
      name = "list-streams"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "ivs:ListStreams"
          ]
          resources = ["arn:aws:ivs:${var.region}:${var.account_id}:channel/*"]
        }
      ]
    },
    {
      name = "list-stream-sessions"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "ivs:ListStreamSessions"
          ]
          resources = ["arn:aws:ivs:${var.region}:${var.account_id}:channel/*"]
        }
      ]
    },
    {
      name = "get-quotas"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "servicequotas:ListServiceQuotas"
          ]
          resources = [
            "*"
            # "arn:aws:servicequotas:${var.region}:${var.account_id}:ivs/*",
          ]
        }
      ]
    },
    {
      name = "get-channel"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "ivs:GetChannel"
          ]
          resources = ["arn:aws:ivs:${var.region}:${var.account_id}:channel/*"]
        }
      ]
    },
    {
      name = "get-stream"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "ivs:GetStream"
          ]
          resources = ["arn:aws:ivs:${var.region}:${var.account_id}:channel/*"]
        }
      ]
    },
    {
      name = "get-session"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "dynamodb:GetItem",
          ]
          resources = [
            "arn:aws:dynamodb:${var.region}:${var.account_id}:table/${var.project_name}-stream-sessions"
          ]
        }
      ]
    },
    {
      name = "get-ingest-metrics"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "dynamodb:GetItem"
          ]
          resources = [
            "arn:aws:dynamodb:${var.region}:${var.account_id}:table/${var.project_name}-ingest-metrics"
          ]
        },
        {
          effect = "Allow"
          actions = [
            "dynamodb:Scan",
            "dynamodb:UpdateItem",
          ],
          resources = [
            "arn:aws:dynamodb:${var.region}:${var.account_id}:table/${var.project_name}-state-events"
          ]
        }
      ]
    },
    {
      name = "eventbridge-triggers"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "ivs:GetStreamSession",
          ]
          resources = ["arn:aws:ivs:${var.region}:${var.account_id}:channel/*"]

        },
        # TODO: this statement needs granular permission
        {
          effect = "Allow"
          actions = [
            "ecs:RunTask",
            "ecs:StopTask",
          ]
          resources = [
            "*"
          ]
        },
        {
          effect = "Allow"
          actions = [
            "execute-api:Invoke",
            "execute-api:ManageConnections",
          ]
          resources = [
            "arn:aws:execute-api:${var.region}:${var.account_id}:${aws_apigatewayv2_stage.stage["get-live-streams"].api_id}/${var.environment}/*/*",
            "arn:aws:execute-api:${var.region}:${var.account_id}:${aws_apigatewayv2_stage.stage["get-session-events"].api_id}/${var.environment}/*/*"
          ]
        },
        # TODO: this statement needs granular permission
        {
          effect = "Allow"
          actions = [
            "iam:PassRole",
          ]
          resources = [
            "arn:aws:iam::${var.account_id}:role/*"
          ]
        },
        {
          effect = "Allow"
          actions = [
            "dynamodb:PutItem",
            "dynamodb:GetItem",
            "dynamodb:UpdateItem"
          ]
          resources = [
            "arn:aws:dynamodb:${var.region}:${var.account_id}:table/${var.project_name}-state-events"
          ]
        },
        {
          effect = "Allow"
          actions = [
            "dynamodb:PutItem",
            "dynamodb:GetItem",
            "dynamodb:UpdateItem"
          ]
          resources = [
            "arn:aws:dynamodb:${var.region}:${var.account_id}:table/${var.project_name}-stream-sessions",
          ]
        },
        {
          effect = "Allow"
          actions = [
            "dynamodb:Scan"
          ]
          resources = [
            "arn:aws:dynamodb:${var.region}:${var.account_id}:table/${var.project_name}-live-stream-session-connection-ids",
          ]
        }
      ]
    },
    {
      name = "ingest-metrics-ecs-task"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "ecr:GetAuthorizationToken",
            "ecr:BatchCheckLayerAvailability",
            "ecr:GetDownloadUrlForLayer",
            "ecr:BatchGetImage",

            "cloudwatch:GetMetricData",
            "cloudwatch:GetMetricStatistics",
            "cloudwatch:ListMetrics",

            "dynamodb:PutItem",
            "dynamodb:DeleteItem",
            "dynamodb:GetItem",
            "dynamodb:Scan",
            "dynamodb:Query",
            "dynamodb:UpdateItem",
            "dynamodb:DescribeStream",
            "dynamodb:BatchWriteItem",

            "dynamodb:ListStreams",
          ],

          resources = ["*"]
        }
      ]
    },
    {
      name = "get-live-streams-connect"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "dynamodb:PutItem",
          ],
          resources = [
            "arn:aws:dynamodb:${var.region}:${var.account_id}:table/${var.project_name}-live-stream-session-connection-ids"
          ]
        },
        {
          effect = "Allow"
          actions = [
            "lambda:InvokeFunction",
          ]
          effect    = "Allow"
          resources = ["*"]
        }
      ]
    },
    {
      name = "get-live-streams-disconnect"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },

        {
          effect = "Allow"
          actions = [
            "dynamodb:DeleteItem",
          ],
          resources = [
            "arn:aws:dynamodb:${var.region}:${var.account_id}:table/${var.project_name}-live-stream-session-connection-ids"
          ]
        },
        {
          effect = "Allow"
          actions = [
            "lambda:InvokeFunction",
          ]
          effect    = "Allow"
          resources = ["*"]
        }
      ]
    },
    {
      name = "get-session-events-connect"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "lambda:InvokeFunction",
          ]
          effect    = "Allow"
          resources = ["*"]
        }
      ]
    },
    {
      name = "get-session-events-disconnect"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "dynamodb:Scan",
            "dynamodb:UpdateItem",
          ],
          resources = [
            "arn:aws:dynamodb:${var.region}:${var.account_id}:table/${var.project_name}-state-events"
          ]
        },
        {
          effect = "Allow"
          actions = [
            "lambda:InvokeFunction",
          ]
          effect    = "Allow"
          resources = ["*"]
        }
      ]
    },
    {
      name = "get-session-events"
      statements = [
        {
          effect = "Allow"
          actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:*"]
        },
        {
          effect = "Allow"
          actions = [
            "execute-api:Invoke",
            "execute-api:ManageConnections",
          ]
          resources = [
            "arn:aws:execute-api:${var.region}:${var.account_id}:${aws_apigatewayv2_stage.stage["get-live-streams"].api_id}/${var.environment}/*/*",
            "arn:aws:execute-api:${var.region}:${var.account_id}:${aws_apigatewayv2_stage.stage["get-session-events"].api_id}/${var.environment}/*/*"
          ]
        },
        {
          effect = "Allow"
          actions = [
            "dynamodb:GetItem",
            "dynamodb:UpdateItem",
          ],
          resources = [
            "arn:aws:dynamodb:${var.region}:${var.account_id}:table/${var.project_name}-state-events"
          ]
        },
        # {
        #   effect = "Allow"
        #   actions = [
        #     "dynamodb:PutItem",
        #   ],
        #   resources = [
        #     "arn:aws:dynamodb:${var.region}:${var.account_id}:table/${var.project_name}-live-stream-session-connection-ids"
        #   ]
        # },
        {
          effect = "Allow"
          actions = [
            "lambda:InvokeFunction",
          ]
          effect    = "Allow"
          resources = ["*"]
        }
      ]
    },
  ]

  ecs_task_execution_policy = [
    {
      name = "${var.project_name}-${var.region}-ecs-task-execution-policy"
      statements = [
        {
          effect = "Allow"
          actions = [
            "ecr:BatchCheckLayerAvailability",
            "ecr:GetDownloadUrlForLayer",
            "ecr:BatchGetImage"
          ]
          resources = ["arn:aws:ecr:${var.region}:${data.aws_caller_identity.current.account_id}:repository/*"]

        },

        # TODO: this statement needs granular permission
        {
          effect = "Allow"
          actions = [
            "ecr:GetAuthorizationToken",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ]
          resources = ["*"]
        },

        # TODO: this statement needs granular permission
        {
          effect = "Allow"
          actions = [
            "cloudwatch:GetMetricData",
            "cloudwatch:GetMetricStatistics",
            "cloudwatch:ListMetrics"
          ]
          resources = ["*"]
        },
        {
          effect = "Allow"
          actions = [
            "dynamodb:UpdateItem",
          ]
          resources = ["arn:aws:dynamodb:${var.region}:${var.account_id}:table/${var.project_name}-ingest-metrics"]
        }
      ]
    }
  ]
}
