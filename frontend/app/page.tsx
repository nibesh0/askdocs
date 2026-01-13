'use client';

import { useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? `http://${window.location.hostname}:8000` : 'http://localhost:8000');

interface Citation {
  number: number;
  text: string;
  source: string;
  title: string;
  score: number;
}

export default function Home() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [namespace, setNamespace] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);
  const [hasQueried, setHasQueried] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (files: FileList) => {
    setIsUploading(true);
    setError(null);
    setUploadStatus(null);

    const results: string[] = [];
    let currentNamespace = namespace; // Use existing namespace if available

    for (const file of Array.from(files)) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', file.name);
      // Pass namespace so all files go into the same index
      if (currentNamespace) {
        formData.append('namespace', currentNamespace);
      }

      try {
        const response = await fetch(`${API_URL}/api/upload`, {
          method: 'POST',
          body: formData,
        });
        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || `Upload failed for ${file.name}`);

        // After first upload, use the returned namespace for subsequent files
        currentNamespace = data.stats.namespace;
        results.push(`✓ ${file.name} — ${data.stats.chunks_created} chunks`);
      } catch (err: any) {
        results.push(`✗ ${file.name} — ${err.message}`);
      }
    }

    if (currentNamespace) setNamespace(currentNamespace);
    setUploadStatus(results.join(' | '));
    setIsUploading(false);
  };

  const handleQuery = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setAnswer(null);
    setCitations([]);
    setHasQueried(true);

    try {
      const response = await fetch(`${API_URL}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, namespace }),
      });
      const data = await response.json();

      if (!response.ok) throw new Error(data.detail || 'Query failed');

      setAnswer(data.answer);
      setCitations(data.citations || []);
      setStats({
        time: data.timing_ms,
        tokens: data.token_estimate
      });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="app-layout">
      {/* Main Content Area */}
      <div className="content-area">
        <div className="container">
          <h1 className="title">AskDocs</h1>
          <p className="subtitle">Upload documents and ask questions.</p>

          {/* Answer Section */}
          {answer && (
            <div className="section">
              <div className="section-title">Answer</div>
              <div className="answer-box markdown-content">
                <ReactMarkdown>{answer}</ReactMarkdown>
              </div>
              {stats && (
                <div className="stats">
                  <span>{stats.time}ms</span>
                  <span>~{stats.tokens} tokens</span>
                </div>
              )}
            </div>
          )}

          {/* Citations Section */}
          {citations.length > 0 && (
            <div className="section">
              <div className="section-title">Sources</div>
              <div className="citations-list">
                {citations.map((citation) => (
                  <div key={citation.number} className="citation-item">
                    <div className="citation-number">[{citation.number}]</div>
                    <div className="citation-content">
                      <div className="citation-title">{citation.title}</div>
                      <div className="citation-text">{citation.text}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error */}
          {error && <div className="status-error">{error}</div>}
        </div>
      </div>

      {/* Sticky Bottom Bar */}
      <div className="sticky-bar">
        {/* Upload */}
        <div className="upload-inline">
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.pdf,.md"
            multiple
            style={{ display: 'none' }}
            onChange={async (e) => {
              if (e.target.files && e.target.files.length > 0) {
                await handleFileUpload(e.target.files);
                e.target.value = ''; // Reset to allow re-uploading same files
              }
            }}
          />
          <button
            className="btn-icon"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            title="Upload document"
          >
            {isUploading ? '⏳' : '📎'}
          </button>
          {uploadStatus && <span className="upload-status">{uploadStatus}</span>}
        </div>

        {/* Query Input */}
        <div className="query-bar">
          <input
            type="text"
            className="input-field-inline"
            placeholder="Ask a question..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
          />
          <button
            className="btn btn-primary"
            onClick={handleQuery}
            disabled={isLoading || !query.trim()}
          >
            {isLoading ? <span className="loading-dots"><span>.</span><span>.</span><span>.</span></span> : '→'}
          </button>
        </div>

        {/* Example buttons - only show before first query */}
        {!hasQueried && (
          <div className="example-buttons">
            {['summarize', 'key points', 'explain'].map((q) => (
              <button key={q} className="link-btn-small" onClick={() => setQuery(q)}>
                {q}
              </button>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
