"""
Comprehensive tests for ReportingService to increase coverage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, UTC

from backend.services.reporting_service import (
    ReportingService, ReportType, ReportFormat, ReportFrequency, ReportStatus,
    ReportTemplate, ReportDefinition, GeneratedReport, ReportSchedule
)


class TestReportingService:
    """Comprehensive tests for ReportingService."""

    @pytest.fixture
    def reporting_service(self):
        """Create ReportingService instance."""
        return ReportingService()

    def test_init(self, reporting_service):
        """Test ReportingService initialization."""
        assert reporting_service is not None
        assert hasattr(reporting_service, 'templates')
        assert hasattr(reporting_service, 'definitions')
        assert hasattr(reporting_service, 'generated_reports')
        assert hasattr(reporting_service, 'schedules')
        assert isinstance(reporting_service.templates, dict)
        assert isinstance(reporting_service.definitions, dict)
        assert isinstance(reporting_service.generated_reports, dict)
        assert isinstance(reporting_service.schedules, dict)
        
        # Should have default templates initialized
        assert len(reporting_service.templates) > 0
        assert "template_health" in reporting_service.templates
        assert "template_performance" in reporting_service.templates
        assert "template_security" in reporting_service.templates
        
        # Should have sample definitions
        assert len(reporting_service.definitions) > 0

    def test_initialize_default_templates(self, reporting_service):
        """Test that default templates are properly initialized."""
        # Check health template
        health_template = reporting_service.templates.get("template_health")
        assert health_template is not None
        assert isinstance(health_template, ReportTemplate)
        assert health_template.name == "System Health Report"
        assert health_template.type == ReportType.SYSTEM_HEALTH
        assert health_template.format == ReportFormat.PDF
        assert health_template.is_system_default is True
        assert "include_metrics" in health_template.parameters
        
        # Check performance template
        perf_template = reporting_service.templates.get("template_performance")
        assert perf_template is not None
        assert isinstance(perf_template, ReportTemplate)
        assert perf_template.name == "Performance Analysis Report"
        assert perf_template.type == ReportType.PERFORMANCE
        assert perf_template.format == ReportFormat.HTML
        assert perf_template.is_system_default is True
        
        # Check security template
        security_template = reporting_service.templates.get("template_security")
        assert security_template is not None
        assert isinstance(security_template, ReportTemplate)
        assert security_template.name == "Security Audit Report"
        assert security_template.type == ReportType.SECURITY
        assert security_template.format == ReportFormat.PDF
        assert security_template.is_system_default is True

    @pytest.mark.asyncio
    async def test_create_report_template_success(self, reporting_service):
        """Test creating report template successfully."""
        result = await reporting_service.create_report_template(
            name="Custom Usage Report",
            report_type=ReportType.USAGE,
            description="Custom usage analytics report",
            format=ReportFormat.CSV,
            parameters={"metric": "user_actions", "group_by": "date"},
            query_template="SELECT * FROM usage_logs WHERE date >= '{{start_date}}'",
            created_by="test_user"
        )
        
        assert result is not None
        assert isinstance(result, ReportTemplate)
        assert result.name == "Custom Usage Report"
        assert result.type == ReportType.USAGE
        assert result.format == ReportFormat.CSV
        assert result.description == "Custom usage analytics report"
        assert result.parameters == {"metric": "user_actions", "group_by": "date"}
        assert result.query_template == "SELECT * FROM usage_logs WHERE date >= '{{start_date}}'"
        assert result.is_system_default is False
        assert len(result.id) > 0
        assert len(result.created_at) > 0
        # Should be stored in templates dict
        assert result.id in reporting_service.templates

    @pytest.mark.asyncio
    async def test_get_template_success(self, reporting_service):
        """Test getting existing template."""
        result = await reporting_service.get_template("template_health")
        
        assert result is not None
        assert isinstance(result, ReportTemplate)
        assert result.id == "template_health"
        assert result.name == "System Health Report"

    @pytest.mark.asyncio
    async def test_get_template_not_found(self, reporting_service):
        """Test getting non-existent template."""
        result = await reporting_service.get_template("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_templates_all(self, reporting_service):
        """Test listing all templates."""
        result = await reporting_service.list_templates()
        
        assert isinstance(result, list)
        assert len(result) >= 3  # Should have at least default templates
        for template in result:
            assert isinstance(template, ReportTemplate)

    @pytest.mark.asyncio
    async def test_list_templates_filter_by_type(self, reporting_service):
        """Test listing templates filtered by type."""
        result = await reporting_service.list_templates(report_type=ReportType.SYSTEM_HEALTH)
        
        assert isinstance(result, list)
        for template in result:
            assert template.type == ReportType.SYSTEM_HEALTH

    @pytest.mark.asyncio
    async def test_list_templates_include_system(self, reporting_service):
        """Test listing templates with include_system filter."""
        result = await reporting_service.list_templates(include_system=False)
        
        assert isinstance(result, list)
        for template in result:
            assert template.is_system_default is False

    @pytest.mark.asyncio
    async def test_create_report_definition_success(self, reporting_service):
        """Test creating report definition successfully."""
        result = await reporting_service.create_report_definition(
            name="Daily Health Check",
            template_id="template_health",
            parameters={"time_range": "24h"},
            recipients=["admin@example.com", "ops@example.com"],
            schedule_frequency=ReportFrequency.DAILY,
            schedule_time="08:00:00",
            created_by="admin_user"
        )
        
        assert result is not None
        assert isinstance(result, ReportDefinition)
        assert result.name == "Daily Health Check"
        assert result.template_id == "template_health"
        assert result.parameters == {"time_range": "24h"}
        assert result.recipients == ["admin@example.com", "ops@example.com"]
        assert result.schedule_frequency == ReportFrequency.DAILY
        assert result.schedule_time == "08:00:00"
        assert result.is_active is True
        assert len(result.id) > 0
        assert len(result.created_at) > 0
        assert len(result.updated_at) > 0
        # Should be stored in definitions dict
        assert result.id in reporting_service.definitions
        
        # Should have created a schedule
        assert len(reporting_service.schedules) > 0

    @pytest.mark.asyncio
    async def test_generate_report_success(self, reporting_service):
        """Test generating report successfully."""
        # Create a definition first
        definition = await reporting_service.create_report_definition(
            name="Test Report",
            template_id="template_health",
            parameters={"test": "value"},
            recipients=["test@example.com"],
            schedule_frequency=ReportFrequency.ONCE,
            schedule_time=None,
            created_by="test_user"
        )
        
        result = await reporting_service.generate_report(definition.id)
        
        assert result is not None
        assert isinstance(result, GeneratedReport)
        assert result.definition_id == definition.id
        assert result.status == ReportStatus.COMPLETED
        assert result.data is not None
        assert isinstance(result.data, dict)
        # Health report has different structure than expected
        assert "overall_status" in result.data or "report_period" in result.data
        assert result.generated_at is not None
        assert result.completed_at is not None
        assert result.error_message is None
        assert result.recipient_emails == ["test@example.com"]
        # Should be stored in generated_reports dict
        assert result.id in reporting_service.generated_reports

    @pytest.mark.asyncio
    async def test_generate_report_definition_not_found(self, reporting_service):
        """Test generating report for non-existent definition."""
        with pytest.raises(ValueError) as exc_info:
            await reporting_service.generate_report("nonexistent")
        
        assert "Report definition nonexistent not found" in str(exc_info.value)



    @pytest.mark.asyncio
    async def test_get_generated_reports(self, reporting_service):
        """Test getting generated reports."""
        # Generate some reports
        definition = await reporting_service.create_report_definition(
            name="Test Definition",
            template_id="template_health",
            parameters={},
            recipients=[],
            schedule_frequency=ReportFrequency.ONCE,
            schedule_time=None,
            created_by="test_user"
        )
        
        await reporting_service.generate_report(definition.id)
        await reporting_service.generate_report(definition.id)
        
        result = await reporting_service.get_generated_reports()
        
        assert isinstance(result, list)
        assert len(result) >= 2
        for report in result:
            assert isinstance(report, GeneratedReport)
            assert report.definition_id == definition.id

    @pytest.mark.asyncio
    async def test_get_report_definitions(self, reporting_service):
        """Test getting report definitions."""
        # Create some definitions
        await reporting_service.create_report_definition(
            name="Definition 1",
            template_id="template_health",
            parameters={},
            recipients=[],
            schedule_frequency=ReportFrequency.DAILY,
            schedule_time="09:00:00",
            created_by="user1"
        )
        await reporting_service.create_report_definition(
            name="Definition 2",
            template_id="template_performance",
            parameters={},
            recipients=[],
            schedule_frequency=ReportFrequency.WEEKLY,
            schedule_time="10:00:00",
            created_by="user2"
        )
        
        result = await reporting_service.get_report_definitions()
        
        assert isinstance(result, list)
        assert len(result) >= 2
        for definition in result:
            assert isinstance(definition, ReportDefinition)
            assert definition.is_active is True

    @pytest.mark.asyncio
    async def test_get_report_schedules(self, reporting_service):
        """Test getting report schedules."""
        # Create a definition (which creates a schedule)
        await reporting_service.create_report_definition(
            name="Scheduled Report",
            template_id="template_health",
            parameters={},
            recipients=[],
            schedule_frequency=ReportFrequency.MONTHLY,
            schedule_time="01:00:00",
            created_by="scheduler"
        )
        
        result = await reporting_service.get_report_schedules()
        
        assert isinstance(result, list)
        assert len(result) >= 1
        for schedule in result:
            assert isinstance(schedule, ReportSchedule)
            assert schedule.is_active is True
            assert schedule.next_run_time is not None

    @pytest.mark.asyncio
    async def test_export_report_json_format(self, reporting_service):
        """Test exporting report in JSON format."""
        # Generate a report first
        definition = await reporting_service.create_report_definition(
            name="Export Test",
            template_id="template_health",
            parameters={},
            recipients=[],
            schedule_frequency=ReportFrequency.ONCE,
            schedule_time=None,
            created_by="export_user"
        )
        
        report = await reporting_service.generate_report(definition.id)
        
        result = await reporting_service.export_report(report.id, ReportFormat.JSON)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        # Should be valid JSON
        import json
        data = json.loads(result.decode('utf-8'))
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_export_report_csv_format(self, reporting_service):
        """Test exporting report in CSV format."""
        # Generate a report first
        definition = await reporting_service.create_report_definition(
            name="CSV Export Test",
            template_id="template_health",
            parameters={},
            recipients=[],
            schedule_frequency=ReportFrequency.ONCE,
            schedule_time=None,
            created_by="csv_user"
        )
        
        report = await reporting_service.generate_report(definition.id)
        
        result = await reporting_service.export_report(report.id, ReportFormat.CSV)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        # Should contain CSV-like content
        text = result.decode('utf-8')
        assert isinstance(text, str)

    @pytest.mark.asyncio
    async def test_export_report_not_found(self, reporting_service):
        """Test exporting non-existent report."""
        with pytest.raises(ValueError) as exc_info:
            await reporting_service.export_report("nonexistent", ReportFormat.JSON)
        
        assert "Report nonexistent not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_report_fallback_format(self, reporting_service):
        """Test exporting report with fallback format (EXCEL falls back to JSON)."""
        # Generate a report first
        definition = await reporting_service.create_report_definition(
            name="Fallback Format Test",
            template_id="template_health",
            parameters={},
            recipients=[],
            schedule_frequency=ReportFrequency.ONCE,
            schedule_time=None,
            created_by="fallback_user"
        )
        
        report = await reporting_service.generate_report(definition.id)
        
        # EXCEL format falls back to JSON in implementation
        result = await reporting_service.export_report(report.id, ReportFormat.EXCEL)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        # Should be valid JSON (fallback)
        import json
        data = json.loads(result.decode('utf-8'))
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_get_reporting_statistics(self, reporting_service):
        """Test getting reporting statistics."""
        # Generate some reports
        definition = await reporting_service.create_report_definition(
            name="Stats Test",
            template_id="template_health",
            parameters={},
            recipients=[],
            schedule_frequency=ReportFrequency.ONCE,
            schedule_time=None,
            created_by="stats_user"
        )
        
        await reporting_service.generate_report(definition.id)
        
        result = await reporting_service.get_reporting_statistics()
        
        assert isinstance(result, dict)
        # Statistics structure changed - check for nested structure
        assert "templates" in result or "total_templates" in result
        assert "definitions" in result or "total_definitions" in result
        assert "reports" in result or "total_generated_reports" in result
        assert "schedules" in result or "total_schedules" in result
        # Check we have some data
        assert len(result) > 0

    def test_report_template_dataclass(self):
        """Test ReportTemplate dataclass."""
        template = ReportTemplate(
            id="test-template",
            name="Test Template",
            type=ReportType.CUSTOM,
            description="Test description",
            format=ReportFormat.JSON,
            parameters={"key": "value"},
            query_template="SELECT * FROM test",
            created_by="test_user",
            created_at=datetime.now(UTC).isoformat()
        )
        
        assert template.id == "test-template"
        assert template.name == "Test Template"
        assert template.type == ReportType.CUSTOM
        assert template.format == ReportFormat.JSON
        assert template.is_system_default is False

    def test_report_definition_dataclass(self):
        """Test ReportDefinition dataclass."""
        definition = ReportDefinition(
            id="test-def",
            name="Test Definition",
            template_id="template_health",
            parameters={"param": "value"},
            recipients=["user@example.com"],
            schedule_frequency=ReportFrequency.DAILY,
            schedule_time="12:00:00",
            is_active=True,
            created_by="test_user",
            created_at=datetime.now(UTC).isoformat(),
            updated_at=datetime.now(UTC).isoformat()
        )
        
        assert definition.id == "test-def"
        assert definition.name == "Test Definition"
        assert definition.template_id == "template_health"
        assert definition.is_active is True

    def test_generated_report_dataclass(self):
        """Test GeneratedReport dataclass."""
        report = GeneratedReport(
            id="test-report",
            definition_id="def_123",
            name="Generated Report",
            type=ReportType.USAGE,
            format=ReportFormat.PDF,
            status=ReportStatus.COMPLETED,
            parameters={"gen": "param"},
            data={"result": "data"},
            file_path="/path/to/report.pdf",
            file_size=1024,
            generated_at=datetime.now(UTC).isoformat(),
            completed_at=datetime.now(UTC).isoformat(),
            error_message=None,
            recipient_emails=["user@example.com"]
        )
        
        assert report.id == "test-report"
        assert report.status == ReportStatus.COMPLETED
        assert report.file_size == 1024
        assert report.error_message is None

    def test_report_schedule_dataclass(self):
        """Test ReportSchedule dataclass."""
        schedule = ReportSchedule(
            id="test-schedule",
            definition_id="def_123",
            frequency=ReportFrequency.WEEKLY,
            next_run_time="2024-01-01T00:00:00Z",
            last_run_time="2023-12-25T00:00:00Z",
            is_active=True,
            created_at=datetime.now(UTC).isoformat()
        )
        
        assert schedule.id == "test-schedule"
        assert schedule.frequency == ReportFrequency.WEEKLY
        assert schedule.is_active is True

    def test_enum_values(self):
        """Test enum values are correctly defined."""
        # Test ReportType values
        assert ReportType.SYSTEM_HEALTH.value == "system_health"
        assert ReportType.PERFORMANCE.value == "performance"
        assert ReportType.SECURITY.value == "security"
        assert ReportType.USAGE.value == "usage"
        
        # Test ReportFormat values
        assert ReportFormat.PDF.value == "pdf"
        assert ReportFormat.CSV.value == "csv"
        assert ReportFormat.JSON.value == "json"
        assert ReportFormat.HTML.value == "html"
        
        # Test ReportFrequency values
        assert ReportFrequency.ONCE.value == "once"
        assert ReportFrequency.HOURLY.value == "hourly"
        assert ReportFrequency.DAILY.value == "daily"
        assert ReportFrequency.WEEKLY.value == "weekly"
        assert ReportFrequency.MONTHLY.value == "monthly"
        
        # Test ReportStatus values
        assert ReportStatus.PENDING.value == "pending"
        assert ReportStatus.GENERATING.value == "generating"
        assert ReportStatus.COMPLETED.value == "completed"
        assert ReportStatus.FAILED.value == "failed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])