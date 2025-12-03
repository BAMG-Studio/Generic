import { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { auditsApi, usageApi, tokensApi, Audit, UsageStats, ApiToken } from '../api/audits';



type Tab = 'overview' | 'audits' | 'tokens' | 'submit';

export default function ClientPortal() {
  const { logout } = useAuthStore();
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [usage, setUsage] = useState<UsageStats | null>(null);
  const [audits, setAudits] = useState<Audit[]>([]);
  const [tokens, setTokens] = useState<ApiToken[]>([]);
  const [loading, setLoading] = useState(true);
  const [showTokenModal, setShowTokenModal] = useState(false);
  const [newTokenName, setNewTokenName] = useState('');
  const [createdToken, setCreatedToken] = useState<string | null>(null);
  const [repoUrl, setRepoUrl] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [usageData, auditsData, tokensData] = await Promise.all([
        usageApi.getStats(),
        auditsApi.list(),
        tokensApi.list()
      ]);
      setUsage(usageData);
      setAudits(auditsData.audits);
      setTokens(tokensData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createToken = async () => {
    if (!newTokenName.trim()) return;
    try {
      const newToken = await tokensApi.create(newTokenName);
      setCreatedToken(newToken.token);
      setTokens([...tokens, { ...newToken, token: 'ft_***************' }]);
      setNewTokenName('');
    } catch (error) {
      console.error('Failed to create token:', error);
      alert('Failed to create token');
    }
  };

  const deleteToken = async (id: string) => {
    if (confirm('Are you sure you want to delete this token?')) {
      try {
        await tokensApi.revoke(id);
        setTokens(tokens.filter(t => t.id !== id));
      } catch (error) {
        console.error('Failed to delete token:', error);
        alert('Failed to delete token');
      }
    }
  };

  const submitAudit = async () => {
    if (!repoUrl.trim()) return;
    setSubmitting(true);
    try {
      const newAudit = await auditsApi.submit(repoUrl);
      setAudits([newAudit, ...audits]);
      setRepoUrl('');
      setActiveTab('audits');
    } catch (error) {
      console.error('Failed to submit audit:', error);
      alert('Failed to submit audit');
    } finally {
      setSubmitting(false);
    }
  };

  const downloadReport = async (auditId: string, format: 'json' | 'pdf') => {
    try {
      const blob = await auditsApi.downloadReport(auditId, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-${auditId}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download report:', error);
      alert('Failed to download report');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  const usagePercentage = usage ? (usage.filesScanned / usage.monthlyLimit) * 100 : 0;
  const maxUsage = Math.max(...(usage?.usageHistory.map(h => h.count) || [1]));

  return (
    <div className="min-h-screen bg-slate-900">
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-white">ForgeTrace</h1>
              <span className="px-3 py-1 bg-blue-500/20 text-blue-400 text-sm font-medium rounded-full">Client Portal</span>
            </div>
            <button onClick={logout} className="text-slate-400 hover:text-white transition-colors">Sign Out</button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex space-x-1 mb-8 bg-slate-800 p-1 rounded-lg border border-slate-700">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'audits', label: 'Audits' },
            { id: 'tokens', label: 'API Tokens' },
            { id: 'submit', label: 'Submit Audit' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as Tab)}
              className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab.id ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === 'overview' && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-slate-400 text-sm font-medium">Files Scanned</h3>
                  <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <p className="text-3xl font-bold text-white">{usage?.filesScanned.toLocaleString()}</p>
                <p className="text-sm text-slate-400 mt-1">of {usage?.monthlyLimit.toLocaleString()} this month</p>
                <div className="mt-4 bg-slate-700 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full transition-all" style={{ width: `${Math.min(usagePercentage, 100)}%` }} />
                </div>
              </div>

              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-slate-400 text-sm font-medium">API Requests</h3>
                  <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <p className="text-3xl font-bold text-white">{usage?.apiRequests.toLocaleString()}</p>
                <p className="text-sm text-slate-400 mt-1">this month</p>
              </div>

              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-slate-400 text-sm font-medium">Subscription</h3>
                  <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                </div>
                <p className="text-3xl font-bold text-white capitalize">{usage?.tier}</p>
                <p className="text-sm text-slate-400 mt-1">Active plan</p>
              </div>
            </div>

            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mb-8">
              <h3 className="text-lg font-semibold text-white mb-4">Usage Trend</h3>
              <div className="flex items-end space-x-2 h-32">
                {usage?.usageHistory.map((item, i) => (
                  <div key={i} className="flex-1 flex flex-col items-center">
                    <div className="w-full bg-slate-700 rounded-t relative" style={{ height: `${(item.count / maxUsage) * 100}%`, minHeight: '4px' }}>
                      <div className="absolute inset-0 bg-blue-500 rounded-t"></div>
                    </div>
                    <span className="text-xs text-slate-400 mt-2">{item.date.split('-')[1]}</span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {activeTab === 'audits' && (
          <div className="bg-slate-800 rounded-lg border border-slate-700">
            <div className="px-6 py-4 border-b border-slate-700">
              <h2 className="text-xl font-bold text-white">Audit History</h2>
            </div>
            <div className="divide-y divide-slate-700">
              {audits.map((audit) => (
                <div key={audit.id} className="px-6 py-4 hover:bg-slate-700/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-white font-medium">{audit.repository}</h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          audit.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                          audit.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                          audit.status === 'processing' ? 'bg-blue-500/20 text-blue-400' :
                          'bg-slate-500/20 text-slate-400'
                        }`}>
                          {audit.status}
                        </span>
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-slate-400">
                        <span>ID: {audit.id}</span>
                        <span>•</span>
                        <span>{new Date(audit.createdAt).toLocaleString()}</span>
                        {audit.filesScanned && (
                          <>
                            <span>•</span>
                            <span>{audit.filesScanned} files</span>
                          </>
                        )}
                      </div>
                    </div>
                    {audit.status === 'completed' && (
                      <div className="flex space-x-2">
                        <button
                          onClick={() => downloadReport(audit.id, 'json')}
                          className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white text-sm rounded-md transition-colors"
                        >
                          JSON
                        </button>
                        <button
                          onClick={() => downloadReport(audit.id, 'pdf')}
                          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-md transition-colors"
                        >
                          PDF
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {audits.length === 0 && (
                <div className="px-6 py-12 text-center text-slate-400">
                  No audits yet. Submit your first audit to get started.
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'tokens' && (
          <div className="bg-slate-800 rounded-lg border border-slate-700">
            <div className="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">API Tokens</h2>
              <button
                onClick={() => setShowTokenModal(true)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-md transition-colors"
              >
                Create Token
              </button>
            </div>
            <div className="divide-y divide-slate-700">
              {tokens.map((token) => (
                <div key={token.id} className="px-6 py-4 flex items-center justify-between">
                  <div>
                    <h3 className="text-white font-medium mb-1">{token.name}</h3>
                    <div className="flex items-center space-x-4 text-sm text-slate-400">
                      <span className="font-mono">{token.token}</span>
                      <span>•</span>
                      <span>Created {new Date(token.createdAt).toLocaleDateString()}</span>
                      {token.lastUsed && (
                        <>
                          <span>•</span>
                          <span>Last used {new Date(token.lastUsed).toLocaleDateString()}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => deleteToken(token.id)}
                    className="px-3 py-1.5 bg-red-600/20 hover:bg-red-600/30 text-red-400 text-sm rounded-md transition-colors"
                  >
                    Revoke
                  </button>
                </div>
              ))}
              {tokens.length === 0 && (
                <div className="px-6 py-12 text-center text-slate-400">
                  No API tokens yet. Create one to get started with the API.
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'submit' && (
          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4">Submit New Audit</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Repository URL
                </label>
                <input
                  type="text"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="https://github.com/org/repo"
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <button
                onClick={submitAudit}
                disabled={submitting || !repoUrl.trim()}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium rounded-md transition-colors"
              >
                {submitting ? 'Submitting...' : 'Submit Audit'}
              </button>
            </div>
          </div>
        )}
      </div>

      {showTokenModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-white mb-4">
              {createdToken ? 'Token Created' : 'Create API Token'}
            </h3>
            {createdToken ? (
              <>
                <p className="text-slate-300 mb-4">Copy this token now. You won't be able to see it again!</p>
                <div className="bg-slate-900 border border-slate-700 rounded-md p-3 mb-4">
                  <code className="text-green-400 text-sm break-all">{createdToken}</code>
                </div>
                <button
                  onClick={() => {
                    setShowTokenModal(false);
                    setCreatedToken(null);
                  }}
                  className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-md transition-colors"
                >
                  Done
                </button>
              </>
            ) : (
              <>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Token Name
                  </label>
                  <input
                    type="text"
                    value={newTokenName}
                    onChange={(e) => setNewTokenName(e.target.value)}
                    placeholder="My API Token"
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={() => {
                      setShowTokenModal(false);
                      setNewTokenName('');
                    }}
                    className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white font-medium rounded-md transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={createToken}
                    disabled={!newTokenName.trim()}
                    className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium rounded-md transition-colors"
                  >
                    Create
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}                 <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="text-white font-medium">{audit.repository}</h3>
                      <div className="flex items-center space-x-4 mt-1">
                        <span className="text-sm text-slate-400">{audit.filesScanned} files scanned</span>
                        <span className="text-sm text-slate-400">{new Date(audit.createdAt).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                        audit.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                        audit.status === 'processing' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'
                      }`}>
                        {audit.status}
                      </span>
                      {audit.status === 'completed' && (
                        <div className="flex space-x-2">
                          <button onClick={() => downloadReport(audit.id, 'json')} className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-white text-sm rounded transition-colors">JSON</button>
                          <button onClick={() => downloadReport(audit.id, 'pdf')} className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors">PDF</button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'tokens' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-white">API Tokens</h2>
              <button onClick={() => setShowTokenModal(true)} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">Create Token</button>
            </div>
            <div className="bg-slate-800 rounded-lg border border-slate-700 divide-y divide-slate-700">
              {tokens.map((token) => (
                <div key={token.id} className="px-6 py-4 flex items-center justify-between">
                  <div>
                    <h3 className="text-white font-medium">{token.name}</h3>
                    <p className="text-sm text-slate-400 font-mono mt-1">{token.token}</p>
                    <p className="text-xs text-slate-500 mt-1">Created: {token.createdAt} • Last used: {token.lastUsed || 'Never'}</p>
                  </div>
                  <button onClick={() => deleteToken(token.id)} className="text-red-400 hover:text-red-300 transition-colors">Delete</button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'submit' && (
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 max-w-2xl">
            <h2 className="text-xl font-bold text-white mb-4">Submit New Audit</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Repository URL</label>
                <input
                  type="text"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="https://github.com/org/repo"
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <button
                onClick={submitAudit}
                disabled={submitting || !repoUrl.trim()}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
              >
                {submitting ? 'Submitting...' : 'Submit Audit'}
              </button>
            </div>
          </div>
        )}
      </div>

      {showTokenModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 max-w-md w-full mx-4 border border-slate-700">
            {createdToken ? (
              <>
                <h3 className="text-lg font-bold text-white mb-4">Token Created</h3>
                <p className="text-sm text-slate-300 mb-4">Copy this token now. You won't be able to see it again!</p>
                <div className="bg-slate-900 p-3 rounded border border-slate-700 mb-4">
                  <code className="text-sm text-green-400 break-all">{createdToken}</code>
                </div>
                <button onClick={() => { setShowTokenModal(false); setCreatedToken(null); }} className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">Close</button>
              </>
            ) : (
              <>
                <h3 className="text-lg font-bold text-white mb-4">Create API Token</h3>
                <input
                  type="text"
                  value={newTokenName}
                  onChange={(e) => setNewTokenName(e.target.value)}
                  placeholder="Token name"
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 mb-4"
                />
                <div className="flex space-x-3">
                  <button onClick={() => setShowTokenModal(false)} className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors">Cancel</button>
                  <button onClick={createToken} disabled={!newTokenName.trim()} className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors">Create</button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
