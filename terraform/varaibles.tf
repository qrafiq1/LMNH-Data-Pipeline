
variable "DATABASE_USERNAME" {
    description = "The username for the database"
    type = string
    sensitive = true
}


variable "DATABASE_PASSWORD" {
    description = "The password for the database"
    type = string
    sensitive = true
}

variable "KEY_NAME" {
    description = "value"
    type = string
    sensitive = true
}