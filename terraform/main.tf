provider "aws" {
    region = "eu-west-2"
}

resource "aws_security_group" "c14-qasim-ec2-sg" {
    name = "c14-qasim-ec2-sg"
    description = "Allow SSH and PostgreSQL access"
    vpc_id = "vpc-0344763624ac09cb6"

    ingress {
        description = "SSH"
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = [ "0.0.0.0/0" ]
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = [ "0.0.0.0/0" ]
    }
}

resource "aws_security_group" "c14-qasim-museum-sg" {
    name = "c14-qasim-museum-sg"
    description = "Allow access to PostgreSQL from anywhere"
    vpc_id = "vpc-0344763624ac09cb6"

    ingress {
        description = "PostrgeSQL"
        from_port = 5432
        to_port = 5432
        protocol = "tcp"
        cidr_blocks = [ "0.0.0.0/0" ]
        security_groups = [aws_security_group.c14-qasim-ec2-sg.id]
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = [ "0.0.0.0/0" ]
    }
}

data "aws_subnet" "vpc-subnet-c14" {
    filter {
      name = "tag:Name"
      values = [ "c14-public-subnet-1" ]
    }
  
}

resource "aws_instance" "c14_qasim_museum_ec2" {
    ami           = "ami-0acc77abdfc7ed5a6" 
    instance_type = "t3.micro"
    key_name      = var.KEY_NAME
    subnet_id = data.aws_subnet.vpc-subnet-c14.id
    
    associate_public_ip_address = true

    vpc_security_group_ids = [ aws_security_group.c14-qasim-ec2-sg.id ]

    tags = {
        Name = "c14-qasim-museum-ec2"
    }
}

resource "aws_db_instance" "c14-qasim-museum-db" {
    engine = "postgres"
    engine_version = "16.2"
    instance_class = "db.t3.micro"
    allocated_storage = 20
    identifier = "c14-qasim-museum-db"
    db_name = "museum"
    username = var.DATABASE_USERNAME
    password = var.DATABASE_PASSWORD
    publicly_accessible = true
    skip_final_snapshot = true
    performance_insights_enabled = false

    db_subnet_group_name = "c14-public-subnet-group"

    vpc_security_group_ids = [ aws_security_group.c14-qasim-museum-sg.id ]

    tags = {
       Name = "c14-qasim-museum-db"
     }
}