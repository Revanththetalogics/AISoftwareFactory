"""
Reporting API Routes

Provides REST endpoints for comprehensive reporting functionality including
report generation, scheduling, templates, and export capabilities.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.services.reporting_service import (
    ReportFormat,
    ReportFrequency,
    ReportStatus,
    ReportType,
    reporting_service,
)

router = APIRouter(prefix="/reports", tags=["Reporting"])
logger = get_logger(__name__)


class ReportTemplateCreate(BaseModel):
    """Report template creation request model."""
    name: str
    type: str
    description: str
    format: str
    parameters: dict[str, Any]
    query_template: str


class ReportDefinitionCreate(BaseModel):
    """Report definition creation request model."""
    name: str
    template_id: str
    parameters: dict[str, Any]
    recipients: list[str]
    schedule_frequency: str
    schedule_time: str | None = None


class ReportGenerateRequest(BaseModel):
    """Report generation request model."""
    definition_id: str
    override_parameters: dict[str, Any] | None = None


@router.get("/templates/", response_model=APIResponse)
async def list_report_templates(
    report_type: str | None = None,
    include_system: bool = True
):
    """
    List available report templates.
    
    Args:
        report_type: Filter by report type
        include_system: Whether to include system default templates
        
    Returns:
        APIResponse with list of templates
    """
    try:
        report_type_enum = ReportType(report_type) if report_type else None
        templates = await reporting_service.list_templates(report_type_enum, include_system)
        templates_data = [template.__dict__ for template in templates]

        return APIResponse(
            success=True,
            data=templates_data,
            message=f"Retrieved {len(templates_data)} report templates"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to list report templates", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list report templates: {str(e)}")


@router.post("/templates/", response_model=APIResponse)
async def create_report_template(template_data: ReportTemplateCreate):
    """
    Create a new report template.
    
    Args:
        template_data: Template creation data
        
    Returns:
        APIResponse with created template
    """
    try:
        # For demo purposes, using a fixed user ID
        created_by = "admin_1"

        template = await reporting_service.create_report_template(
            name=template_data.name,
            report_type=ReportType(template_data.type),
            description=template_data.description,
            format=ReportFormat(template_data.format),
            parameters=template_data.parameters,
            query_template=template_data.query_template,
            created_by=created_by
        )

        return APIResponse(
            success=True,
            data=template.__dict__,
            message=f"Report template '{template.name}' created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to create report template", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create report template: {str(e)}")


@router.get("/templates/{template_id}", response_model=APIResponse)
async def get_report_template(template_id: str):
    """
    Get a specific report template.
    
    Args:
        template_id: ID of the template
        
    Returns:
        APIResponse with template data
    """
    try:
        template = await reporting_service.get_template(template_id)

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        return APIResponse(
            success=True,
            data=template.__dict__,
            message=f"Retrieved template '{template.name}'"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get report template", error=str(e), template_id=template_id)
        raise HTTPException(status_code=500, detail=f"Failed to get report template: {str(e)}")


@router.get("/definitions/", response_model=APIResponse)
async def list_report_definitions(active_only: bool = True):
    """
    List report definitions.
    
    Args:
        active_only: Whether to return only active definitions
        
    Returns:
        APIResponse with list of definitions
    """
    try:
        definitions = await reporting_service.get_report_definitions(active_only)
        definitions_data = [definition.__dict__ for definition in definitions]

        return APIResponse(
            success=True,
            data=definitions_data,
            message=f"Retrieved {len(definitions_data)} report definitions"
        )
    except Exception as e:
        logger.error("Failed to list report definitions", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list report definitions: {str(e)}")


@router.post("/definitions/", response_model=APIResponse)
async def create_report_definition(definition_data: ReportDefinitionCreate):
    """
    Create a new report definition.
    
    Args:
        definition_data: Definition creation data
        
    Returns:
        APIResponse with created definition
    """
    try:
        # For demo purposes, using a fixed user ID
        created_by = "admin_1"

        definition = await reporting_service.create_report_definition(
            name=definition_data.name,
            template_id=definition_data.template_id,
            parameters=definition_data.parameters,
            recipients=definition_data.recipients,
            schedule_frequency=ReportFrequency(definition_data.schedule_frequency),
            schedule_time=definition_data.schedule_time,
            created_by=created_by
        )

        definition_dict = definition.__dict__.copy()
        # Convert enum values to strings for serialization
        definition_dict['schedule_frequency'] = definition.schedule_frequency.value

        return APIResponse(
            success=True,
            data=definition_dict,
            message=f"Report definition '{definition.name}' created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to create report definition", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create report definition: {str(e)}")


@router.post("/generate", response_model=APIResponse)
async def generate_report(generate_request: ReportGenerateRequest):
    """
    Generate a report based on definition.
    
    Args:
        generate_request: Report generation request
        
    Returns:
        APIResponse with generated report information
    """
    try:
        report = await reporting_service.generate_report(
            definition_id=generate_request.definition_id,
            override_parameters=generate_request.override_parameters
        )

        report_dict = report.__dict__.copy()
        # Convert enum values to strings
        report_dict['type'] = report.type.value
        report_dict['format'] = report.format.value
        report_dict['status'] = report.status.value

        return APIResponse(
            success=True,
            data=report_dict,
            message=f"Report '{report.name}' generated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to generate report", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/generated/", response_model=APIResponse)
async def list_generated_reports(
    definition_id: str | None = None,
    status: str | None = None,
    limit: int = 50
):
    """
    List generated reports.
    
    Args:
        definition_id: Filter by definition ID
        status: Filter by report status
        limit: Maximum number of reports to return
        
    Returns:
        APIResponse with list of generated reports
    """
    try:
        status_enum = ReportStatus(status) if status else None
        reports = await reporting_service.get_generated_reports(definition_id, status_enum, limit)
        reports_data = []

        for report in reports:
            report_dict = report.__dict__.copy()
            # Convert enum values to strings
            report_dict['type'] = report.type.value
            report_dict['format'] = report.format.value
            report_dict['status'] = report.status.value
            reports_data.append(report_dict)

        return APIResponse(
            success=True,
            data=reports_data,
            message=f"Retrieved {len(reports_data)} generated reports"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to list generated reports", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list generated reports: {str(e)}")


@router.get("/generated/{report_id}", response_model=APIResponse)
async def get_generated_report(report_id: str):
    """
    Get a specific generated report.
    
    Args:
        report_id: ID of the generated report
        
    Returns:
        APIResponse with report data
    """
    try:
        report = reporting_service.generated_reports.get(report_id)

        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        report_dict = report.__dict__.copy()
        # Convert enum values to strings
        report_dict['type'] = report.type.value
        report_dict['format'] = report.format.value
        report_dict['status'] = report.status.value

        return APIResponse(
            success=True,
            data=report_dict,
            message=f"Retrieved report '{report.name}'"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get generated report", error=str(e), report_id=report_id)
        raise HTTPException(status_code=500, detail=f"Failed to get generated report: {str(e)}")


@router.get("/schedules/", response_model=APIResponse)
async def list_report_schedules(active_only: bool = True):
    """
    List report schedules.
    
    Args:
        active_only: Whether to return only active schedules
        
    Returns:
        APIResponse with list of schedules
    """
    try:
        schedules = await reporting_service.get_report_schedules(active_only)
        schedules_data = []

        for schedule in schedules:
            schedule_dict = schedule.__dict__.copy()
            schedule_dict['frequency'] = schedule.frequency.value
            schedules_data.append(schedule_dict)

        return APIResponse(
            success=True,
            data=schedules_data,
            message=f"Retrieved {len(schedules_data)} report schedules"
        )
    except Exception as e:
        logger.error("Failed to list report schedules", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list report schedules: {str(e)}")


@router.get("/export/{report_id}/{format}", response_model=APIResponse)
async def export_report(report_id: str, format: str):
    """
    Export a generated report in specified format.
    
    Args:
        report_id: ID of the report to export
        format: Export format (pdf, csv, json, html, excel)
        
    Returns:
        APIResponse with exported report data
    """
    try:
        format_enum = ReportFormat(format.lower())
        export_data = await reporting_service.export_report(report_id, format_enum)

        # Return the export data
        return Response(
            content=export_data,
            media_type=f"text/{format.lower()}",
            headers={"Content-Disposition": f"attachment; filename=report_{report_id}.{format.lower()}"}
        )
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid format: {format}")
    except Exception as e:
        logger.error("Failed to export report", error=str(e), report_id=report_id)
        raise HTTPException(status_code=500, detail=f"Failed to export report: {str(e)}")


@router.get("/types", response_model=APIResponse)
async def get_report_types():
    """
    Get list of available report types.
    
    Returns:
        APIResponse with report types
    """
    try:
        types = [{"name": rt.name, "value": rt.value} for rt in ReportType]

        return APIResponse(
            success=True,
            data=types,
            message="Retrieved available report types"
        )
    except Exception as e:
        logger.error("Failed to get report types", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get report types: {str(e)}")


@router.get("/formats", response_model=APIResponse)
async def get_report_formats():
    """
    Get list of available report formats.
    
    Returns:
        APIResponse with report formats
    """
    try:
        formats = [{"name": rf.name, "value": rf.value} for rf in ReportFormat]

        return APIResponse(
            success=True,
            data=formats,
            message="Retrieved available report formats"
        )
    except Exception as e:
        logger.error("Failed to get report formats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get report formats: {str(e)}")


@router.get("/frequencies", response_model=APIResponse)
async def get_report_frequencies():
    """
    Get list of available report frequencies.
    
    Returns:
        APIResponse with report frequencies
    """
    try:
        frequencies = [{"name": rf.name, "value": rf.value} for rf in ReportFrequency]

        return APIResponse(
            success=True,
            data=frequencies,
            message="Retrieved available report frequencies"
        )
    except Exception as e:
        logger.error("Failed to get report frequencies", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get report frequencies: {str(e)}")


@router.get("/statuses", response_model=APIResponse)
async def get_report_statuses():
    """
    Get list of available report statuses.
    
    Returns:
        APIResponse with report statuses
    """
    try:
        statuses = [{"name": rs.name, "value": rs.value} for rs in ReportStatus]

        return APIResponse(
            success=True,
            data=statuses,
            message="Retrieved available report statuses"
        )
    except Exception as e:
        logger.error("Failed to get report statuses", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get report statuses: {str(e)}")


@router.get("/dashboard", response_model=APIResponse)
async def get_reporting_dashboard():
    """
    Get comprehensive reporting dashboard data.
    
    Returns:
        APIResponse with dashboard information
    """
    try:
        # Get all relevant reporting data
        templates = await reporting_service.list_templates()
        definitions = await reporting_service.get_report_definitions()
        reports = await reporting_service.get_generated_reports(limit=20)
        schedules = await reporting_service.get_report_schedules()
        stats = await reporting_service.get_reporting_statistics()

        dashboard_data = {
            "statistics": stats,
            "recent_reports": [],
            "active_schedules": [],
            "system_templates": len([t for t in templates if t.is_system_default])
        }

        # Add recent reports data
        for report in reports:
            report_dict = report.__dict__.copy()
            report_dict['type'] = report.type.value
            report_dict['status'] = report.status.value
            dashboard_data['recent_reports'].append(report_dict)

        # Add active schedules data
        for schedule in schedules:
            schedule_dict = schedule.__dict__.copy()
            schedule_dict['frequency'] = schedule.frequency.value
            dashboard_data['active_schedules'].append(schedule_dict)

        return APIResponse(
            success=True,
            data=dashboard_data,
            message="Retrieved reporting dashboard data"
        )
    except Exception as e:
        logger.error("Failed to get reporting dashboard", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get reporting dashboard: {str(e)}")


@router.get("/stats", response_model=APIResponse)
async def get_reporting_statistics():
    """
    Get comprehensive reporting system statistics.
    
    Returns:
        APIResponse with reporting statistics
    """
    try:
        stats = await reporting_service.get_reporting_statistics()

        return APIResponse(
            success=True,
            data=stats,
            message="Retrieved reporting system statistics"
        )
    except Exception as e:
        logger.error("Failed to get reporting statistics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get reporting statistics: {str(e)}")


@router.delete("/definitions/{definition_id}", response_model=APIResponse)
async def delete_report_definition(definition_id: str):
    """
    Delete a report definition.
    
    Args:
        definition_id: ID of the definition to delete
        
    Returns:
        APIResponse confirming deletion
    """
    try:
        definition = reporting_service.definitions.get(definition_id)
        if not definition:
            raise HTTPException(status_code=404, detail="Report definition not found")

        # Deactivate the definition
        definition.is_active = False
        definition.updated_at = datetime.now(UTC).isoformat()

        # Also deactivate associated schedules
        for schedule in reporting_service.schedules.values():
            if schedule.definition_id == definition_id:
                schedule.is_active = False

        return APIResponse(
            success=True,
            message=f"Report definition '{definition.name}' deactivated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete report definition", error=str(e), definition_id=definition_id)
        raise HTTPException(status_code=500, detail=f"Failed to delete report definition: {str(e)}")
