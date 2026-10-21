terraform {
  required_version = ">= 1.6"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 4.6"
    }
  }
}

provider "docker" {
  host = "npipe:////./pipe/dockerDesktopLinuxEngine"
}

variable "image_id" {
  type        = string
  description = "Local image ID from docker image inspect task-management-api:local --format '{{.Id}}'."
}

resource "docker_volume" "tasks" {
  name = "task-project-terraform-data"
}

resource "docker_container" "api" {
  name  = "task-project-terraform-api"
  image = var.image_id
  ports {
    internal = 8080
    external = 8083
    ip       = "127.0.0.1"
  }
  volumes {
    volume_name    = docker_volume.tasks.name
    container_path = "/data"
  }
}

output "api_url" {
  value = "http://localhost:8083"
}
