// src/pages/Documents.tsx
import React, { useEffect, useState, useRef } from 'react';
import {
  Upload,
  FileText,
  Trash2,
  CheckCircle2,
  AlertCircle,
  FileCode,
  FileSpreadsheet,
  File,
  Layers,
  HardDrive,
  Calendar,
} from 'lucide-react';
import { documentsApi } from '../api/documents';
import { DocumentItem } from '../types/api';
import StatusBadge from '../components/common/StatusBadge';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

export const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Upload state
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await documentsApi.listDocuments();
      setDocuments(data);
    } catch (err: any) {
      console.error('Error fetching documents:', err);
      setError(err.response?.data?.detail || 'Failed to retrieve company documents.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async (file: File) => {
    const allowed = ['pdf', 'docx', 'txt', 'csv', 'md'];
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!ext || !allowed.includes(ext)) {
      setUploadError(`Unsupported file format. Supported: ${allowed.join(', ').toUpperCase()}`);
      return;
    }

    try {
      setUploading(true);
      setUploadError(null);
      setUploadSuccess(null);
      setUploadProgress(0);

      const newDoc = await documentsApi.uploadDocument(file, (percent) => {
        setUploadProgress(percent);
      });

      setUploadSuccess(`Successfully ingested "${newDoc.filename}" (${newDoc.chunk_count} chunks generated).`);
      await fetchDocuments();
    } catch (err: any) {
      console.error('Upload error:', err);
      setUploadError(err.response?.data?.detail || 'Failed to upload and ingest document.');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleDelete = async (docId: string, filename: string) => {
    if (!window.confirm(`Are you sure you want to remove "${filename}" from the knowledge base?`)) {
      return;
    }

    try {
      await documentsApi.deleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete document.');
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getFileIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'pdf':
        return <FileText className="h-5 w-5 text-rose-500" />;
      case 'docx':
        return <File className="h-5 w-5 text-blue-500" />;
      case 'csv':
        return <FileSpreadsheet className="h-5 w-5 text-emerald-500" />;
      case 'md':
      case 'txt':
        return <FileCode className="h-5 w-5 text-slate-600" />;
      default:
        return <FileText className="h-5 w-5 text-slate-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header and Upload Area */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900">
            Document Knowledge Base
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            Manage company knowledge documents indexed with pgvector embeddings for RAG retrieval.
          </p>
        </div>

        <div>
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileChange}
            accept=".pdf,.docx,.txt,.csv,.md"
            className="hidden"
            id="doc-upload-input"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="inline-flex items-center space-x-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-blue-500 disabled:opacity-50 transition cursor-pointer"
          >
            <Upload className="h-4 w-4" />
            <span>{uploading ? 'Processing File...' : 'Upload Document'}</span>
          </button>
        </div>
      </div>

      {/* Upload Status Banners */}
      {uploading && (
        <div className="rounded-xl border border-blue-200 bg-blue-50/70 p-4 shadow-xs">
          <div className="flex items-center justify-between text-xs font-semibold text-blue-900 mb-2">
            <span>Uploading & Processing Chunks...</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="w-full bg-blue-200/80 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-200"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {uploadSuccess && (
        <div className="flex items-center space-x-2 rounded-xl border border-emerald-200 bg-emerald-50/70 p-4 text-xs font-medium text-emerald-800">
          <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
          <span>{uploadSuccess}</span>
        </div>
      )}

      {uploadError && (
        <div className="flex items-center space-x-2 rounded-xl border border-rose-200 bg-rose-50/70 p-4 text-xs font-medium text-rose-800">
          <AlertCircle className="h-4 w-4 text-rose-600 shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      {/* Drag & Drop Upload Zone */}
      <div
        onClick={() => fileInputRef.current?.click()}
        className="rounded-2xl border-2 border-dashed border-slate-200 bg-white p-8 text-center hover:border-blue-400 hover:bg-blue-50/20 transition cursor-pointer"
      >
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-600 mb-3">
          <Upload className="h-6 w-6" />
        </div>
        <h4 className="text-sm font-semibold text-slate-800">
          Click or drop files to upload
        </h4>
        <p className="mt-1 text-xs text-slate-500">
          Supported formats: PDF, DOCX, TXT, CSV, MD (Max 25 MB)
        </p>
      </div>

      {/* Document Listing Table */}
      {loading ? (
        <Loading message="Fetching ingested documents..." />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchDocuments} />
      ) : documents.length === 0 ? (
        <div className="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-xs">
          <FileText className="mx-auto h-12 w-12 text-slate-300 mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No documents uploaded yet</h3>
          <p className="mt-1 text-xs text-slate-500 max-w-sm mx-auto">
            Upload enterprise manuals, policies, or product specifications to populate the AI knowledge base.
          </p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-200/80 bg-slate-50/70 font-semibold text-slate-600 uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="py-3.5 pl-6 pr-3">Document</th>
                  <th className="px-3 py-3.5">Format</th>
                  <th className="px-3 py-3.5">Status</th>
                  <th className="px-3 py-3.5">Chunks</th>
                  <th className="px-3 py-3.5">Size</th>
                  <th className="px-3 py-3.5">Date Ingested</th>
                  <th className="py-3.5 pl-3 pr-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3 pl-6 pr-3">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 rounded-lg bg-slate-100">
                          {getFileIcon(doc.file_type)}
                        </div>
                        <div>
                          <p className="font-semibold text-slate-900 truncate max-w-xs sm:max-w-sm">
                            {doc.filename}
                          </p>
                          <span className="text-[10px] text-slate-400 font-mono">
                            {doc.id.substring(0, 8)}...
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-3 py-3 uppercase font-semibold text-slate-600">
                      {doc.file_type}
                    </td>
                    <td className="px-3 py-3">
                      <StatusBadge status={doc.status} />
                    </td>
                    <td className="px-3 py-3 text-slate-600">
                      <div className="flex items-center space-x-1">
                        <Layers className="w-3.5 h-3.5 text-slate-400" />
                        <span>{doc.chunk_count}</span>
                      </div>
                    </td>
                    <td className="px-3 py-3 text-slate-500">
                      <div className="flex items-center space-x-1">
                        <HardDrive className="w-3.5 h-3.5 text-slate-400" />
                        <span>{formatBytes(doc.file_size_bytes)}</span>
                      </div>
                    </td>
                    <td className="px-3 py-3 text-slate-500">
                      <div className="flex items-center space-x-1">
                        <Calendar className="w-3.5 h-3.5 text-slate-400" />
                        <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                      </div>
                    </td>
                    <td className="py-3 pl-3 pr-6 text-right">
                      <button
                        onClick={() => handleDelete(doc.id, doc.filename)}
                        className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition cursor-pointer"
                        title="Delete document"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
export default Documents;
