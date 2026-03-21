"""
Terraform Generator for AI Software Factory.

This module provides Infrastructure as Code generation using Terraform
for AWS, Azure, and GCP.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

from backend.core.logging import get_logger

logger = get_logger(__name__)


class CloudProvider(str, Enum):
    """Supported cloud providers."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


@dataclass
class ResourceConfig:
    """
    Resource configuration.

    Attributes:
        name: Resource name
        resource_type: Terraform resource type
        config: Resource configuration dict
    """
    name: str
    resource_type: str
    config: Dict[str, Any] = field(default_factory=dict)


class TerraformGenerator:
    """
    Terraform configuration generator.

    This class provides:
    - AWS infrastructure generation
    - Azure infrastructure generation
    - GCP infrastructure generation
    - Modular resource management

    Example:
        >>> generator = TerraformGenerator()
        >>> config = generator.generate_aws_basic(
        ...     project_name="myproject",
        ...     region="us-east-1"
        ... )
    """

    def __init__(self):
        """Initialize the Terraform generator."""
        self._logger = get_logger(__name__)

    def generate_aws_basic(
        self,
        project_name: str,
        region: str = "us-east-1",
        enable_ecs: bool = True,
        enable_rds: bool = True,
    ) -> Dict[str, str]:
        """
        Generate basic AWS Terraform configuration.

        Args:
            project_name: Project name
            region: AWS region
            enable_ecs: Whether to include ECS
            enable_rds: Whether to include RDS

        Returns:
            Dictionary mapping filenames to content
        """
        files = {}

        # Main configuration
        files["main.tf"] = f'''terraform {{
  required_version = ">= 1.0"

  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}

  backend "s3" {{
    bucket = "{project_name}-terraform-state"
    key    = "terraform.tfstate"
    region = "{region}"
  }}
}}

provider "aws" {{
  region = var.aws_region

  default_tags {{
    tags = {{
      Project     = "{project_name}"
      Environment = var.environment
      ManagedBy   = "terraform"
    }}
  }}
}}

# VPC and Networking
module "vpc" {{
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${{var.project_name}}-${{var.environment}}"
  cidr = "10.0.0.0/16"

  azs             = ["{region}a", "{region}b", "{region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false

  tags = {{
    Terraform = "true"
  }}
}}
'''

        # Variables
        files["variables.tf"] = f'''variable "project_name" {{
  description = "Project name"
  type        = string
  default     = "{project_name}"
}}

variable "environment" {{
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}}

variable "aws_region" {{
  description = "AWS region"
  type        = string
  default     = "{region}"
}}

variable "app_port" {{
  description = "Application port"
  type        = number
  default     = 8000
}}
'''

        # Outputs
        files["outputs.tf"] = '''output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "private_subnets" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnets
}
'''

        if enable_ecs:
            files["ecs.tf"] = '''# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 1
    capacity_provider = "FARGATE"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "${var.project_name}-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "app"
    image = "${aws_ecr_repository.app.repository_url}:latest"
    portMappings = [{
      containerPort = var.app_port
      protocol      = "tcp"
    }]
    environment = [
      { name = "ENVIRONMENT", value = var.environment }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.app.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "ecs"
      }
    }
  }])
}

# ECR Repository
resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-${var.environment}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.project_name}-${var.environment}"
  retention_in_days = 7
}

# IAM Roles
resource "aws_iam_role" "ecs_execution" {
  name = "${var.project_name}-ecs-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name = "${var.project_name}-ecs-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}
'''

        if enable_rds:
            files["rds.tf"] = '''# RDS Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}"
  subnet_ids = module.vpc.private_subnets

  tags = {
    Name = "${var.project_name}-${var.environment}"
  }
}

# RDS Security Group
resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}"

  engine         = "postgres"
  engine_version = "15"
  instance_class = "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = replace("${var.project_name}_${var.environment}", "-", "_")
  username = "dbadmin"
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"

  skip_final_snapshot = var.environment != "prod"

  tags = {
    Name = "${var.project_name}-${var.environment}"
  }
}

# Random password for RDS
resource "random_password" "db_password" {
  length  = 16
  special = true
}
'''

        self._logger.info(
            "AWS Terraform configuration generated",
            project=project_name,
            region=region,
            ecs=enable_ecs,
            rds=enable_rds,
            files=len(files),
        )

        return files

    def generate_azure_basic(
        self,
        project_name: str,
        location: str = "eastus",
    ) -> Dict[str, str]:
        """
        Generate basic Azure Terraform configuration.

        Args:
            project_name: Project name
            location: Azure location

        Returns:
            Dictionary mapping filenames to content
        """
        files = {}

        files["main.tf"] = f'''terraform {{
  required_version = ">= 1.0"

  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }}
  }}

  backend "azurerm" {{
    resource_group_name  = "{project_name}-terraform"
    storage_account_name = "{project_name}tfstate"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }}
}}

provider "azurerm" {{
  features {{}}
}}

# Resource Group
resource "azurerm_resource_group" "main" {{
  name     = "${{var.project_name}}-${{var.environment}}"
  location = var.location

  tags = {{
    Environment = var.environment
    Project     = var.project_name
  }}
}}

# Virtual Network
resource "azurerm_virtual_network" "main" {{
  name                = "${{var.project_name}}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}}

# Subnets
resource "azurerm_subnet" "app" {{
  name                 = "app"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}}

resource "azurerm_subnet" "db" {{
  name                 = "db"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
  service_endpoints    = ["Microsoft.Sql"]
}}
'''

        files["variables.tf"] = f'''variable "project_name" {{
  description = "Project name"
  type        = string
  default     = "{project_name}"
}}

variable "environment" {{
  description = "Environment"
  type        = string
  default     = "dev"
}}

variable "location" {{
  description = "Azure location"
  type        = string
  default     = "{location}"
}}
'''

        files["outputs.tf"] = '''output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}

output "virtual_network_id" {
  description = "Virtual network ID"
  value       = azurerm_virtual_network.main.id
}
'''

        self._logger.info(
            "Azure Terraform configuration generated",
            project=project_name,
            location=location,
        )

        return files

    def generate_gcp_basic(
        self,
        project_name: str,
        region: str = "us-central1",
    ) -> Dict[str, str]:
        """
        Generate basic GCP Terraform configuration.

        Args:
            project_name: Project name
            region: GCP region

        Returns:
            Dictionary mapping filenames to content
        """
        files = {}

        files["main.tf"] = f'''terraform {{
  required_version = ">= 1.0"

  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "~> 5.0"
    }}
  }}

  backend "gcs" {{
    bucket = "{project_name}-terraform-state"
    prefix = "terraform/state"
  }}
}}

provider "google" {{
  project = var.gcp_project_id
  region  = var.region
}}

# VPC Network
resource "google_compute_network" "main" {{
  name                    = "${{var.project_name}}-${{var.environment}}"
  auto_create_subnetworks = false
}}

# Subnet
resource "google_compute_subnetwork" "main" {{
  name          = "${{var.project_name}}-${{var.environment}}"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.main.id
}}

# Cloud Run Service
resource "google_cloud_run_service" "app" {{
  name     = "${{var.project_name}}-${{var.environment}}"
  location = var.region

  template {{
    spec {{
      containers {{
        image = "gcr.io/${{var.gcp_project_id}}/${{var.project_name}}:latest"

        ports {{
          container_port = 8000
        }}

        resources {{
          limits = {{
            cpu    = "1"
            memory = "512Mi"
          }}
        }}
      }}
    }}
  }}

  traffic {{
    percent         = 100
    latest_revision = true
  }}
}}

# Allow unauthenticated access
resource "google_cloud_run_service_iam_member" "public" {{
  service  = google_cloud_run_service.app.name
  location = google_cloud_run_service.app.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}}
'''

        files["variables.tf"] = f'''variable "project_name" {{
  description = "Project name"
  type        = string
  default     = "{project_name}"
}}

variable "environment" {{
  description = "Environment"
  type        = string
  default     = "dev"
}}

variable "gcp_project_id" {{
  description = "GCP Project ID"
  type        = string
}}

variable "region" {{
  description = "GCP Region"
  type        = string
  default     = "{region}"
}}
'''

        files["outputs.tf"] = '''output "cloud_run_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_service.app.status[0].url
}

output "network_id" {
  description = "VPC Network ID"
  value       = google_compute_network.main.id
}
'''

        self._logger.info(
            "GCP Terraform configuration generated",
            project=project_name,
            region=region,
        )

        return files
