# create cloudwatch log group for lambda
resource "aws_amplify_app" "app" {
  name         = "aws-${var.project_name}"
  repository   = var.repository
  access_token = var.token

  build_spec = var.path_to_build_spec != null ? file("${path.root}/${var.path_to_build_spec}") : file("${path.root}/../amplify.yml")

  # The default rewrites and redirects added by the Amplify Console.
  custom_rule {
    source = "/<*>"
    status = "404"
    target = "/index.html"
  }
}

resource "aws_amplify_branch" "branch" {
  app_id            = aws_amplify_app.app.id
  branch_name       = var.branch_name
  enable_auto_build = false
  framework         = "Vue"
  stage             = "PRODUCTION"
}

