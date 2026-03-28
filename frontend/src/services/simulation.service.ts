/**
 * Simulation Service
 * 
 * Provides client-side operations for simulation management including
 * running simulations and retrieving results.
 */

import { API_BASE_URL } from '@/lib/config';
import { errorHandler } from './error-handler.service';

interface SimulationRunRequest {
  code: string;
  language?: string;
  requirements?: string[];
  run_security_scan?: boolean;
  run_performance_test?: boolean;
  run_integration_test?: boolean;
  generate_reports?: boolean;
  output_formats?: string[];
}

interface SimulationResult {
  simulation_id: string;
  start_time: string;
  end_time: string;
  status: string;
  config: Record<string, any>;
  tests: Record<string, any>;
  validation: Record<string, any>;
  reports: Array<{ format: string; path: string }>;
  summary: Record<string, any>;
}

interface SimulationStats {
  total_simulations: number;
  successful_simulations: number;
  failed_simulations: number;
  average_duration: number;
  supported_languages: string[];
  last_run: string | null;
}

interface APIResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp: string;
}

class SimulationService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_BASE_URL}/simulations`;
  }

  /**
   * Run a new simulation
   */
  async runSimulation(request: SimulationRunRequest): Promise<SimulationResult> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/run`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            code: request.code,
            language: request.language || 'python',
            requirements: request.requirements || [],
            run_security_scan: request.run_security_scan !== false,
            run_performance_test: request.run_performance_test !== false,
            run_integration_test: request.run_integration_test !== false,
            generate_reports: request.generate_reports !== false,
            output_formats: request.output_formats || ['json', 'markdown']
          }),
        });
        
        const result: APIResponse<SimulationResult> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to run simulation');
        }
        
        return result.data!;
      },
      'SimulationService',
      'runSimulation',
      {
        showToast: true,
        retryAttempts: 1,
        retryDelay: 3000,
        fallbackData: {
          simulation_id: 'failed_simulation',
          start_time: new Date().toISOString(),
          end_time: new Date().toISOString(),
          status: 'failed',
          config: {},
          tests: {},
          validation: {},
          reports: [],
          summary: {}
        }
      }
    );
  }

  /**
   * Get simulation by ID
   */
  async getSimulation(simulationId: string): Promise<SimulationResult> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/${simulationId}`);
        const result: APIResponse<SimulationResult> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to get simulation');
        }
        
        return result.data!;
      },
      'SimulationService',
      'getSimulation',
      {
        showToast: true,
        retryAttempts: 2,
        retryDelay: 1500,
        fallbackData: {
          simulation_id: simulationId,
          start_time: new Date().toISOString(),
          end_time: new Date().toISOString(),
          status: 'not_found',
          config: {},
          tests: {},
          validation: {},
          reports: [],
          summary: {}
        }
      }
    );
  }

  /**
   * List simulations with pagination
   */
  async listSimulations(skip: number = 0, limit: number = 50): Promise<{
    simulations: SimulationResult[];
    total_count: number;
    skip: number;
    limit: number;
  }> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const params = new URLSearchParams({
          skip: skip.toString(),
          limit: limit.toString(),
        });
        
        const response = await fetch(`${this.baseUrl}?${params}`);
        const result: APIResponse<any> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to list simulations');
        }
        
        return result.data!;
      },
      'SimulationService',
      'listSimulations',
      {
        showToast: false,
        retryAttempts: 2,
        retryDelay: 1500,
        fallbackData: {
          simulations: [],
          total_count: 0,
          skip: skip,
          limit: limit
        }
      }
    );
  }

  /**
   * Get simulation statistics
   */
  async getStats(): Promise<SimulationStats> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/stats`);
        const result: APIResponse<SimulationStats> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to get simulation stats');
        }
        
        return result.data!;
      },
      'SimulationService',
      'getStats',
      {
        showToast: false,
        retryAttempts: 2,
        retryDelay: 1500,
        fallbackData: {
          total_simulations: 0,
          successful_simulations: 0,
          failed_simulations: 0,
          average_duration: 0,
          supported_languages: ['python'],
          last_run: null
        }
      }
    );
  }

  /**
   * Cancel a running simulation
   */
  async cancelSimulation(simulationId: string): Promise<void> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/${simulationId}/cancel`, {
          method: 'POST',
        });
        
        const result: APIResponse<any> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to cancel simulation');
        }
      },
      'SimulationService',
      'cancelSimulation',
      {
        showToast: true,
        retryAttempts: 1,
        retryDelay: 2000,
        fallbackData: undefined
      }
    );
  }

  /**
   * Delete a simulation
   */
  async deleteSimulation(simulationId: string): Promise<void> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/${simulationId}`, {
          method: 'DELETE',
        });
        
        const result: APIResponse<any> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to delete simulation');
        }
      },
      'SimulationService',
      'deleteSimulation',
      {
        showToast: true,
        retryAttempts: 1,
        retryDelay: 1500,
        fallbackData: undefined
      }
    );
  }
}

// Export singleton instance
export const simulationService = new SimulationService();

// Export types for convenience
export type {
  SimulationRunRequest,
  SimulationResult,
  SimulationStats,
};
