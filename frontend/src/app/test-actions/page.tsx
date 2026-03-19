'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { testServerAction } from '@/actions/test';

export default function TestActionsPage() {
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleTest = async () => {
    setLoading(true);
    try {
      const response = await testServerAction();
      setResult(response.message);
    } catch (error) {
      setResult(`Error: ${(error as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-6">Server Actions Test</h1>
        
        <div className="space-y-4">
          <Button 
            onClick={handleTest} 
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {loading ? 'Testing...' : 'Test Server Action'}
          </Button>
          
          {result && (
            <div className={`p-4 rounded-lg ${
              result.includes('Error') 
                ? 'bg-red-900/50 border border-red-700' 
                : 'bg-green-900/50 border border-green-700'
            }`}>
              <p className="text-white">{result}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}