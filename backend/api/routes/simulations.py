"""
Simulation Engine API Routes.

Provides RESTful endpoints for simulation management including
running simulations, retrieving results, and managing simulation history.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.simulation.simulation_orchestrator import SimulationConfig, SimulationOrchestrator

router = APIRouter(prefix="/simulations", tags=["Simulations"])
logger = get_logger(__name__)

# Global simulation orchestrator instance (in production, use dependency injection)
simulation_orchestrator = SimulationOrchestrator()

class SimulationRunRequest(BaseModel):
    """Request model for running a simulation."""
    code: str
    language: str = "python"
    requirements: list[str] | None = None
    run_security_scan: bool = True
    run_performance_test: bool = True
    run_integration_test: bool = True
    generate_reports: bool = True
    output_formats: list[str] | None = None

class SimulationResultResponse(BaseModel):
    """Response model for simulation results."""
    simulation_id: str
    start_time: str
    end_time: str
    status: str
    config: dict[str, Any]
    tests: dict[str, Any]
    validation: dict[str, Any]
    reports: list[dict[str, str]]
    summary: dict[str, Any]

@router.post("/run", response_model=APIResponse)
async def run_simulation(request: SimulationRunRequest):
    """
    Run a new simulation.
    
    Args:
        request: Simulation run request with code and configuration
        
    Returns:
        APIResponse with simulation results
    """
    try:
        # Create simulation configuration
        config = SimulationConfig(
            run_security_scan=request.run_security_scan,
            run_performance_test=request.run_performance_test,
            run_integration_test=request.run_integration_test,
            generate_reports=request.generate_reports,
            output_formats=request.output_formats or ["json", "markdown"]
        )

        # Run simulation
        results = await simulation_orchestrator.run_simulation(
            code=request.code,
            language=request.language,
            requirements=request.requirements,
            config=config
        )

        # Generate summary
        summary = simulation_orchestrator.get_simulation_summary(results)
        results["summary"] = summary

        logger.info(
            "Simulation completed successfully",
            simulation_id=results["simulation_id"],
            language=request.language
        )

        return APIResponse(
            success=True,
            data=results,
            message=f"Simulation {results['simulation_id']} completed successfully"
        )
    except Exception as e:
        logger.error("Simulation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.get("/{simulation_id}", response_model=APIResponse)
async def get_simulation(simulation_id: str):
    """
    Get a specific simulation by ID.
    
    Args:
        simulation_id: Simulation ID
        
    Returns:
        APIResponse with simulation data
    """
    # In a real implementation, this would fetch from a database
    # For now, we'll return a placeholder since simulations aren't persisted
    raise HTTPException(status_code=404, detail="Simulation not found - simulations are not persisted in this version")

@router.get("/", response_model=APIResponse)
async def list_simulations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    List recent simulations (placeholder - simulations are not persisted).
    
    Args:
        skip: Number of simulations to skip
        limit: Maximum number of simulations to return
        
    Returns:
        APIResponse with list of simulations
    """
    # In a real implementation, this would query a database
    # For now, return empty list since simulations aren't persisted
    return APIResponse(
        success=True,
        data={
            "simulations": [],
            "total_count": 0,
            "skip": skip,
            "limit": limit
        },
        message="No simulations found - simulations are not persisted in this version"
    )

@router.get("/stats", response_model=APIResponse)
async def get_simulation_stats():
    """
    Get simulation statistics.
    
    Returns:
        APIResponse with simulation statistics
    """
    # In a real implementation, this would aggregate from a database
    # For now, return basic placeholder stats
    stats = {
        "total_simulations": 0,
        "successful_simulations": 0,
        "failed_simulations": 0,
        "average_duration": 0,
        "supported_languages": ["python"],
        "last_run": None
    }

    return APIResponse(
        success=True,
        data=stats,
        message="Simulation statistics retrieved"
    )

@router.post("/{simulation_id}/cancel", response_model=APIResponse)
async def cancel_simulation(simulation_id: str):
    """
    Cancel a running simulation.
    
    Args:
        simulation_id: Simulation ID to cancel
        
    Returns:
        APIResponse confirming cancellation
    """
    # In a real implementation, this would cancel the running task
    # For now, return not implemented
    raise HTTPException(status_code=501, detail="Simulation cancellation not implemented in this version")

@router.delete("/{simulation_id}", response_model=APIResponse)
async def delete_simulation(simulation_id: str):
    """
    Delete a simulation and its results.
    
    Args:
        simulation_id: Simulation ID to delete
        
    Returns:
        APIResponse confirming deletion
    """
    # In a real implementation, this would delete from a database
    # For now, return not found since simulations aren't persisted
    raise HTTPException(status_code=404, detail="Simulation not found - simulations are not persisted in this version")
