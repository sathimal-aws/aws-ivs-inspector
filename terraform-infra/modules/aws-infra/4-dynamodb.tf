resource "aws_dynamodb_table" "tables_with_range" {
  for_each     = { for table in var.dynamodb_tables_with_range : table.name => table }
  name         = "${var.project_name}-${each.value.name}"
  billing_mode = each.value.billing_mode
  hash_key     = each.value.hash_key
  range_key    = each.value.range_key
  attribute {
    name = each.value.hash_key
    type = "S"
  }
  attribute {
    name = each.value.range_key
    type = "S"
  }
  tags = {
    environment = "ivs"
  }
}

resource "aws_dynamodb_table" "tables" {
  for_each     = { for table in var.dynamodb_tables : table.name => table }
  name         = "${var.project_name}-${each.value.name}"
  billing_mode = each.value.billing_mode
  hash_key     = each.value.hash_key
  attribute {
    name = each.value.hash_key
    type = "S"
  }
  tags = {
    environment = "ivs"
  }
}
