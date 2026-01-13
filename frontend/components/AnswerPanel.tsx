'use client';

import { useState } from 'react';
import { QueryResult, Citation } from '@/app/page';

interface AnswerPanelProps {
    result: QueryResult | null;
    isLoading: boolean;
}

export default function AnswerPanel({ result, isLoading }: AnswerPanelProps) {
    const [expandedCitation, setExpandedCitation] = useState<number | null>(null);

    if (isLoading) {
        return (
            <div className="glass-card p-6">
                <div className="flex items-center gap-3 mb-4">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-500 to-cyan-500 animate-pulse"></div>
                    <div className="h-4 w-24 bg-gray-700 rounded animate-pulse"></div>
                </div>
                <div className="space-y-3">
                    <div className="h-4 bg-gray-700 rounded w-full animate-pulse"></div>
                    <div className="h-4 bg-gray-700 rounded w-5/6 animate-pulse"></div>
                    <div className="h-4 bg-gray-700 rounded w-4/6 animate-pulse"></div>
                </div>
            </div>
        );
    }

    if (!result) {
        return (
            <div className="glass-card p-6 text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-800 flex items-center justify-center">
                    <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                </div>
                <p className="text-gray-500">Upload a document and ask a question to see answers here</p>
            </div>
        );
    }

    // Parse answer to highlight citations
    const parseAnswerWithCitations = (text: string) => {
        const parts = text.split(/(\[\d+\])/g);
        return parts.map((part, index) => {
            const match = part.match(/\[(\d+)\]/);
            if (match) {
                const citNum = parseInt(match[1]);
                return (
                    <button
                        key={index}
                        className="citation-tag"
                        onClick={() => setExpandedCitation(expandedCitation === citNum ? null : citNum)}
                        title="Click to view source"
                    >
                        {citNum}
                    </button>
                );
            }
            return <span key={index}>{part}</span>;
        });
    };

    return (
        <div className="glass-card p-6">
            {/* Answer Header */}
            <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-500 to-cyan-500 flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                </div>
                <h3 className="text-lg font-semibold">Answer</h3>
            </div>

            {/* Answer Text */}
            <div className="text-gray-200 leading-relaxed mb-6 whitespace-pre-wrap">
                {parseAnswerWithCitations(result.answer)}
            </div>

            {/* Citations Section */}
            {result.citations && result.citations.length > 0 && (
                <div className="border-t border-gray-700 pt-4">
                    <h4 className="text-sm font-medium text-gray-400 mb-3">Sources</h4>
                    <div className="space-y-2">
                        {result.citations.map((citation: Citation) => (
                            <div
                                key={citation.number}
                                className={`p-3 rounded-lg transition-all cursor-pointer ${expandedCitation === citation.number
                                        ? 'bg-indigo-500/20 border border-indigo-500/30'
                                        : 'bg-gray-800/50 hover:bg-gray-800'
                                    }`}
                                onClick={() => setExpandedCitation(
                                    expandedCitation === citation.number ? null : citation.number
                                )}
                            >
                                <div className="flex items-start gap-2">
                                    <span className="citation-tag flex-shrink-0">{citation.number}</span>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-gray-300 truncate">
                                            {citation.title}
                                        </p>
                                        {expandedCitation === citation.number && (
                                            <div className="mt-2">
                                                <p className="text-sm text-gray-400 italic">
                                                    "{citation.text}"
                                                </p>
                                                <div className="flex items-center gap-2 mt-2">
                                                    <span className="text-xs text-gray-500">
                                                        Source: {citation.source}
                                                    </span>
                                                    <span className="text-xs text-gray-500">
                                                        Score: {(citation.score * 100).toFixed(1)}%
                                                    </span>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                    <svg
                                        className={`w-4 h-4 text-gray-500 transition-transform ${expandedCitation === citation.number ? 'rotate-180' : ''
                                            }`}
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                    </svg>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Stats Section */}
            <div className="border-t border-gray-700 pt-4 mt-4">
                <div className="flex flex-wrap gap-3">
                    <div className="stats-badge">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Total: {result.timing.total_ms}ms
                    </div>
                    <div className="stats-badge">
                        Embed: {result.timing.embedding_ms}ms
                    </div>
                    <div className="stats-badge">
                        Retrieve: {result.timing.retrieval_ms}ms
                    </div>
                    <div className="stats-badge">
                        Rerank: {result.timing.reranking_ms}ms
                    </div>
                    <div className="stats-badge">
                        Generate: {result.timing.generation_ms}ms
                    </div>
                    <div className="stats-badge">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        ~{result.cost_estimate.input_tokens + result.cost_estimate.output_tokens} tokens
                    </div>
                    <div className="stats-badge">
                        ${result.cost_estimate.estimated_cost_usd.toFixed(6)}
                    </div>
                </div>
            </div>
        </div>
    );
}
