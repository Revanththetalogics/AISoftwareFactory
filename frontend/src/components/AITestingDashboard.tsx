'use client';

import { useState, useEffect } from 'react';
import { 
  aiTestingService,
  TestCase,
  TestSuite,
  AITestGenerationRequest,
  AITestAnalysis
} from '@/services/ai-testing.service';

export default function AITestingDashboard() {
  const [testSuites, setTestSuites] = useState<TestSuite[]>([]);
  const [selectedSuite, setSelectedSuite] = useState<TestSuite | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [codeInput, setCodeInput] = useState('');
  const [analysis, setAnalysis] = useState<AITestAnalysis | null>(null);
  const [generatedTests, setGeneratedTests] = useState<TestCase[]>([]);
  const [activeTab, setActiveTab] = useState<'suites' | 'generator' | 'analysis'>('suites');

  useEffect(() => {
    loadTestSuites();
  }, []);

  const loadTestSuites = () => {
    const suites = aiTestingService.getAllTestSuites();
    setTestSuites(suites);
  };

  const generateTests = async () => {
    if (!codeInput.trim()) return;

    setIsGenerating(true);
    try {
      const request: AITestGenerationRequest = {
        codeSnippet: codeInput,
        testTypes: ['unit', 'integration', 'security'],
        framework: 'jest',
        coverageTarget: 90,
        includeEdgeCases: true,
        includeErrorCases: true
      };

      const tests = await aiTestingService.generateTestCases(request);
      setGeneratedTests(tests);
      
      // Also analyze the code
      const codeAnalysis = await aiTestingService.analyzeCode(codeInput);
      setAnalysis(codeAnalysis);
      
    } catch (error) {
      console.error('Failed to generate tests:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const createTestSuite = () => {
    if (generatedTests.length === 0) return;

    const suite = aiTestingService.createTestSuite(
      `AI Generated Tests - ${new Date().toLocaleDateString()}`,
      'Automatically generated test suite',
      generatedTests
    );
    
    setTestSuites([...testSuites, suite]);
    setGeneratedTests([]);
    setCodeInput('');
    setActiveTab('suites');
  };

  const executeTestSuite = async (suiteId: string) => {
    setIsExecuting(true);
    try {
      const updatedSuite = await aiTestingService.executeTestSuite(suiteId);
      setTestSuites(prev => prev.map(s => s.id === suiteId ? updatedSuite : s));
      setSelectedSuite(updatedSuite);
    } catch (error) {
      console.error('Failed to execute test suite:', error);
    } finally {
      setIsExecuting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'running': return 'bg-blue-100 text-blue-800';
      case 'pending': return 'bg-gray-100 text-gray-800';
      case 'skipped': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Testing Automation</h1>
            <p className="text-gray-600 mt-1">
              Intelligent test generation, execution, and analysis powered by AI
            </p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('suites')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'suites'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Test Suites
            </button>
            <button
              onClick={() => setActiveTab('generator')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'generator'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Test Generator
            </button>
            <button
              onClick={() => setActiveTab('analysis')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'analysis'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Code Analysis
            </button>
          </div>
        </div>
      </div>

      {/* Test Suites Tab */}
      {activeTab === 'suites' && (
        <div className="space-y-6">
          {/* Test Suites List */}
          <div className="bg-white rounded-xl shadow-sm border">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Test Suites</h2>
              <p className="text-gray-600 mt-1">Manage and execute your test suites</p>
            </div>
            
            <div className="p-6">
              {testSuites.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No test suites yet</h3>
                  <p className="text-gray-500 mb-6">Generate tests using the Test Generator tab</p>
                  <button
                    onClick={() => setActiveTab('generator')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Generate Tests
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {testSuites.map((suite) => (
                    <div key={suite.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="font-medium text-gray-900">{suite.name}</h3>
                            <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(suite.status)}`}>
                              {suite.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mb-3">{suite.description}</p>
                          
                          <div className="flex items-center space-x-6 text-sm text-gray-500">
                            <span>{suite.totalTests} tests</span>
                            <span className="text-green-600">{suite.passedTests} passed</span>
                            <span className="text-red-600">{suite.failedTests} failed</span>
                            <span className="text-yellow-600">{suite.skippedTests} skipped</span>
                            {suite.duration && (
                              <span>{(suite.duration / 1000).toFixed(2)}s duration</span>
                            )}
                          </div>
                          
                          {suite.progress > 0 && suite.progress < 100 && (
                            <div className="mt-3">
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                  style={{ width: `${suite.progress}%` }}
                                ></div>
                              </div>
                              <div className="flex justify-between text-xs text-gray-500 mt-1">
                                <span>Progress: {suite.progress}%</span>
                                <span>
                                  {suite.passedTests + suite.failedTests + suite.skippedTests} / {suite.totalTests} executed
                                </span>
                              </div>
                            </div>
                          )}
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => setSelectedSuite(suite)}
                            className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg"
                          >
                            View Details
                          </button>
                          <button
                            onClick={() => executeTestSuite(suite.id)}
                            disabled={isExecuting || suite.status === 'running'}
                            className="px-3 py-1 text-sm bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 rounded-lg flex items-center"
                          >
                            {isExecuting ? (
                              <>
                                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>
                                Executing...
                              </>
                            ) : (
                              'Execute'
                            )}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Test Suite Details Modal */}
          {selectedSuite && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-semibold text-gray-900">
                      {selectedSuite.name} - Test Cases
                    </h3>
                    <button
                      onClick={() => setSelectedSuite(null)}
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
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-2">Suite Summary</h4>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Status:</span>
                          <span className={`font-medium ${getStatusColor(selectedSuite.status).includes('green') ? 'text-green-600' : 'text-red-600'}`}>
                            {selectedSuite.status}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Progress:</span>
                          <span>{selectedSuite.progress}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Duration:</span>
                          <span>{selectedSuite.duration ? `${(selectedSuite.duration / 1000).toFixed(2)}s` : 'N/A'}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-2">Test Statistics</h4>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Total Tests:</span>
                          <span className="font-medium">{selectedSuite.totalTests}</span>
                        </div>
                        <div className="flex justify-between text-green-600">
                          <span>Passed:</span>
                          <span className="font-medium">{selectedSuite.passedTests}</span>
                        </div>
                        <div className="flex justify-between text-red-600">
                          <span>Failed:</span>
                          <span className="font-medium">{selectedSuite.failedTests}</span>
                        </div>
                        <div className="flex justify-between text-yellow-600">
                          <span>Skipped:</span>
                          <span className="font-medium">{selectedSuite.skippedTests}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-900 mb-4">Test Cases</h4>
                    <div className="space-y-3">
                      {selectedSuite.testCases.map((testCase) => (
                        <div key={testCase.id} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                <h5 className="font-medium text-gray-900">{testCase.name}</h5>
                                <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(testCase.status)}`}>
                                  {testCase.status}
                                </span>
                                <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(testCase.priority)}`}>
                                  {testCase.priority}
                                </span>
                                {testCase.aiGenerated && (
                                  <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">
                                    AI Generated
                                  </span>
                                )}
                              </div>
                              <p className="text-sm text-gray-600 mb-2">{testCase.description}</p>
                              <div className="flex items-center space-x-4 text-xs text-gray-500">
                                <span>Type: {testCase.type}</span>
                                <span>Confidence: {testCase.confidence}%</span>
                                {testCase.executionTime && (
                                  <span>Time: {testCase.executionTime}ms</span>
                                )}
                                {testCase.lastRun && (
                                  <span>Last run: {new Date(testCase.lastRun).toLocaleTimeString()}</span>
                                )}
                              </div>
                              {testCase.failureReason && (
                                <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                                  Failure: {testCase.failureReason}
                                </div>
                              )}
                            </div>
                            
                            <div className="flex items-center space-x-2">
                              {testCase.flaky && (
                                <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-full">
                                  Flaky
                                </span>
                              )}
                              <button className="text-xs text-blue-600 hover:text-blue-800">
                                View Code
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Test Generator Tab */}
      {activeTab === 'generator' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">AI Test Generator</h2>
              <p className="text-gray-600 mt-1">Generate comprehensive test cases from your code</p>
            </div>
            
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Code to Test
                  </label>
                  <textarea
                    value={codeInput}
                    onChange={(e) => setCodeInput(e.target.value)}
                    rows={8}
                    placeholder="Paste your code here to generate tests..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                  />
                </div>
                
                <div className="flex justify-end">
                  <button
                    onClick={generateTests}
                    disabled={isGenerating || !codeInput.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
                  >
                    {isGenerating ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Generating Tests...
                      </>
                    ) : (
                      'Generate Tests'
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Generated Tests Preview */}
          {generatedTests.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Generated Tests ({generatedTests.length})
                  </h2>
                  <button
                    onClick={createTestSuite}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    Create Test Suite
                  </button>
                </div>
              </div>
              
              <div className="p-6">
                <div className="space-y-4">
                  {generatedTests.map((test, index) => (
                    <div key={test.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">{test.name}</h3>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(test.priority)}`}>
                            {test.priority}
                          </span>
                          <span className="text-xs text-gray-500">Confidence: {test.confidence}%</span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{test.description}</p>
                      <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto">
                        <code>{test.code}</code>
                      </pre>
                      <div className="flex items-center space-x-2 mt-3 text-xs text-gray-500">
                        <span className="px-2 py-1 bg-gray-100 rounded">Type: {test.type}</span>
                        <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded">
                          {test.aiGenerated ? 'AI Generated' : 'Manual'}
                        </span>
                        {test.tags.map(tag => (
                          <span key={tag} className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Code Analysis Tab */}
      {activeTab === 'analysis' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Code Quality Analysis</h2>
              <p className="text-gray-600 mt-1">AI-powered analysis of your code quality and test coverage</p>
            </div>
            
            <div className="p-6">
              {analysis ? (
                <div className="space-y-6">
                  {/* Quality Scores */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-blue-50 p-6 rounded-lg">
                      <h3 className="font-medium text-blue-900 mb-4">Code Quality</h3>
                      <div className="flex items-center justify-between">
                        <div className="text-3xl font-bold text-blue-600">{analysis.codeQuality}%</div>
                        <div className="w-24 bg-blue-200 rounded-full h-3">
                          <div 
                            className="bg-blue-600 h-3 rounded-full" 
                            style={{ width: `${analysis.codeQuality}%` }}
                          ></div>
                        </div>
                      </div>
                      <p className="text-sm text-blue-700 mt-2">
                        Overall code quality score based on maintainability, readability, and best practices
                      </p>
                    </div>
                    
                    <div className="bg-green-50 p-6 rounded-lg">
                      <h3 className="font-medium text-green-900 mb-4">Test Coverage</h3>
                      <div className="flex items-center justify-between">
                        <div className="text-3xl font-bold text-green-600">{analysis.testCoverage}%</div>
                        <div className="w-24 bg-green-200 rounded-full h-3">
                          <div 
                            className="bg-green-600 h-3 rounded-full" 
                            style={{ width: `${analysis.testCoverage}%` }}
                          ></div>
                        </div>
                      </div>
                      <p className="text-sm text-green-700 mt-2">
                        Percentage of code covered by existing tests
                      </p>
                    </div>
                  </div>

                  {/* Risk Assessment */}
                  <div className="bg-white border border-gray-200 rounded-lg">
                    <div className="p-6 border-b border-gray-200">
                      <h3 className="text-lg font-medium text-gray-900">Risk Assessment</h3>
                    </div>
                    <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <h4 className="font-medium text-red-600 mb-2">High Risk Areas</h4>
                        <ul className="space-y-1 text-sm text-gray-600">
                          {analysis.riskAssessment.highRiskAreas.map((area, index) => (
                            <li key={index} className="flex items-center">
                              <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                              {area}
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="font-medium text-yellow-600 mb-2">Medium Risk Areas</h4>
                        <ul className="space-y-1 text-sm text-gray-600">
                          {analysis.riskAssessment.mediumRiskAreas.map((area, index) => (
                            <li key={index} className="flex items-center">
                              <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
                              {area}
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="font-medium text-green-600 mb-2">Low Risk Areas</h4>
                        <ul className="space-y-1 text-sm text-gray-600">
                          {analysis.riskAssessment.lowRiskAreas.map((area, index) => (
                            <li key={index} className="flex items-center">
                              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                              {area}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="bg-white border border-gray-200 rounded-lg">
                    <div className="p-6 border-b border-gray-200">
                      <h3 className="text-lg font-medium text-gray-900">Recommendations</h3>
                    </div>
                    <div className="p-6">
                      <ul className="space-y-3">
                        {analysis.recommendations.map((rec, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-green-500 mr-2 mt-0.5">✓</span>
                            <span className="text-gray-700">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Missing Test Cases */}
                  {analysis.missingTestCases.length > 0 && (
                    <div className="bg-white border border-gray-200 rounded-lg">
                      <div className="p-6 border-b border-gray-200">
                        <h3 className="text-lg font-medium text-gray-900">Missing Test Cases</h3>
                      </div>
                      <div className="p-6">
                        <div className="space-y-3">
                          {analysis.missingTestCases.map((test, index) => (
                            <div key={index} className="border border-gray-200 rounded-lg p-4">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="font-medium text-gray-900">{test.name}</h4>
                                <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(test.priority)}`}>
                                  {test.priority}
                                </span>
                              </div>
                              <p className="text-sm text-gray-600">{test.description}</p>
                              <pre className="bg-gray-50 p-3 rounded text-xs mt-2 overflow-x-auto">
                                <code>{test.code}</code>
                              </pre>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No analysis available</h3>
                  <p className="text-gray-500 mb-6">Generate tests in the Test Generator tab to see code analysis</p>
                  <button
                    onClick={() => setActiveTab('generator')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Generate Tests
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}