'use client';

import { useState } from 'react';
import { QueryResult } from '@/app/page';

const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? `http://${window.location.hostname}:8000` : 'http://localhost:8000');

interface QueryPanelProps {
    namespace: string | null;
    onQueryStart: () => void;
    onQueryResult: (result: QueryResult) => void;
    onQueryError: () => void;
}

export default function QueryPanel({
    namespace,
    onQueryStart,
    onQueryResult,
    onQueryError
}: QueryPanelProps) {
    const [query, setQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleQuery = async () => {
        if (!query.trim()) {
            setError('Please enter a question');
            return;
        }

        setIsLoading(true);
        setError(null);
        onQueryStart();

        try {
            const response = await fetch(`${API_URL}/api/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    namespace: namespace,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Query failed');
            }

            onQueryResult(data);
        } catch (err: any) {
            setError(err.message || 'Query failed');
            onQueryError();
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleQuery();
        }
    };

    return (
        <div className="glass-card p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Ask a Question
            </h2>

            {/* Status Badge */}
            <div className="mb-4">
                {namespace ? (
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/30 rounded-full text-green-400 text-sm">
                        <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                        Document indexed
                    </div>
                ) : (
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-yellow-500/10 border border-yellow-500/30 rounded-full text-yellow-400 text-sm">
                        <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                        Upload a document first
                    </div>
                )}
            </div>

            {/* Query Input */}
            <div className="relative">
                <textarea
                    className="textarea-field pr-12"
                    placeholder="Ask anything about your documents..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                    rows={4}
                />
                <button
                    className="absolute right-3 bottom-3 p-2 bg-indigo-500 hover:bg-indigo-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    onClick={handleQuery}
                    disabled={isLoading || !query.trim()}
                >
                    {isLoading ? (
                        <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                    ) : (
                        <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                        </svg>
                    )}
                </button>
            </div>

            {/* Error Message */}
            {error && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                    {error}
                </div>
            )}

            {/* Example Queries */}
            <div className="mt-4">
                <p className="text-gray-500 text-sm mb-2">Try asking:</p>
                <div className="flex flex-wrap gap-2">
                    {['What is the main topic?', 'Summarize the key points', 'List the main concepts'].map((q) => (
                        <button
                            key={q}
                            className="text-xs px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-full text-gray-400 hover:text-gray-300 transition-colors"
                            onClick={() => setQuery(q)}
                        >
                            {q}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
