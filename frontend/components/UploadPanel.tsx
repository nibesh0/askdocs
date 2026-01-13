'use client';

import { useState, useRef } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? `http://${window.location.hostname}:8000` : 'http://localhost:8000');

interface UploadPanelProps {
    onUploadSuccess: (namespace: string) => void;
}

export default function UploadPanel({ onUploadSuccess }: UploadPanelProps) {
    const [text, setText] = useState('');
    const [title, setTitle] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const [uploadResult, setUploadResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            await uploadFile(e.dataTransfer.files[0]);
        }
    };

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            await uploadFile(e.target.files[0]);
        }
    };

    const uploadFile = async (file: File) => {
        setIsUploading(true);
        setError(null);
        setUploadResult(null);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', title || file.name);

        try {
            const response = await fetch(`${API_URL}/api/upload`, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Upload failed');
            }

            setUploadResult(data);
            onUploadSuccess(data.stats.namespace);
        } catch (err: any) {
            setError(err.message || 'Upload failed');
        } finally {
            setIsUploading(false);
        }
    };

    const uploadText = async () => {
        if (!text.trim()) {
            setError('Please enter some text');
            return;
        }

        setIsUploading(true);
        setError(null);
        setUploadResult(null);

        const formData = new FormData();
        formData.append('text', text);
        formData.append('title', title || 'Direct Input');

        try {
            const response = await fetch(`${API_URL}/api/upload`, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Upload failed');
            }

            setUploadResult(data);
            onUploadSuccess(data.stats.namespace);
            setText('');
        } catch (err: any) {
            setError(err.message || 'Upload failed');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="glass-card p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                Upload Document
            </h2>

            {/* File Drop Zone */}
            <div
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all mb-4 ${dragActive
                    ? 'border-indigo-500 bg-indigo-500/10'
                    : 'border-gray-600 hover:border-gray-500'
                    }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    accept=".txt,.pdf,.md"
                    onChange={handleFileChange}
                />
                <svg className="w-10 h-10 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-gray-400 text-sm">
                    Drop a file here or click to browse
                </p>
                <p className="text-gray-500 text-xs mt-1">.txt, .pdf, .md (max 5MB)</p>
            </div>

            <div className="relative my-4">
                <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-700"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-[#1e1e23] text-gray-500">or paste text</span>
                </div>
            </div>

            {/* Title Input */}
            <input
                type="text"
                className="input-field mb-3"
                placeholder="Document title (optional)"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
            />

            {/* Text Input */}
            <textarea
                className="textarea-field"
                placeholder="Paste your text content here..."
                value={text}
                onChange={(e) => setText(e.target.value)}
            />

            {/* Upload Button */}
            <button
                className="btn-primary w-full mt-4"
                onClick={uploadText}
                disabled={isUploading || !text.trim()}
            >
                {isUploading ? (
                    <span className="flex items-center justify-center gap-2">
                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Processing...
                    </span>
                ) : (
                    'Upload & Index'
                )}
            </button>

            {/* Error Message */}
            {error && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                    {error}
                </div>
            )}

            {/* Success Message */}
            {uploadResult && (
                <div className="mt-4 p-3 bg-green-500/10 border border-green-500/30 rounded-lg text-green-400 text-sm">
                    <p className="font-medium">✓ Indexed successfully!</p>
                    <div className="flex flex-wrap gap-2 mt-2">
                        <span className="stats-badge">
                            {uploadResult.stats.chunks_created} chunks
                        </span>
                        <span className="stats-badge">
                            ~{uploadResult.stats.avg_chunk_tokens} tokens/chunk
                        </span>
                        <span className="stats-badge">
                            {uploadResult.stats.processing_time_ms}ms
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
}
