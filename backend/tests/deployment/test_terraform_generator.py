"""
Tests for Terraform Generator.
"""

from backend.deployment.terraform_generator import (
    ResourceConfig,
    TerraformGenerator,
)


class TestResourceConfig:
    """Test cases for ResourceConfig."""

    def test_config_creation(self):
        """Test creating resource config."""
        config = ResourceConfig(
            name="mybucket",
            resource_type="aws_s3_bucket",
            config={"bucket": "my-bucket"},
        )

        assert config.name == "mybucket"
        assert config.resource_type == "aws_s3_bucket"


class TestTerraformGenerator:
    """Test cases for TerraformGenerator."""

    def setup_method(self):
        """Create fresh generator for each test."""
        self.generator = TerraformGenerator()

    def test_generator_initialization(self):
        """Test generator initialization."""
        assert self.generator is not None

    def test_generate_aws_basic(self):
        """Test generating basic AWS config."""
        files = self.generator.generate_aws_basic(
            project_name="myproject",
            region="us-east-1",
        )

        assert "main.tf" in files
        assert 'provider "aws"' in files["main.tf"]
        assert "region" in files["main.tf"]

    def test_generate_azure_basic(self):
        """Test generating basic Azure config."""
        files = self.generator.generate_azure_basic(
            project_name="myproject",
        )

        assert "main.tf" in files
        assert 'provider "azurerm"' in files["main.tf"]

    def test_generate_gcp_basic(self):
        """Test generating basic GCP config."""
        files = self.generator.generate_gcp_basic(
            project_name="myproject",
            region="us-central1",
        )

        assert "main.tf" in files
        assert 'provider "google"' in files["main.tf"]
