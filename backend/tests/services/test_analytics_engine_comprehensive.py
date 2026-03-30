"""
Comprehensive tests for AdvancedAnalyticsEngine to increase coverage.
"""

from datetime import UTC, datetime, timedelta

import pytest
from backend.services.analytics_engine import (
    AdvancedAnalyticsEngine,
    AnalyticsQuery,
    AnalyticsReport,
    DataPoint,
    MetricType,
    PredictionResult,
    ReportType,
    TimeGranularity,
    TimeSeries,
)


class TestAdvancedAnalyticsEngine:
    """Comprehensive tests for AdvancedAnalyticsEngine."""

    @pytest.fixture
    def analytics_engine(self):
        """Create AdvancedAnalyticsEngine instance."""
        return AdvancedAnalyticsEngine()

    def test_init(self, analytics_engine):
        """Test AdvancedAnalyticsEngine initialization."""
        assert analytics_engine is not None
        assert hasattr(analytics_engine, 'queries')
        assert hasattr(analytics_engine, 'reports')
        assert hasattr(analytics_engine, 'predictions')
        assert hasattr(analytics_engine, 'project_series')
        assert hasattr(analytics_engine, 'user_series')
        assert isinstance(analytics_engine.queries, dict)
        assert isinstance(analytics_engine.reports, dict)
        assert isinstance(analytics_engine.predictions, dict)

    def test_sample_data_initialization(self, analytics_engine):
        """Test that sample data is properly initialized."""
        # Check project series
        assert analytics_engine.project_series is not None
        assert isinstance(analytics_engine.project_series, TimeSeries)
        assert analytics_engine.project_series.name == "Projects Created"
        assert analytics_engine.project_series.metric_type == MetricType.COUNT
        assert len(analytics_engine.project_series.data_points) > 0

        # Check user series
        assert analytics_engine.user_series is not None
        assert isinstance(analytics_engine.user_series, TimeSeries)
        assert analytics_engine.user_series.name == "Active Users"
        assert analytics_engine.user_series.metric_type == MetricType.COUNT
        assert len(analytics_engine.user_series.data_points) > 0

        # Check data points
        for dp in analytics_engine.project_series.data_points:
            assert isinstance(dp, DataPoint)
            assert isinstance(dp.timestamp, str)
            assert isinstance(dp.value, float)

    @pytest.mark.asyncio
    async def test_create_analytics_query_success(self, analytics_engine):
        """Test creating analytics query successfully."""
        result = await analytics_engine.create_analytics_query(
            name="Test Query",
            metrics=["projects_created", "active_users"],
            dimensions=["date"],
            filters={"status": "active"},
            time_range={
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z"
            },
            granularity=TimeGranularity.DAY
        )

        assert result is not None
        assert isinstance(result, AnalyticsQuery)
        assert result.name == "Test Query"
        assert "projects_created" in result.metrics
        assert "active_users" in result.metrics
        assert result.dimensions == ["date"]
        assert result.filters == {"status": "active"}
        assert result.granularity == TimeGranularity.DAY
        assert len(result.id) > 0

    @pytest.mark.asyncio
    async def test_execute_query_success(self, analytics_engine):
        """Test executing query successfully."""
        # Create a query first
        query = await analytics_engine.create_analytics_query(
            name="Execution Test",
            metrics=["projects_created"],
            dimensions=["date"],
            filters={},
            time_range={
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-01-31T23:59:59Z"
            },
            granularity=TimeGranularity.DAY
        )

        # Execute the query
        result = await analytics_engine.execute_query(query.id)

        assert isinstance(result, dict)
        assert "projects_created" in result
        assert isinstance(result["projects_created"], list)

        # Check data structure
        data_point = result["projects_created"][0]
        assert "period" in data_point
        assert "value" in data_point
        assert "average" in data_point
        assert "count" in data_point

    @pytest.mark.asyncio
    async def test_execute_query_not_found(self, analytics_engine):
        """Test executing non-existent query."""
        with pytest.raises(ValueError) as exc_info:
            await analytics_engine.execute_query("nonexistent_query_id")

        assert "Query nonexistent_query_id not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_report_success(self, analytics_engine):
        """Test generating report successfully."""
        # Create and execute a query first
        query = await analytics_engine.create_analytics_query(
            name="Report Test",
            metrics=["active_users"],
            dimensions=["date"],
            filters={},
            time_range={
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-01-31T23:59:59Z"
            },
            granularity=TimeGranularity.WEEK
        )

        # Generate report
        result = await analytics_engine.generate_report(
            query_id=query.id,
            report_type=ReportType.SUMMARY,
            visualization_type="chart"
        )

        assert result is not None
        assert isinstance(result, AnalyticsReport)
        assert result.name == "Report Test Report"
        assert result.type == ReportType.SUMMARY
        assert result.visualization_type == "chart"
        assert result.query.id == query.id
        assert isinstance(result.data, dict)
        assert len(result.id) > 0

    @pytest.mark.asyncio
    async def test_generate_report_query_not_found(self, analytics_engine):
        """Test generating report with non-existent query."""
        with pytest.raises(ValueError) as exc_info:
            await analytics_engine.generate_report(
                query_id="nonexistent",
                report_type=ReportType.SUMMARY
            )

        assert "Query nonexistent not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_predict_future_values_projects(self, analytics_engine):
        """Test predicting future values for projects metric."""
        result = await analytics_engine.predict_future_values(
            metric="projects_created",
            periods=5,
            model_type="linear_regression"
        )

        assert result is not None
        assert isinstance(result, PredictionResult)
        assert result.metric == "projects_created"
        assert result.model_type == "linear_regression"
        assert len(result.predicted_values) == 5
        assert isinstance(result.confidence_interval, tuple)
        assert len(result.confidence_interval) == 2
        assert 0 <= result.accuracy_score <= 1

        # Check predicted values
        for dp in result.predicted_values:
            assert isinstance(dp, DataPoint)
            assert isinstance(dp.timestamp, str)
            assert isinstance(dp.value, float)
            assert dp.value >= 0  # Should be non-negative

    @pytest.mark.asyncio
    async def test_predict_future_values_users(self, analytics_engine):
        """Test predicting future values for users metric."""
        result = await analytics_engine.predict_future_values(
            metric="active_users",
            periods=3,
            model_type="linear_regression"
        )

        assert result is not None
        assert result.metric == "active_users"
        assert len(result.predicted_values) == 3

    @pytest.mark.asyncio
    async def test_predict_future_values_unknown_metric(self, analytics_engine):
        """Test predicting future values with unknown metric."""
        with pytest.raises(ValueError) as exc_info:
            await analytics_engine.predict_future_values(
                metric="unknown_metric",
                periods=5
            )

        assert "Unknown metric: unknown_metric" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_trend_analysis_projects(self, analytics_engine):
        """Test trend analysis for projects metric."""
        # Use a time range that covers the sample data (last 30 days)
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=25)
        time_range = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }

        result = await analytics_engine.get_trend_analysis(
            metric="projects_created",
            time_range=time_range
        )

        assert isinstance(result, dict)
        assert result["metric"] == "projects_created"
        assert "trend_direction" in result
        assert "trend_strength" in result
        assert "trend_classification" in result
        assert "slope" in result
        assert "volatility" in result
        assert result["data_points"] > 0
        assert "period_start" in result
        assert "period_end" in result

    @pytest.mark.asyncio
    async def test_get_trend_analysis_users(self, analytics_engine):
        """Test trend analysis for users metric."""
        # Use a time range that covers the sample data (last 30 days)
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=25)
        time_range = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }

        result = await analytics_engine.get_trend_analysis(
            metric="active_users",
            time_range=time_range
        )

        assert result["metric"] == "active_users"

    @pytest.mark.asyncio
    async def test_get_trend_analysis_insufficient_data(self, analytics_engine):
        """Test trend analysis with insufficient data."""
        # Create a time range that will result in very few data points
        time_range = {
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-01T01:00:00Z"  # Only 1 hour
        }

        result = await analytics_engine.get_trend_analysis(
            metric="projects_created",
            time_range=time_range
        )

        # Should handle gracefully with error message
        assert isinstance(result, dict)
        if "error" in result:
            assert "Insufficient data" in result["error"]

    @pytest.mark.asyncio
    async def test_get_trend_analysis_unknown_metric(self, analytics_engine):
        """Test trend analysis with unknown metric."""
        with pytest.raises(ValueError) as exc_info:
            await analytics_engine.get_trend_analysis(
                metric="unknown_metric",
                time_range={
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-01-31T23:59:59Z"
                }
            )

        assert "Unknown metric: unknown_metric" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_correlation_analysis_success(self, analytics_engine):
        """Test correlation analysis between metrics."""
        # Use a time range that covers the sample data (last 30 days)
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=25)
        time_range = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }

        result = await analytics_engine.get_correlation_analysis(
            metrics=["projects_created", "active_users"],
            time_range=time_range
        )

        assert isinstance(result, dict)
        assert "correlations" in result
        assert "data_points" in result
        assert "metrics_analyzed" in result

        correlations = result["correlations"]
        assert "projects_created_vs_active_users" in correlations
        assert isinstance(correlations["projects_created_vs_active_users"], float)
        assert -1 <= correlations["projects_created_vs_active_users"] <= 1

    @pytest.mark.asyncio
    async def test_get_correlation_analysis_single_metric(self, analytics_engine):
        """Test correlation analysis with single metric (should handle gracefully)."""
        # Use a time range that covers the sample data (last 30 days)
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=25)
        time_range = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }

        result = await analytics_engine.get_correlation_analysis(
            metrics=["projects_created"],
            time_range=time_range
        )

        # Should handle gracefully - no correlations possible with single metric
        assert isinstance(result, dict)
        assert "correlations" in result

    @pytest.mark.asyncio
    async def test_get_correlation_analysis_unknown_metric(self, analytics_engine):
        """Test correlation analysis with unknown metric."""
        with pytest.raises(ValueError) as exc_info:
            await analytics_engine.get_correlation_analysis(
                metrics=["projects_created", "unknown_metric"],
                time_range={
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-01-31T23:59:59Z"
                }
            )

        assert "Unknown metric: unknown_metric" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_queries(self, analytics_engine):
        """Test listing all queries."""
        # Create a few queries
        await analytics_engine.create_analytics_query(
            name="Query 1", metrics=["projects_created"], dimensions=[],
            filters={}, time_range={"start_date": "2024-01-01T00:00:00Z", "end_date": "2024-12-31T23:59:59Z"},
            granularity=TimeGranularity.DAY
        )

        await analytics_engine.create_analytics_query(
            name="Query 2", metrics=["active_users"], dimensions=[],
            filters={}, time_range={"start_date": "2024-01-01T00:00:00Z", "end_date": "2024-12-31T23:59:59Z"},
            granularity=TimeGranularity.DAY
        )

        result = await analytics_engine.list_queries()

        assert isinstance(result, list)
        assert len(result) >= 2

        for query in result:
            assert isinstance(query, AnalyticsQuery)

    @pytest.mark.asyncio
    async def test_list_reports(self, analytics_engine):
        """Test listing all reports."""
        # Create a query and generate a report
        query = await analytics_engine.create_analytics_query(
            name="Report List Test", metrics=["projects_created"], dimensions=[],
            filters={}, time_range={"start_date": "2024-01-01T00:00:00Z", "end_date": "2024-12-31T23:59:59Z"},
            granularity=TimeGranularity.DAY
        )

        await analytics_engine.generate_report(query.id, ReportType.SUMMARY)

        result = await analytics_engine.list_reports()

        assert isinstance(result, list)
        assert len(result) >= 1

        for report in result:
            assert isinstance(report, AnalyticsReport)

    @pytest.mark.asyncio
    async def test_list_predictions(self, analytics_engine):
        """Test listing all predictions."""
        # Generate a prediction
        await analytics_engine.predict_future_values("projects_created", 3)

        result = await analytics_engine.list_predictions()

        assert isinstance(result, list)
        assert len(result) >= 1

        for prediction in result:
            assert isinstance(prediction, PredictionResult)

    def test_aggregate_time_series_day_granularity(self, analytics_engine):
        """Test time series aggregation with day granularity."""
        time_range = {
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-10T23:59:59Z"
        }

        result = analytics_engine._aggregate_time_series(
            analytics_engine.project_series,
            time_range,
            TimeGranularity.DAY
        )

        assert isinstance(result, list)
        if result:  # If there's data
            data_point = result[0]
            assert "period" in data_point
            assert "value" in data_point
            assert "average" in data_point
            assert "count" in data_point
            assert "-" in data_point["period"]  # Should be YYYY-MM-DD format

    def test_aggregate_time_series_month_granularity(self, analytics_engine):
        """Test time series aggregation with month granularity."""
        time_range = {
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-03-31T23:59:59Z"
        }

        result = analytics_engine._aggregate_time_series(
            analytics_engine.user_series,
            time_range,
            TimeGranularity.MONTH
        )

        assert isinstance(result, list)
        if result:
            data_point = result[0]
            assert "-" in data_point["period"]  # Should be YYYY-MM format

    def test_calculate_conversion_rate(self, analytics_engine):
        """Test conversion rate calculation."""
        time_range = {
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-31T23:59:59Z"
        }

        result = analytics_engine._calculate_conversion_rate(time_range)

        assert isinstance(result, float)
        assert 0 <= result <= 1  # Should be between 0 and 1

    def test_apply_filters(self, analytics_engine):
        """Test applying filters to data."""
        test_data = {"metric1": 100, "metric2": 200}
        filters = {"status": "active"}

        result = analytics_engine._apply_filters(test_data, filters)

        # Should return the data unchanged (simplified implementation)
        assert result == test_data

    def test_filter_by_time_range(self, analytics_engine):
        """Test filtering data points by time range."""
        # Create test data points
        now = datetime.now(UTC)
        data_points = [
            DataPoint((now - timedelta(days=5)).isoformat(), 10.0),
            DataPoint((now - timedelta(days=2)).isoformat(), 20.0),
            DataPoint((now + timedelta(days=1)).isoformat(), 30.0)
        ]

        time_range = {
            "start_date": (now - timedelta(days=3)).isoformat(),
            "end_date": (now + timedelta(days=2)).isoformat()
        }

        result = analytics_engine._filter_by_time_range(data_points, time_range)

        assert isinstance(result, list)
        # Should include middle and last points (within range)
        assert len(result) >= 2
        for dp in result:
            assert isinstance(dp, DataPoint)

    def test_linear_regression_predict(self, analytics_engine):
        """Test linear regression prediction."""
        # Create a simple time series
        data_points = [
            DataPoint("2024-01-01T00:00:00Z", 10.0),
            DataPoint("2024-01-02T00:00:00Z", 15.0),
            DataPoint("2024-01-03T00:00:00Z", 20.0),
            DataPoint("2024-01-04T00:00:00Z", 25.0)
        ]

        series = TimeSeries("Test Series", data_points, MetricType.COUNT)

        result = analytics_engine._linear_regression_predict(series, 3)

        assert isinstance(result, list)
        assert len(result) == 3
        for dp in result:
            assert isinstance(dp, DataPoint)
            assert isinstance(dp.timestamp, str)
            assert isinstance(dp.value, float)
            assert dp.value >= 0

    def test_calculate_linear_trend(self, analytics_engine):
        """Test linear trend calculation."""
        x_values = [1, 2, 3, 4, 5]
        y_values = [10, 15, 20, 25, 30]  # Perfect linear relationship

        slope, intercept = analytics_engine._calculate_linear_trend(x_values, y_values)

        assert isinstance(slope, float)
        assert isinstance(intercept, float)
        # For perfect linear data, slope should be 5 and intercept should be 5
        assert abs(slope - 5.0) < 0.001
        assert abs(intercept - 5.0) < 0.001

    def test_align_time_series(self, analytics_engine):
        """Test aligning multiple time series."""
        series_map = {
            "projects": analytics_engine.project_series,
            "users": analytics_engine.user_series
        }

        time_range = {
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-31T23:59:59Z"
        }

        result = analytics_engine._align_time_series(series_map, time_range)

        assert isinstance(result, list)
        if result:
            row = result[0]
            assert "timestamp" in row
            assert "projects" in row
            assert "users" in row

    def test_calculate_correlation(self, analytics_engine):
        """Test correlation calculation."""
        # Perfect positive correlation
        x_values = [1, 2, 3, 4, 5]
        y_values = [2, 4, 6, 8, 10]

        result = analytics_engine._calculate_correlation(x_values, y_values)

        assert isinstance(result, float)
        assert abs(result - 1.0) < 0.001  # Should be very close to 1.0

        # Perfect negative correlation
        y_values_negative = [10, 8, 6, 4, 2]
        result_negative = analytics_engine._calculate_correlation(x_values, y_values_negative)
        assert abs(result_negative - (-1.0)) < 0.001  # Should be very close to -1.0

        # No correlation (random data)
        import random
        random.seed(42)
        x_random = [random.random() for _ in range(10)]
        y_random = [random.random() for _ in range(10)]
        result_random = analytics_engine._calculate_correlation(x_random, y_random)
        assert -1 <= result_random <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
