import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { repositoryAPI, scanAPI } from '../api/client';

interface Repository {
  id: string;
  name: string;
  full_name: string;
  provider: string;
  last_scanned_at: string | null;
}

interface Scan {
  id: string;
  repository_id: string;
  status: string;
  created_at: string;
  total_files: number;
  foreground_count: number;
  third_party_count: number;
  background_count: number;
}

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [recentScans, setRecentScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    loadData();
  }, [user, navigate]);

  const loadData = async () => {
    try {
      const [reposResponse, scansResponse] = await Promise.all([
        repositoryAPI.list(),
        scanAPI.list({ limit: 10 }),
      ]);
      
      setRepositories(reposResponse.data);
      setRecentScans(scansResponse.data);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">ForgeTrace Platform</h1>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">{user?.email}</span>
            <button
              onClick={handleLogout}
              className="text-sm text-primary-600 hover:text-primary-500"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Total Repositories</h3>
            <p className="mt-2 text-3xl font-bold text-gray-900">{repositories.length}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Total Scans</h3>
            <p className="mt-2 text-3xl font-bold text-gray-900">{recentScans.length}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Account Tier</h3>
            <p className="mt-2 text-3xl font-bold text-primary-600">Free</p>
          </div>
        </div>

        {/* Repositories */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-lg font-medium text-gray-900">Repositories</h2>
            <button className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700">
              Connect Repository
            </button>
          </div>
          
          <div className="px-6 py-4">
            {repositories.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No repositories connected yet. Connect your first repository to get started.
              </p>
            ) : (
              <div className="space-y-4">
                {repositories.map((repo) => (
                  <div key={repo.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <h3 className="font-medium text-gray-900">{repo.full_name}</h3>
                    <p className="text-sm text-gray-500">{repo.provider}</p>
                    {repo.last_scanned_at && (
                      <p className="text-xs text-gray-400 mt-1">
                        Last scanned: {new Date(repo.last_scanned_at).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recent Scans */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Recent Scans</h2>
          </div>
          
          <div className="px-6 py-4">
            {recentScans.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No scans yet. Start your first scan to analyze IP provenance.
              </p>
            ) : (
              <div className="space-y-4">
                {recentScans.map((scan) => (
                  <div key={scan.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          scan.status === 'completed' ? 'bg-green-100 text-green-800' :
                          scan.status === 'running' ? 'bg-blue-100 text-blue-800' :
                          scan.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {scan.status}
                        </span>
                        <p className="text-xs text-gray-400 mt-1">
                          {new Date(scan.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="text-sm text-gray-600">
                        {scan.total_files} files analyzed
                      </div>
                    </div>
                    
                    {scan.status === 'completed' && (
                      <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Foreground:</span>
                          <span className="ml-2 font-medium">{scan.foreground_count}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Third-party:</span>
                          <span className="ml-2 font-medium">{scan.third_party_count}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Background:</span>
                          <span className="ml-2 font-medium">{scan.background_count}</span>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};
