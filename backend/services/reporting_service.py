"""
Comprehensive Reporting Service

Provides enterprise-grade reporting capabilities including automated report generation,
scheduled reports, custom report templates, and multi-format export options.
"""

import asyncio
import json
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


class ReportType(str, Enum):
    """Types of reports available."""
    SYSTEM_HEALTH = "system_health"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USAGE = "usage"
    FINANCIAL = "financial"
    AUDIT = "audit"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    """Supported report formats."""
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    EXCEL = "excel"


class ReportFrequency(str, Enum):
    """Report scheduling frequencies."""
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class ReportStatus(str, Enum):
    """Report generation statuses."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ReportTemplate:
    """Report template definition."""
    id: str
    name: str
    type: ReportType
    description: str
    format: ReportFormat
    parameters: dict[str, Any]
    query_template: str
    created_by: str
    created_at: str
    is_system_default: bool = False


@dataclass
class ReportDefinition:
    """Report generation definition."""
    id: str
    name: str
    template_id: str
    parameters: dict[str, Any]
    recipients: list[str]
    schedule_frequency: ReportFrequency
    schedule_time: str | None  # ISO format time for scheduled reports
    is_active: bool
    created_by: str
    created_at: str
    updated_at: str


@dataclass
class GeneratedReport:
    """Generated report instance."""
    id: str
    definition_id: str
    name: str
    type: ReportType
    format: ReportFormat
    status: ReportStatus
    parameters: dict[str, Any]
    data: dict[str, Any] | None
    file_path: str | None
    file_size: int | None
    generated_at: str
    completed_at: str | None
    error_message: str | None
    recipient_emails: list[str]


@dataclass
class ReportSchedule:
    """Report scheduling configuration."""
    id: str
    definition_id: str
    frequency: ReportFrequency
    next_run_time: str
    last_run_time: str | None
    is_active: bool
    created_at: str


class ReportingService:
    """Main service for comprehensive reporting capabilities."""

    def __init__(self):
        self.templates: dict[str, ReportTemplate] = {}
        self.definitions: dict[str, ReportDefinition] = {}
        self.generated_reports: dict[str, GeneratedReport] = {}
        self.schedules: dict[str, ReportSchedule] = {}
        self._initialize_default_templates()
        self._initialize_sample_definitions()

    def _initialize_default_templates(self):
        """Initialize with default report templates."""
        # System Health Report Template
        health_template = ReportTemplate(
            id="template_health",
            name="System Health Report",
            type=ReportType.SYSTEM_HEALTH,
            description="Comprehensive system health and status overview",
            format=ReportFormat.PDF,
            parameters={
                "include_metrics": True,
                "include_alerts": True,
                "include_services": True,
                "time_range": "24h"
            },
            query_template="""
                SELECT
                    service_name,
                    status,
                    response_time,
                    error_rate,
                    last_check
                FROM system_health
                WHERE last_check >= NOW() - INTERVAL '{{time_range}}'
                ORDER BY service_name
            """,
            created_by="system",
            created_at=datetime.now(UTC).isoformat(),
            is_system_default=True
        )

        # Performance Report Template
        perf_template = ReportTemplate(
            id="template_performance",
            name="Performance Analysis Report",
            type=ReportType.PERFORMANCE,
            description="Detailed performance metrics and trends",
            format=ReportFormat.HTML,
            parameters={
                "metrics": ["cpu_usage", "memory_usage", "response_time"],
                "aggregation": "hourly",
                "include_charts": True
            },
            query_template="""
                SELECT
                    timestamp,
                    AVG(cpu_usage) as avg_cpu,
                    AVG(memory_usage) as avg_memory,
                    AVG(response_time) as avg_response_time
                FROM performance_metrics
                WHERE timestamp >= NOW() - INTERVAL '7 days'
                GROUP BY DATE_TRUNC('{{aggregation}}', timestamp)
                ORDER BY timestamp
            """,
            created_by="system",
            created_at=datetime.now(UTC).isoformat(),
            is_system_default=True
        )

        # Security Report Template
        security_template = ReportTemplate(
            id="template_security",
            name="Security Audit Report",
            type=ReportType.SECURITY,
            description="Security vulnerabilities and compliance status",
            format=ReportFormat.PDF,
            parameters={
                "scan_types": ["vulnerability", "compliance"],
                "severity_levels": ["high", "critical"],
                "include_recommendations": True
            },
            query_template="""
                SELECT
                    scan_date,
                    vulnerability_id,
                    severity,
                    description,
                    remediation_steps
                FROM security_scans
                WHERE severity IN ('{{severity_levels}}')
                AND scan_date >= NOW() - INTERVAL '30 days'
                ORDER BY severity DESC, scan_date DESC
            """,
            created_by="system",
            created_at=datetime.now(UTC).isoformat(),
            is_system_default=True
        )

        # Usage Report Template
        usage_template = ReportTemplate(
            id="template_usage",
            name="User Usage Report",
            type=ReportType.USAGE,
            description="User activity and engagement metrics",
            format=ReportFormat.EXCEL,
            parameters={
                "metrics": ["active_users", "sessions", "feature_usage"],
                "group_by": "user_role",
                "time_range": "30d"
            },
            query_template="""
                SELECT
                    DATE_TRUNC('day', activity_date) as date,
                    user_role,
                    COUNT(DISTINCT user_id) as active_users,
                    COUNT(session_id) as sessions,
                    COUNT(feature_interactions) as feature_usage
                FROM user_activity
                WHERE activity_date >= NOW() - INTERVAL '{{time_range}}'
                GROUP BY DATE_TRUNC('day', activity_date), user_role
                ORDER BY date DESC
            """,
            created_by="system",
            created_at=datetime.now(UTC).isoformat(),
            is_system_default=True
        )

        self.templates = {
            health_template.id: health_template,
            perf_template.id: perf_template,
            security_template.id: security_template,
            usage_template.id: usage_template
        }

    def _initialize_sample_definitions(self):
        """Initialize with sample report definitions."""
        # Daily Health Report Definition
        daily_health_def = ReportDefinition(
            id="def_daily_health",
            name="Daily System Health Report",
            template_id="template_health",
            parameters={
                "include_metrics": True,
                "include_alerts": True,
                "time_range": "24h"
            },
            recipients=["admin@thetaai.com", "ops@thetaai.com"],
            schedule_frequency=ReportFrequency.DAILY,
            schedule_time="09:00:00",
            is_active=True,
            created_by="admin_1",
            created_at=datetime.now(UTC).isoformat(),
            updated_at=datetime.now(UTC).isoformat()
        )

        # Weekly Performance Report Definition
        weekly_perf_def = ReportDefinition(
            id="def_weekly_perf",
            name="Weekly Performance Analysis",
            template_id="template_performance",
            parameters={
                "metrics": ["cpu_usage", "memory_usage"],
                "aggregation": "daily",
                "include_charts": True
            },
            recipients=["admin@thetaai.com", "engineering@thetaai.com"],
            schedule_frequency=ReportFrequency.WEEKLY,
            schedule_time="10:00:00",
            is_active=True,
            created_by="admin_1",
            created_at=datetime.now(UTC).isoformat(),
            updated_at=datetime.now(UTC).isoformat()
        )

        self.definitions = {
            daily_health_def.id: daily_health_def,
            weekly_perf_def.id: weekly_perf_def
        }

    async def create_report_template(
        self,
        name: str,
        report_type: ReportType,
        description: str,
        format: ReportFormat,
        parameters: dict[str, Any],
        query_template: str,
        created_by: str
    ) -> ReportTemplate:
        """Create a new report template."""
        try:
            template_id = f"template_{uuid.uuid4().hex[:8]}"

            template = ReportTemplate(
                id=template_id,
                name=name,
                type=report_type,
                description=description,
                format=format,
                parameters=parameters,
                query_template=query_template,
                created_by=created_by,
                created_at=datetime.now(UTC).isoformat()
            )

            self.templates[template_id] = template

            logger.info(f"Created report template: {name}", template_id=template_id)
            return template

        except Exception as e:
            logger.error("Failed to create report template", error=str(e))
            raise

    async def get_template(self, template_id: str) -> ReportTemplate | None:
        """Get a specific report template."""
        return self.templates.get(template_id)

    async def list_templates(
        self,
        report_type: ReportType | None = None,
        include_system: bool = True
    ) -> list[ReportTemplate]:
        """List available report templates."""
        templates = list(self.templates.values())

        if report_type:
            templates = [t for t in templates if t.type == report_type]

        if not include_system:
            templates = [t for t in templates if not t.is_system_default]

        return templates

    async def create_report_definition(
        self,
        name: str,
        template_id: str,
        parameters: dict[str, Any],
        recipients: list[str],
        schedule_frequency: ReportFrequency,
        schedule_time: str | None,
        created_by: str
    ) -> ReportDefinition:
        """Create a new report definition."""
        try:
            # Validate template exists
            if template_id not in self.templates:
                raise ValueError(f"Template {template_id} not found")

            definition_id = f"def_{uuid.uuid4().hex[:8]}"

            definition = ReportDefinition(
                id=definition_id,
                name=name,
                template_id=template_id,
                parameters=parameters,
                recipients=recipients,
                schedule_frequency=schedule_frequency,
                schedule_time=schedule_time,
                is_active=True,
                created_by=created_by,
                created_at=datetime.now(UTC).isoformat(),
                updated_at=datetime.now(UTC).isoformat()
            )

            self.definitions[definition_id] = definition

            # Create schedule if applicable
            if schedule_frequency != ReportFrequency.ONCE and schedule_time:
                await self._create_report_schedule(definition)

            logger.info(f"Created report definition: {name}", definition_id=definition_id)
            return definition

        except Exception as e:
            logger.error("Failed to create report definition", error=str(e))
            raise

    async def _create_report_schedule(self, definition: ReportDefinition):
        """Create schedule for recurring reports."""
        try:
            schedule_id = f"schedule_{uuid.uuid4().hex[:8]}"

            # Calculate next run time
            now = datetime.now(UTC)
            if definition.schedule_frequency == ReportFrequency.DAILY:
                next_run = now.replace(hour=int(definition.schedule_time.split(':')[0]),
                                     minute=int(definition.schedule_time.split(':')[1]),
                                     second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
            elif definition.schedule_frequency == ReportFrequency.WEEKLY:
                next_run = now.replace(hour=int(definition.schedule_time.split(':')[0]),
                                     minute=int(definition.schedule_time.split(':')[1]),
                                     second=0, microsecond=0)
                # Add days to reach next occurrence
                days_ahead = 7 - now.weekday()  # Next Monday
                if days_ahead <= 0:
                    days_ahead += 7
                next_run += timedelta(days=days_ahead)
            else:
                next_run = now + timedelta(hours=1)  # Default fallback

            schedule = ReportSchedule(
                id=schedule_id,
                definition_id=definition.id,
                frequency=definition.schedule_frequency,
                next_run_time=next_run.isoformat(),
                last_run_time=None,
                is_active=definition.is_active,
                created_at=datetime.now(UTC).isoformat()
            )

            self.schedules[schedule_id] = schedule

            logger.info(f"Created report schedule for definition {definition.id}")

        except Exception as e:
            logger.error("Failed to create report schedule", error=str(e))

    async def generate_report(
        self,
        definition_id: str,
        override_parameters: dict[str, Any] | None = None
    ) -> GeneratedReport:
        """Generate a report based on definition."""
        try:
            definition = self.definitions.get(definition_id)
            if not definition:
                raise ValueError(f"Report definition {definition_id} not found")

            template = self.templates.get(definition.template_id)
            if not template:
                raise ValueError(f"Template {definition.template_id} not found")

            # Merge parameters
            parameters = template.parameters.copy()
            parameters.update(definition.parameters)
            if override_parameters:
                parameters.update(override_parameters)

            report_id = f"report_{uuid.uuid4().hex[:8]}"

            # Create pending report
            report = GeneratedReport(
                id=report_id,
                definition_id=definition_id,
                name=f"{definition.name} - {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')}",
                type=template.type,
                format=template.format,
                status=ReportStatus.GENERATING,
                parameters=parameters,
                data=None,
                file_path=None,
                file_size=None,
                generated_at=datetime.now(UTC).isoformat(),
                completed_at=None,
                error_message=None,
                recipient_emails=definition.recipients
            )

            self.generated_reports[report_id] = report

            try:
                # Simulate report generation process
                # In real implementation, this would execute the actual queries
                await asyncio.sleep(2)  # Simulate processing time

                # Generate sample data based on report type
                report_data = await self._generate_report_data(template.type, parameters)

                # In real implementation, this would save to file system
                file_path = f"/reports/{report_id}.{template.format.value}"

                # Update report with results
                report.status = ReportStatus.COMPLETED
                report.data = report_data
                report.file_path = file_path
                report.file_size = len(json.dumps(report_data))  # Simulated size
                report.completed_at = datetime.now(UTC).isoformat()

                logger.info(f"Generated report: {report.name}", report_id=report_id)
                return report

            except Exception as e:
                report.status = ReportStatus.FAILED
                report.error_message = str(e)
                report.completed_at = datetime.now(UTC).isoformat()
                raise

        except Exception as e:
            logger.error("Failed to generate report", error=str(e), definition_id=definition_id)
            raise

    async def _generate_report_data(self, report_type: ReportType, parameters: dict[str, Any]) -> dict[str, Any]:
        """Generate sample report data based on type."""
        now = datetime.now(UTC)

        if report_type == ReportType.SYSTEM_HEALTH:
            return {
                "report_period": f"Last 24 hours ({now.strftime('%Y-%m-%d')})",
                "overall_status": "HEALTHY",
                "services": [
                    {"name": "API Gateway", "status": "healthy", "response_time_ms": 45},
                    {"name": "Authentication", "status": "healthy", "response_time_ms": 62},
                    {"name": "Database", "status": "degraded", "response_time_ms": 180},
                    {"name": "Cache", "status": "healthy", "response_time_ms": 12}
                ],
                "metrics": {
                    "uptime_percentage": 99.8,
                    "average_response_time": 72.3,
                    "error_rate": 0.02
                },
                "alerts": [
                    {"severity": "warning", "message": "Database response time elevated", "timestamp": (now - timedelta(hours=2)).isoformat()}
                ]
            }

        elif report_type == ReportType.PERFORMANCE:
            # Generate time series data
            data_points = []
            for i in range(24):
                timestamp = (now - timedelta(hours=23-i)).isoformat()
                data_points.append({
                    "timestamp": timestamp,
                    "cpu_usage": 25 + (i % 8) + (20 * (i/24)),  # Increasing trend
                    "memory_usage": 45 + (i % 5) + (15 * (i/24)),
                    "response_time": 80 + (i % 10) + (40 * (i/24))
                })

            return {
                "report_period": f"Last 24 hours ({now.strftime('%Y-%m-%d')})",
                "metrics": parameters.get("metrics", ["cpu_usage", "memory_usage"]),
                "data_points": data_points,
                "statistics": {
                    "cpu_avg": 45.2,
                    "memory_avg": 62.8,
                    "response_time_avg": 120.5
                }
            }

        elif report_type == ReportType.SECURITY:
            return {
                "report_period": f"Last 30 days ({(now - timedelta(days=30)).strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')})",
                "total_vulnerabilities": 12,
                "by_severity": {
                    "critical": 2,
                    "high": 5,
                    "medium": 3,
                    "low": 2
                },
                "vulnerabilities": [
                    {
                        "id": "CVE-2024-12345",
                        "severity": "high",
                        "description": "SQL injection vulnerability in user authentication",
                        "detected_date": (now - timedelta(days=15)).isoformat(),
                        "status": "open"
                    },
                    {
                        "id": "CVE-2024-12346",
                        "severity": "medium",
                        "description": "Cross-site scripting vulnerability",
                        "detected_date": (now - timedelta(days=8)).isoformat(),
                        "status": "patched"
                    }
                ]
            }

        elif report_type == ReportType.USAGE:
            return {
                "report_period": f"Last 30 days ({(now - timedelta(days=30)).strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')})",
                "total_users": 1250,
                "active_users": 892,
                "by_role": {
                    "admin": 5,
                    "developer": 420,
                    "analyst": 180,
                    "viewer": 287
                },
                "engagement_metrics": {
                    "avg_sessions_per_user": 3.2,
                    "avg_session_duration_min": 28.5,
                    "feature_adoption_rate": 78.3
                }
            }

        else:  # CUSTOM
            return {
                "report_type": report_type.value,
                "generated_at": now.isoformat(),
                "parameters": parameters,
                "data": {"sample": "custom_report_data"}
            }

    async def get_generated_reports(
        self,
        definition_id: str | None = None,
        status: ReportStatus | None = None,
        limit: int = 50
    ) -> list[GeneratedReport]:
        """Get generated reports with optional filtering."""
        try:
            reports = list(self.generated_reports.values())

            if definition_id:
                reports = [r for r in reports if r.definition_id == definition_id]

            if status:
                reports = [r for r in reports if r.status == status]

            # Sort by generation time (newest first)
            reports.sort(key=lambda x: x.generated_at, reverse=True)

            return reports[:limit]

        except Exception as e:
            logger.error("Failed to get generated reports", error=str(e))
            raise

    async def get_report_definitions(self, active_only: bool = True) -> list[ReportDefinition]:
        """Get report definitions."""
        try:
            definitions = list(self.definitions.values())

            if active_only:
                definitions = [d for d in definitions if d.is_active]

            return definitions

        except Exception as e:
            logger.error("Failed to get report definitions", error=str(e))
            raise

    async def get_report_schedules(self, active_only: bool = True) -> list[ReportSchedule]:
        """Get report schedules."""
        try:
            schedules = list(self.schedules.values())

            if active_only:
                schedules = [s for s in schedules if s.is_active]

            # Sort by next run time
            schedules.sort(key=lambda x: x.next_run_time)

            return schedules

        except Exception as e:
            logger.error("Failed to get report schedules", error=str(e))
            raise

    async def export_report(self, report_id: str, format: ReportFormat) -> bytes:
        """Export a generated report in specified format."""
        try:
            report = self.generated_reports.get(report_id)
            if not report:
                raise ValueError(f"Report {report_id} not found")

            if report.status != ReportStatus.COMPLETED:
                raise ValueError("Report is not completed")

            # In real implementation, this would convert and return the actual file
            # For demo, we'll return JSON representation
            export_data = {
                "report_info": {
                    "id": report.id,
                    "name": report.name,
                    "type": report.type.value,
                    "generated_at": report.generated_at,
                    "completed_at": report.completed_at
                },
                "data": report.data
            }

            if format == ReportFormat.JSON:
                return json.dumps(export_data, indent=2).encode('utf-8')
            elif format == ReportFormat.CSV:
                # Convert to CSV format
                csv_content = "Report Data Export\n"
                csv_content += f"ID: {report.id}\n"
                csv_content += f"Name: {report.name}\n"
                csv_content += f"Generated: {report.generated_at}\n\n"
                csv_content += json.dumps(report.data, indent=2)
                return csv_content.encode('utf-8')
            else:
                # For other formats, return JSON as fallback
                return json.dumps(export_data, indent=2).encode('utf-8')

        except Exception as e:
            logger.error("Failed to export report", error=str(e), report_id=report_id)
            raise

    async def get_reporting_statistics(self) -> dict[str, Any]:
        """Get comprehensive reporting system statistics."""
        try:
            templates = await self.list_templates()
            definitions = await self.get_report_definitions()
            reports = await self.get_generated_reports()
            schedules = await self.get_report_schedules()

            # Calculate statistics
            status_counts = defaultdict(int)
            type_counts = defaultdict(int)

            for report in reports:
                status_counts[report.status.value] += 1
                type_counts[report.type.value] += 1

            stats = {
                "templates": {
                    "total": len(templates),
                    "system_default": len([t for t in templates if t.is_system_default]),
                    "custom": len([t for t in templates if not t.is_system_default])
                },
                "definitions": {
                    "total": len(definitions),
                    "active": len([d for d in definitions if d.is_active])
                },
                "reports": {
                    "total": len(reports),
                    "by_status": dict(status_counts),
                    "by_type": dict(type_counts),
                    "recent_24h": len([r for r in reports if "T" in r.generated_at and r.generated_at.split("T")[0] == datetime.now(UTC).strftime("%Y-%m-%d")])
                },
                "schedules": {
                    "total": len(schedules),
                    "active": len([s for s in schedules if s.is_active])
                }
            }

            return stats

        except Exception as e:
            logger.error("Failed to get reporting statistics", error=str(e))
            raise


# Global service instance
reporting_service = ReportingService()
