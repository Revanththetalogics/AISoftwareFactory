// Security scanning service for vulnerability assessment and reporting
// Integrates with backend security scanning APIs

export type VulnerabilitySeverity = 'critical' | 'high' | 'medium' | 'low' | 'info';
export type VulnerabilityCategory = 'security' | 'performance' | 'quality' | 'compliance';

export interface Vulnerability {
  id: string;
  severity: VulnerabilitySeverity;
  category: VulnerabilityCategory;
  title: string;
  description: string;
  file_path?: string;
  line_number?: number;
  code_snippet?: string;
  remediation?: string;
  cve_id?: string;
  cvss_score?: number;
  discovered_at: string;
  status: 'open' | 'acknowledged' | 'fixed' | 'dismissed';
}

export interface SecurityScanResult {
  scan_id: string;
  target: string;
  scan_type: 'code' | 'dependencies' | 'infrastructure' | 'full';
  started_at: string;
  completed_at: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  summary: {
    total_vulnerabilities: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
  vulnerabilities: Vulnerability[];
  recommendations: string[];
}

export interface DependencyVulnerability {
  package_name: string;
  installed_version: string;
  affected_versions: string;
  fixed_version?: string;
  severity: VulnerabilitySeverity;
  cve_id: string;
  description: string;
  cvss_score: number;
  published_date: string;
}

class SecurityScanningService {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  }

  // Start a new security scan
  public async startScan(
    target: string,
    scanType: 'code' | 'dependencies' | 'infrastructure' | 'full' = 'full',
    options: {
      include_subdirectories?: boolean;
      exclude_patterns?: string[];
      min_severity?: VulnerabilitySeverity;
    } = {}
  ): Promise<{ scan_id: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/testing/detect-bugs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          directory: scanType === 'code' || scanType === 'full' ? target : undefined,
          use_static_analysis: true,
          use_llm_review: true,
          min_confidence: 0.7,
          ...options
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to start scan: ${response.statusText}`);
      }

      const data = await response.json();
      return { scan_id: data.scan_id || `scan_${Date.now()}` };
    } catch (error) {
      console.error('Failed to start security scan:', error);
      throw error;
    }
  }

  // Get scan results
  public async getScanResults(scanId: string): Promise<SecurityScanResult> {
    try {
      // In a real implementation, this would poll for results
      // For now, we'll simulate the response
      
      // Simulate processing delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      const mockResult: SecurityScanResult = {
        scan_id: scanId,
        target: '/project/src',
        scan_type: 'full',
        started_at: new Date(Date.now() - 30000).toISOString(),
        completed_at: new Date().toISOString(),
        status: 'completed',
        summary: {
          total_vulnerabilities: 12,
          critical: 2,
          high: 3,
          medium: 4,
          low: 2,
          info: 1
        },
        vulnerabilities: [
          {
            id: 'vuln_1',
            severity: 'critical',
            category: 'security',
            title: 'SQL Injection Vulnerability',
            description: 'Potential SQL injection vulnerability detected in user input handling',
            file_path: '/src/database/user_service.py',
            line_number: 45,
            code_snippet: 'cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")',
            remediation: 'Use parameterized queries instead of string concatenation',
            cve_id: 'CVE-2024-XXXX',
            cvss_score: 9.8,
            discovered_at: new Date(Date.now() - 25000).toISOString(),
            status: 'open'
          },
          {
            id: 'vuln_2',
            severity: 'high',
            category: 'security',
            title: 'Hardcoded Credentials',
            description: 'Hardcoded password found in source code',
            file_path: '/src/config/database.py',
            line_number: 12,
            code_snippet: 'DB_PASSWORD = "secret123"',
            remediation: 'Move credentials to environment variables or secure vault',
            cvss_score: 7.5,
            discovered_at: new Date(Date.now() - 24000).toISOString(),
            status: 'open'
          },
          {
            id: 'vuln_3',
            severity: 'medium',
            category: 'performance',
            title: 'N+1 Query Problem',
            description: 'Database query executed in a loop causing performance degradation',
            file_path: '/src/services/order_service.py',
            line_number: 78,
            code_snippet: 'for item in items:\n    product = Product.get(item.product_id)',
            remediation: 'Use eager loading or batch queries',
            discovered_at: new Date(Date.now() - 23000).toISOString(),
            status: 'acknowledged'
          }
        ],
        recommendations: [
          'Implement input validation for all user-provided data',
          'Enable automated security scanning in CI/CD pipeline',
          'Regularly update dependencies to patch known vulnerabilities',
          'Conduct periodic security training for development team'
        ]
      };

      return mockResult;
    } catch (error) {
      console.error('Failed to get scan results:', error);
      throw error;
    }
  }

  // Get dependency vulnerabilities
  public async scanDependencies(dependencies: string[]): Promise<DependencyVulnerability[]> {
    try {
      // In a real implementation, this would integrate with vulnerability databases
      // like Snyk, OSS Index, or GitHub Advisory Database
      
      const mockVulnerabilities: DependencyVulnerability[] = [
        {
          package_name: 'requests',
          installed_version: '2.19.0',
          affected_versions: '< 2.20.0',
          fixed_version: '2.20.0',
          severity: 'high',
          cve_id: 'CVE-2018-18074',
          description: 'requests package is vulnerable to CWE-300: Channel Accessible by Non-Endpoint',
          cvss_score: 7.5,
          published_date: '2018-10-09'
        },
        {
          package_name: 'django',
          installed_version: '2.0',
          affected_versions: '< 2.0.8',
          fixed_version: '2.0.8',
          severity: 'medium',
          cve_id: 'CVE-2018-14574',
          description: 'Django has URL redirect validation bypass',
          cvss_score: 5.4,
          published_date: '2018-08-01'
        }
      ];

      return mockVulnerabilities;
    } catch (error) {
      console.error('Failed to scan dependencies:', error);
      throw error;
    }
  }

  // Get security statistics
  public async getSecurityStats(projectId?: string): Promise<{
    total_vulnerabilities: number;
    by_severity: Record<VulnerabilitySeverity, number>;
    trend_data: Array<{ date: string; count: number }>;
    top_vulnerabilities: Vulnerability[];
  }> {
    try {
      // Mock statistics data
      return {
        total_vulnerabilities: 47,
        by_severity: {
          critical: 3,
          high: 8,
          medium: 15,
          low: 12,
          info: 9
        },
        trend_data: [
          { date: '2024-01-01', count: 25 },
          { date: '2024-01-08', count: 32 },
          { date: '2024-01-15', count: 28 },
          { date: '2024-01-22', count: 47 },
          { date: '2024-01-29', count: 41 }
        ],
        top_vulnerabilities: [
          {
            id: 'top_1',
            severity: 'critical',
            category: 'security',
            title: 'Remote Code Execution',
            description: 'Unsanitized input leads to RCE vulnerability',
            file_path: '/src/api/handlers.py',
            line_number: 123,
            cvss_score: 9.8,
            discovered_at: new Date(Date.now() - 86400000).toISOString(),
            status: 'open'
          }
        ] as Vulnerability[]
      };
    } catch (error) {
      console.error('Failed to get security stats:', error);
      throw error;
    }
  }

  // Acknowledge a vulnerability
  public async acknowledgeVulnerability(vulnId: string, notes?: string): Promise<void> {
    try {
      // In a real implementation, this would update the vulnerability status
      console.log(`Acknowledged vulnerability ${vulnId}`, { notes });
    } catch (error) {
      console.error('Failed to acknowledge vulnerability:', error);
      throw error;
    }
  }

  // Dismiss a vulnerability (false positive)
  public async dismissVulnerability(vulnId: string, reason: string): Promise<void> {
    try {
      // In a real implementation, this would update the vulnerability status
      console.log(`Dismissed vulnerability ${vulnId}`, { reason });
    } catch (error) {
      console.error('Failed to dismiss vulnerability:', error);
      throw error;
    }
  }

  // Get security policies and compliance status
  public async getComplianceStatus(): Promise<{
    policies: Array<{ name: string; status: 'compliant' | 'non_compliant'; last_checked: string }>;
    compliance_score: number;
  }> {
    try {
      return {
        policies: [
          { name: 'OWASP Top 10', status: 'compliant', last_checked: new Date().toISOString() },
          { name: 'PCI DSS', status: 'non_compliant', last_checked: new Date().toISOString() },
          { name: 'GDPR', status: 'compliant', last_checked: new Date().toISOString() }
        ],
        compliance_score: 85
      };
    } catch (error) {
      console.error('Failed to get compliance status:', error);
      throw error;
    }
  }
}

// Singleton instance
export const securityScanningService = new SecurityScanningService();