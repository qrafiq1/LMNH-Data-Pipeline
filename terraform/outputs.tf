output "rds-museum-endpoint" {
  description = "The endpoint of the RDS instance"
  value = aws_db_instance.c14-qasim-museum-db.endpoint
}

output "rds-museum-address" {
  description = "The address of the RDS instance"
  value = aws_db_instance.c14-qasim-museum-db.address
}

output "rds-db-name" {
  description = "The db name"
  value = aws_db_instance.c14-qasim-museum-db.db_name
}

output "ec2-address" {
  description = "The ec2 address"
  value = aws_instance.c14_qasim_museum_ec2.public_dns
}
