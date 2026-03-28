'use client';

import { useState, useEffect } from 'react';
import { 
  securityScanningService, 
  SecurityScanResult, 
  Vulnerability, 
  VulnerabilitySeverity,
  DependencyVulnerability
} from '@/services/security-scanning.service';

export default function SecurityDashboard() {
  const [scanResults, setScanResults] = useState<SecurityScanResult | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [activeTab, setActiveTab] = useState<'overview' | 'vulnerabilities' | 'dependencies'>('overview');
  const [selectedVulnerability, setSelectedVulnerability] = useState<Vulnerability | null>(null);

  const loadSecurityStats = async () => {
    try {
      // This would load current security statistics
      console.log('Loading security statistics...');
    } catch (error) {
      console.error('Failed to load security stats:', error);
    }
  };

  useEffect(() => {
    // Load initial security stats
    loadSecurityStats();
  }, [loadSecurityStats]);

  const startSecurityScan = async () => {
    setIsScanning(true);
    setScanProgress(0);
    setScanResults(null);

    try {
      // Simulate scan progress
      const progressInterval = setInterval(() => {
        setScanProgress(prev => {
          const newProgress = prev + 10;
          if (newProgress >= 100) {
            clearInterval(progressInterval);
            return 100;
          }
          return newProgress;
        });
      }, 300);

      // Start the actual scan
      const { scan_id } = await securityScanningService.startScan('/project/src', 'full');
      
      // Get results (would typically poll for completion)
      setTimeout(async () => {
        const results = await securityScanningService.getScanResults(scan_id);
        setScanResults(results);
        setIsScanning(false);
        setScanProgress(0);
      }, 3500);

    } catch (error) {
      console.error('Security scan failed:', error);
      setIsScanning(false);
      setScanProgress(0);
    }
  };

  const getSeverityColor = (severity: VulnerabilitySeverity) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'info': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSeverityIcon = (severity: VulnerabilitySeverity) => {
    switch (severity) {
      case 'critical': return '🔴';
      case 'high': return '🟠';
      case 'medium': return '🟡';
      case 'low': return '🔵';
      case 'info': return '⚪';
      default: return '⚪';
    }
  };

  const acknowledgeVulnerability = async (vulnId: string) => {
    try {
      await securityScanningService.acknowledgeVulnerability(vulnId, 'Acknowledged by security team');
      if (scanResults) {
        setScanResults({
          ...scanResults,
          vulnerabilities: scanResults.vulnerabilities.map(vuln => 
            vuln.id === vulnId ? { ...vuln, status: 'acknowledged' } : vuln
          )
        });
      }
    } catch (error) {
      console.error('Failed to acknowledge vulnerability:', error);
    }
  };

  if (isScanning) {
    return (
      <div className="space-y-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Security Scan in Progress</h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Scanning project files...</span>
              <span className="text-sm font-medium text-blue-600">{scanProgress}%</span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${scanProgress}%` }}
              ></div>
            </div>
            
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
              <span>Analyzing code for vulnerabilities...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Scan Controls */}
      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Security Scanning</h2>
            <p className="text-gray-600 mt-1">Continuous security monitoring and vulnerability assessment</p>
          </div>
          <button
            onClick={startSecurityScan}
            disabled={isScanning}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Run Security Scan
          </button>
        </div>
      </div>

      {/* Results Overview */}
      {scanResults && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <div className="flex items-center">
                <div className="p-2 bg-red-100 rounded-lg">
                  <span className="text-2xl">🔴</span>
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-gray-900">{scanResults.summary.critical}</p>
                  <p className="text-sm text-gray-600">Critical</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <div className="flex items-center">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <span className="text-2xl">🟠</span>
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-gray-900">{scanResults.summary.high}</p>
                  <p className="text-sm text-gray-600">High</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <div className="flex items-center">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <span className="text-2xl">🟡</span>
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-gray-900">{scanResults.summary.medium}</p>
                  <p className="text-sm text-gray-600">Medium</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <span className="text-2xl">🔵</span>
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-gray-900">{scanResults.summary.low}</p>
                  <p className="text-sm text-gray-600">Low</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <div className="flex items-center">
                <div className="p-2 bg-gray-100 rounded-lg">
                  <span className="text-2xl">⚪</span>
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-gray-900">{scanResults.summary.info}</p>
                  <p className="text-sm text-gray-600">Info</p>
                </div>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="bg-white rounded-xl shadow-sm border">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`py-4 px-6 border-b-2 font-medium text-sm ${
                    activeTab === 'overview'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Overview
                </button>
                <button
                  onClick={() => setActiveTab('vulnerabilities')}
                  className={`py-4 px-6 border-b-2 font-medium text-sm ${
                    activeTab === 'vulnerabilities'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Vulnerabilities ({scanResults.summary.total_vulnerabilities})
                </button>
                <button
                  onClick={() => setActiveTab('dependencies')}
                  className={`py-4 px-6 border-b-2 font-medium text-sm ${
                    activeTab === 'dependencies'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Dependencies
                </button>
              </nav>
            </div>

            <div className="p-6">
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Scan Summary</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-600">Scan ID</p>
                        <p className="font-mono text-sm">{scanResults.scan_id}</p>
                      </div>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-600">Target</p>
                        <p className="font-mono text-sm">{scanResults.target}</p>
                      </div>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-600">Started</p>
                        <p className="text-sm">{new Date(scanResults.started_at).toLocaleString()}</p>
                      </div>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-600">Completed</p>
                        <p className="text-sm">{new Date(scanResults.completed_at).toLocaleString()}</p>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Recommendations</h3>
                    <ul className="space-y-2">
                      {scanResults.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-green-500 mr-2">✓</span>
                          <span className="text-gray-700">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {activeTab === 'vulnerabilities' && (
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-gray-900">Detected Vulnerabilities</h3>
                  
                  <div className="space-y-3">
                    {scanResults.vulnerabilities.map((vuln) => (
                      <div 
                        key={vuln.id} 
                        className={`p-4 rounded-lg border cursor-pointer hover:shadow-md transition-shadow ${
                          getSeverityColor(vuln.severity)
                        }`}
                        onClick={() => setSelectedVulnerability(vuln)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <span>{getSeverityIcon(vuln.severity)}</span>
                              <span className="font-medium capitalize">{vuln.severity}</span>
                              <span className="text-sm bg-white px-2 py-1 rounded">
                                {vuln.category}
                              </span>
                            </div>
                            <h4 className="font-semibold text-gray-900">{vuln.title}</h4>
                            <p className="text-sm text-gray-700 mt-1">{vuln.description}</p>
                            
                            {vuln.file_path && (
                              <div className="mt-2 text-xs text-gray-600">
                                <span className="font-mono">{vuln.file_path}:{vuln.line_number}</span>
                              </div>
                            )}
                            
                            {vuln.cvss_score && (
                              <div className="mt-2 flex items-center space-x-2">
                                <span className="text-xs font-medium">CVSS: {vuln.cvss_score}</span>
                                {vuln.cve_id && (
                                  <span className="text-xs bg-white px-2 py-1 rounded font-mono">
                                    {vuln.cve_id}
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              vuln.status === 'open' ? 'bg-red-100 text-red-800' :
                              vuln.status === 'acknowledged' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {vuln.status}
                            </span>
                            
                            {vuln.status === 'open' && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  acknowledgeVulnerability(vuln.id);
                                }}
                                className="text-xs text-blue-600 hover:text-blue-800"
                              >
                                Acknowledge
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'dependencies' && (
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-gray-900">Dependency Analysis</h3>
                  <div className="text-center py-8 text-gray-500">
                    <svg className="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                    <p>Dependency scanning functionality coming soon</p>
                    <p className="text-sm mt-2">Integration with vulnerability databases and dependency analysis</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* Vulnerability Detail Modal */}
      {selectedVulnerability && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold text-gray-900">
                  {selectedVulnerability.title}
                </h3>
                <button
                  onClick={() => setSelectedVulnerability(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Details</h4>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-600">Severity:</span>
                      <span className="ml-2 capitalize font-medium">{selectedVulnerability.severity}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Category:</span>
                      <span className="ml-2 capitalize">{selectedVulnerability.category}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Status:</span>
                      <span className="ml-2 capitalize">{selectedVulnerability.status}</span>
                    </div>
                    {selectedVulnerability.cvss_score && (
                      <div>
                        <span className="text-gray-600">CVSS Score:</span>
                        <span className="ml-2 font-medium">{selectedVulnerability.cvss_score}</span>
                      </div>
                    )}
                    {selectedVulnerability.cve_id && (
                      <div>
                        <span className="text-gray-600">CVE ID:</span>
                        <span className="ml-2 font-mono">{selectedVulnerability.cve_id}</span>
                      </div>
                    )}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Location</h4>
                  <div className="text-sm">
                    {selectedVulnerability.file_path ? (
                      <>
                        <div className="font-mono bg-gray-100 p-2 rounded">
                          {selectedVulnerability.file_path}
                        </div>
                        {selectedVulnerability.line_number && (
                          <div className="mt-1 text-gray-600">
                            Line {selectedVulnerability.line_number}
                          </div>
                        )}
                      </>
                    ) : (
                      <span className="text-gray-500">Not specified</span>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Description</h4>
                <p className="text-gray-700">{selectedVulnerability.description}</p>
              </div>
              
              {selectedVulnerability.code_snippet && (
                <div className="mb-6">
                  <h4 className="font-medium text-gray-900 mb-2">Affected Code</h4>
                  <pre className="bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
                    <code>{selectedVulnerability.code_snippet}</code>
                  </pre>
                </div>
              )}
              
              {selectedVulnerability.remediation && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Remediation</h4>
                  <p className="text-gray-700">{selectedVulnerability.remediation}</p>
                </div>
              )}
            </div>
            
            <div className="p-6 border-t border-gray-200 bg-gray-50 flex justify-end space-x-3">
              <button
                onClick={() => setSelectedVulnerability(null)}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Close
              </button>
              <button
                onClick={() => {
                  acknowledgeVulnerability(selectedVulnerability.id);
                  setSelectedVulnerability(null);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Acknowledge
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}