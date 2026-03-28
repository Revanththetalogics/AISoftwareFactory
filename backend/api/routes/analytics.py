"""
Advanced Analytics API Routes

Provides REST endpoints for advanced analytics, reporting, and predictive analytics.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.services.analytics_engine import ReportType, TimeGranularity, analytics_engine

router = APIRouter(prefix="/analytics", tags=["Advanced Analytics"])
logger = get_logger(__name__)


class AnalyticsQueryCreate(BaseModel):
    """Analytics query creation request model."""
    name: str
    metrics: list[str]
    dimensions: list[str]
    filters: dict[str, Any]
    time_range: dict[str, str]  # start_date, end_date
    granularity: str


class ReportGenerateRequest(BaseModel):
    """Report generation request model."""
    query_id: str
    report_type: str
    visualization_type: str | None = "table"


class PredictionRequest(BaseModel):
    """Prediction request model."""
    metric: str
    periods: int
    model_type: str | None = "linear_regression"


class TrendAnalysisRequest(BaseModel):
    """Trend analysis request model."""
    metric: str
    time_range: dict[str, str]


class CorrelationAnalysisRequest(BaseModel):
    """Correlation analysis request model."""
    metrics: list[str]
    time_range: dict[str, str]


@router.post("/queries/", response_model=APIResponse)
async def create_analytics_query(query_data: AnalyticsQueryCreate):
    """
    Create a new analytics query.

    Args:
        query_data: Analytics query creation data

    Returns:
        APIResponse with created query
    """
    try:
        query = await analytics_engine.create_analytics_query(
            name=query_data.name,
            metrics=query_data.metrics,
            dimensions=query_data.dimensions,
            filters=query_data.filters,
            time_range=query_data.time_range,
            granularity=TimeGranularity(query_data.granularity)
        )

        return APIResponse(
            success=True,
            data=query.__dict__,
            message=f"Analytics query '{query_data.name}' created successfully"
        )
    except Exception as e:
        logger.error("Failed to create analytics query", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create analytics query: {str(e)}")


@router.get("/queries/", response_model=APIResponse)
async def list_queries():
    """
    List all analytics queries.

    Returns:
        APIResponse with list of queries
    """
    try:
        queries = await analytics_engine.list_queries()
        queries_data = [query.__dict__ for query in queries]

        return APIResponse(
            success=True,
            data=queries_data,
            message=f"Retrieved {len(queries_data)} analytics queries"
        )
    except Exception as e:
        logger.error("Failed to list queries", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list queries: {str(e)}")


@router.post("/queries/{query_id}/execute", response_model=APIResponse)
async def execute_query(query_id: str):
    """
    Execute an analytics query.

    Args:
        query_id: ID of the query to execute

    Returns:
        APIResponse with query results
    """
    try:
        results = await analytics_engine.execute_query(query_id)

        return APIResponse(
            success=True,
            data=results,
            message="Query executed successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to execute query", error=str(e), query_id=query_id)
        raise HTTPException(status_code=500, detail=f"Failed to execute query: {str(e)}")


@router.post("/reports/", response_model=APIResponse)
async def generate_report(report_request: ReportGenerateRequest):
    """
    Generate an analytics report.

    Args:
        report_request: Report generation request data

    Returns:
        APIResponse with generated report
    """
    try:
        report = await analytics_engine.generate_report(
            query_id=report_request.query_id,
            report_type=ReportType(report_request.report_type),
            visualization_type=report_request.visualization_type
        )

        report_dict = report.__dict__.copy()
        report_dict["query"] = report.query.__dict__

        return APIResponse(
            success=True,
            data=report_dict,
            message=f"Report '{report.name}' generated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to generate report", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/reports/", response_model=APIResponse)
async def list_reports():
    """
    List all analytics reports.

    Returns:
        APIResponse with list of reports
    """
    try:
        reports = await analytics_engine.list_reports()
        reports_data = []

        for report in reports:
            report_dict = report.__dict__.copy()
            report_dict["query"] = report.query.__dict__
            reports_data.append(report_dict)

        return APIResponse(
            success=True,
            data=reports_data,
            message=f"Retrieved {len(reports_data)} analytics reports"
        )
    except Exception as e:
        logger.error("Failed to list reports", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")


@router.get("/reports/{report_id}", response_model=APIResponse)
async def get_report(report_id: str):
    """
    Get a specific analytics report.

    Args:
        report_id: ID of the report to retrieve

    Returns:
        APIResponse with report data
    """
    try:
        # Find report by ID
        reports = await analytics_engine.list_reports()
        report = next((r for r in reports if r.id == report_id), None)

        if not report:
            raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

        report_dict = report.__dict__.copy()
        report_dict["query"] = report.query.__dict__

        return APIResponse(
            success=True,
            data=report_dict,
            message=f"Retrieved report '{report.name}'"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get report", error=str(e), report_id=report_id)
        raise HTTPException(status_code=500, detail=f"Failed to get report: {str(e)}")


@router.post("/predict", response_model=APIResponse)
async def predict_future_values(prediction_request: PredictionRequest):
    """
    Predict future values for a metric.

    Args:
        prediction_request: Prediction request data

    Returns:
        APIResponse with prediction results
    """
    try:
        prediction = await analytics_engine.predict_future_values(
            metric=prediction_request.metric,
            periods=prediction_request.periods,
            model_type=prediction_request.model_type
        )

        return APIResponse(
            success=True,
            data=prediction.__dict__,
            message=f"Predictions generated for {prediction_request.metric}"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to generate predictions", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate predictions: {str(e)}")


@router.get("/predictions/", response_model=APIResponse)
async def list_predictions():
    """
    List all prediction results.

    Returns:
        APIResponse with list of predictions
    """
    try:
        predictions = await analytics_engine.list_predictions()
        predictions_data = [prediction.__dict__ for prediction in predictions]

        return APIResponse(
            success=True,
            data=predictions_data,
            message=f"Retrieved {len(predictions_data)} predictions"
        )
    except Exception as e:
        logger.error("Failed to list predictions", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list predictions: {str(e)}")


@router.post("/trend-analysis", response_model=APIResponse)
async def get_trend_analysis(trend_request: TrendAnalysisRequest):
    """
    Perform trend analysis on a metric.

    Args:
        trend_request: Trend analysis request data

    Returns:
        APIResponse with trend analysis results
    """
    try:
        trend_data = await analytics_engine.get_trend_analysis(
            metric=trend_request.metric,
            time_range=trend_request.time_range
        )

        return APIResponse(
            success=True,
            data=trend_data,
            message=f"Trend analysis completed for {trend_request.metric}"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to perform trend analysis", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to perform trend analysis: {str(e)}")


@router.post("/correlation-analysis", response_model=APIResponse)
async def get_correlation_analysis(correlation_request: CorrelationAnalysisRequest):
    """
    Perform correlation analysis between metrics.

    Args:
        correlation_request: Correlation analysis request data

    Returns:
        APIResponse with correlation analysis results
    """
    try:
        correlation_data = await analytics_engine.get_correlation_analysis(
            metrics=correlation_request.metrics,
            time_range=correlation_request.time_range
        )

        return APIResponse(
            success=True,
            data=correlation_data,
            message=f"Correlation analysis completed for {len(correlation_request.metrics)} metrics"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to perform correlation analysis", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to perform correlation analysis: {str(e)}")


@router.get("/metrics/available", response_model=APIResponse)
async def get_available_metrics():
    """
    Get list of available metrics for analytics.

    Returns:
        APIResponse with list of available metrics
    """
    try:
        metrics = [
            {"name": "projects_created", "description": "Number of projects created", "type": "count"},
            {"name": "active_users", "description": "Number of active users", "type": "count"},
            {"name": "conversion_rate", "description": "User conversion rate", "type": "percentage"},
            {"name": "revenue", "description": "Revenue generated", "type": "sum"},
            {"name": "session_duration", "description": "Average session duration", "type": "average"}
        ]

        return APIResponse(
            success=True,
            data=metrics,
            message="Retrieved available metrics"
        )
    except Exception as e:
        logger.error("Failed to get available metrics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get available metrics: {str(e)}")


@router.get("/granularities/available", response_model=APIResponse)
async def get_available_granularities():
    """
    Get list of available time granularities.

    Returns:
        APIResponse with list of available granularities
    """
    try:
        granularities = [{"name": t.name, "value": t.value} for t in TimeGranularity]

        return APIResponse(
            success=True,
            data=granularities,
            message="Retrieved available granularities"
        )
    except Exception as e:
        logger.error("Failed to get available granularities", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get available granularities: {str(e)}")


@router.get("/report-types/available", response_model=APIResponse)
async def get_available_report_types():
    """
    Get list of available report types.

    Returns:
        APIResponse with list of available report types
    """
    try:
        report_types = [{"name": t.name, "value": t.value} for t in ReportType]

        return APIResponse(
            success=True,
            data=report_types,
            message="Retrieved available report types"
        )
    except Exception as e:
        logger.error("Failed to get available report types", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get available report types: {str(e)}")


@router.get("/dashboard-summary", response_model=APIResponse)
async def get_analytics_dashboard_summary():
    """
    Get analytics dashboard summary with key metrics.

    Returns:
        APIResponse with dashboard summary data
    """
    try:
        # Get recent reports and predictions for summary
        reports = await analytics_engine.list_reports()
        predictions = await analytics_engine.list_predictions()

        # Generate summary statistics
        summary = {
            "total_queries": len(await analytics_engine.list_queries()),
            "total_reports": len(reports),
            "total_predictions": len(predictions),
            "recent_activity": {
                "reports_last_24h": len([r for r in reports if "today" in r.generated_at]),
                "predictions_last_week": len([p for p in predictions if "week" in p.created_at])
            },
            "popular_metrics": ["projects_created", "active_users", "conversion_rate"]
        }

        return APIResponse(
            success=True,
            data=summary,
            message="Retrieved analytics dashboard summary"
        )
    except Exception as e:
        logger.error("Failed to get dashboard summary", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard summary: {str(e)}")
