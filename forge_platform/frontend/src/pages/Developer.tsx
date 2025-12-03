import React, { useState } from 'react';
import { Key, Plus, Trash2, Copy, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Card, CardHeader, CardContent, Badge, Button } from '../components/ui';

interface Token {
  id: string;
  name: string;
  scopes: string[];
  created: string;
  lastUsed: string | null;
  expiresAt: string | null;
}

const Developer: React.FC = () => {
  const [tokens, setTokens] = useState<Token[]>([
    {
      id: '1',
      name: 'CI/CD Pipeline',
      scopes: ['read:reports', 'write:audits'],
      created: '2025-11-01T10:00:00Z',
      lastUsed: '2025-11-26T14:30:00Z',
      expiresAt: null,
    },
    {
      id: '2',
      name: 'Local Development',
      scopes: ['read:reports'],
      created: '2025-11-15T08:00:00Z',
      lastUsed: null,
      expiresAt: '2025-12-15T08:00:00Z',
    },
  ]);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTokenName, setNewTokenName] = useState('');
  const [newTokenScopes, setNewTokenScopes] = useState<string[]>([]);
  const [generatedToken, setGeneratedToken] = useState<string | null>(null);
  const [copiedToken, setCopiedToken] = useState(false);

  const availableScopes = [
    { id: 'read:reports', label: 'Read Reports', description: 'View audit reports and summaries' },
    { id: 'write:audits', label: 'Submit Audits', description: 'Create new audit requests' },
    { id: 'read:tokens', label: 'Read Tokens', description: 'List your API tokens' },
    { id: 'write:tokens', label: 'Manage Tokens', description: 'Create and revoke tokens' },
  ];

  const handleCreateToken = () => {
    // Simulate token generation
    const mockToken = `ftk_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`;
    setGeneratedToken(mockToken);
    
    const newToken: Token = {
      id: (tokens.length + 1).toString(),
      name: newTokenName,
      scopes: newTokenScopes,
      created: new Date().toISOString(),
      lastUsed: null,
      expiresAt: null,
    };
    
    setTokens([...tokens, newToken]);
  };

  const handleCopyToken = () => {
    if (generatedToken) {
      navigator.clipboard.writeText(generatedToken);
      setCopiedToken(true);
      setTimeout(() => setCopiedToken(false), 2000);
    }
  };

  const handleDeleteToken = (id: string) => {
    if (confirm('Are you sure you want to revoke this token? This action cannot be undone.')) {
      setTokens(tokens.filter(t => t.id !== id));
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const resetModal = () => {
    setShowCreateModal(false);
    setNewTokenName('');
    setNewTokenScopes([]);
    setGeneratedToken(null);
    setCopiedToken(false);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Developer Portal</h2>
        <p className="text-slate-400">
          Manage API tokens, view usage metrics, and integrate ForgeTrace into your workflows
        </p>
      </div>

      {/* API Tokens Card */}
      <Card>
        <CardHeader 
          icon={<Key size={20} />}
          title="API Tokens"
          description="Personal access tokens for API authentication"
          action={
            <Button 
              variant="primary" 
              size="sm"
              onClick={() => setShowCreateModal(true)}
            >
              <Plus size={16} className="mr-2" />
              Create Token
            </Button>
          }
        />
        <CardContent>
          {tokens.length === 0 ? (
            <div className="text-center py-12 border border-dashed border-slate-700 rounded-lg">
              <Key size={48} className="mx-auto text-slate-600 mb-4" />
              <p className="text-slate-400 mb-4">No API tokens yet</p>
              <Button variant="primary" onClick={() => setShowCreateModal(true)}>
                Create your first token
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {tokens.map((token) => (
                <div 
                  key={token.id}
                  className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg border border-slate-700 hover:border-slate-600 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="text-sm font-medium text-white">{token.name}</h4>
                      {token.expiresAt && (
                        <Badge variant="warning">
                          Expires {formatDate(token.expiresAt)}
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center space-x-4 text-xs text-slate-400">
                      <span>Created {formatDate(token.created)}</span>
                      {token.lastUsed ? (
                        <span className="flex items-center">
                          <CheckCircle2 size={12} className="mr-1 text-emerald-500" />
                          Last used {formatDate(token.lastUsed)}
                        </span>
                      ) : (
                        <span className="text-slate-500">Never used</span>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {token.scopes.map((scope) => (
                        <Badge key={scope} variant="info" className="text-xxs">
                          {scope}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteToken(token.id)}
                    className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                  >
                    <Trash2 size={16} />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Usage & Quota Card */}
      <Card>
        <CardHeader 
          title="API Usage"
          description="Current billing period usage and limits"
        />
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700">
              <div className="text-xs text-slate-400 mb-1">API Requests</div>
              <div className="text-2xl font-bold text-white mb-1">1,247</div>
              <div className="text-xs text-slate-500">of 10,000 / month</div>
              <div className="mt-2 w-full bg-slate-700 rounded-full h-1.5">
                <div className="bg-brand h-1.5 rounded-full" style={{ width: '12.47%' }}></div>
              </div>
            </div>

            <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700">
              <div className="text-xs text-slate-400 mb-1">Files Scanned</div>
              <div className="text-2xl font-bold text-white mb-1">8,432</div>
              <div className="text-xs text-slate-500">of 50,000 / month</div>
              <div className="mt-2 w-full bg-slate-700 rounded-full h-1.5">
                <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: '16.86%' }}></div>
              </div>
            </div>

            <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700">
              <div className="text-xs text-slate-400 mb-1">Storage</div>
              <div className="text-2xl font-bold text-white mb-1">4.2 GB</div>
              <div className="text-xs text-slate-500">of 100 GB</div>
              <div className="mt-2 w-full bg-slate-700 rounded-full h-1.5">
                <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: '4.2%' }}></div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Start Card */}
      <Card>
        <CardHeader 
          title="Quick Start"
          description="Get started with the ForgeTrace API"
        />
        <CardContent>
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-white mb-2">Submit an Audit</h4>
              <pre className="bg-slate-900 border border-slate-700 rounded-lg p-4 overflow-x-auto">
                <code className="text-xs text-slate-300">{`curl -X POST https://api.forgetrace.pro/v1/audits \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "repository": "https://github.com/org/repo",
    "branch": "main"
  }'`}</code>
              </pre>
            </div>

            <div>
              <h4 className="text-sm font-medium text-white mb-2">Get Audit Status</h4>
              <pre className="bg-slate-900 border border-slate-700 rounded-lg p-4 overflow-x-auto">
                <code className="text-xs text-slate-300">{`curl https://api.forgetrace.pro/v1/audits/{audit_id} \\
  -H "Authorization: Bearer YOUR_TOKEN"`}</code>
              </pre>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Create Token Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-canvas-panel border border-canvas-border rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {generatedToken ? (
              // Token Generated View
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-500">
                    <CheckCircle2 size={20} />
                  </div>
                  <h3 className="text-xl font-semibold text-white">Token Created!</h3>
                </div>

                <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-4 mb-6">
                  <div className="flex items-start space-x-3">
                    <AlertCircle size={20} className="text-amber-500 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-amber-200">
                      <strong>Important:</strong> Copy your token now. For security reasons, it won't be shown again.
                    </div>
                  </div>
                </div>

                <div className="mb-6">
                  <label className="text-sm font-medium text-slate-300 block mb-2">Your API Token</label>
                  <div className="flex items-center space-x-2">
                    <input 
                      type="text"
                      value={generatedToken}
                      readOnly
                      className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm font-mono text-white"
                    />
                    <Button
                      variant={copiedToken ? "primary" : "secondary"}
                      size="sm"
                      onClick={handleCopyToken}
                    >
                      {copiedToken ? (
                        <>
                          <CheckCircle2 size={16} className="mr-2" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy size={16} className="mr-2" />
                          Copy
                        </>
                      )}
                    </Button>
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button onClick={resetModal}>Done</Button>
                </div>
              </div>
            ) : (
              // Create Token Form
              <div className="p-6">
                <h3 className="text-xl font-semibold text-white mb-6">Create API Token</h3>

                <div className="space-y-6">
                  <div>
                    <label className="text-sm font-medium text-slate-300 block mb-2">
                      Token Name
                    </label>
                    <input 
                      type="text"
                      value={newTokenName}
                      onChange={(e) => setNewTokenName(e.target.value)}
                      placeholder="e.g., CI/CD Pipeline"
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand"
                    />
                    <p className="text-xs text-slate-500 mt-1">
                      A descriptive name to help you identify this token
                    </p>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-slate-300 block mb-3">
                      Scopes
                    </label>
                    <div className="space-y-2">
                      {availableScopes.map((scope) => (
                        <label 
                          key={scope.id}
                          className="flex items-start space-x-3 p-3 bg-slate-800/30 rounded-lg border border-slate-700 hover:border-slate-600 cursor-pointer transition-colors"
                        >
                          <input 
                            type="checkbox"
                            checked={newTokenScopes.includes(scope.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setNewTokenScopes([...newTokenScopes, scope.id]);
                              } else {
                                setNewTokenScopes(newTokenScopes.filter(s => s !== scope.id));
                              }
                            }}
                            className="mt-0.5 h-4 w-4 rounded border-slate-600 text-brand focus:ring-brand focus:ring-offset-canvas-panel"
                          />
                          <div className="flex-1">
                            <div className="text-sm font-medium text-white">{scope.label}</div>
                            <div className="text-xs text-slate-400">{scope.description}</div>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex justify-end space-x-3 mt-6 pt-6 border-t border-slate-700">
                  <Button variant="secondary" onClick={resetModal}>
                    Cancel
                  </Button>
                  <Button 
                    variant="primary"
                    onClick={handleCreateToken}
                    disabled={!newTokenName || newTokenScopes.length === 0}
                  >
                    Create Token
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Developer;
