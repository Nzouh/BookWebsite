"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { getDownloadStatus } from "@/lib/api";

interface DownloadProgressProps {
    jobId: string;
    bookId: string;
    onComplete?: () => void;
    onRetry?: () => void;
}

export default function DownloadProgress({ jobId, bookId, onComplete, onRetry }: DownloadProgressProps) {
    const [status, setStatus] = useState("pending");
    const [progress, setProgress] = useState(0);
    const [errorMessage, setErrorMessage] = useState("");
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        if (!jobId) return;

        const poll = async () => {
            try {
                const data = await getDownloadStatus(jobId);
                setStatus(data.status);
                setProgress(data.progress);
                setErrorMessage(data.error_message || "");

                if (data.status === "completed") {
                    if (intervalRef.current) clearInterval(intervalRef.current);
                    onComplete?.();
                }
                if (data.status === "failed") {
                    if (intervalRef.current) clearInterval(intervalRef.current);
                }
            } catch (err) {
                console.error("Failed to poll download status", err);
            }
        };

        poll(); // immediate first poll
        intervalRef.current = setInterval(poll, 2000);

        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, [jobId, onComplete]);

    const statusLabel = () => {
        switch (status) {
            case "pending": return "Queued — waiting to start…";
            case "downloading":
                if (progress < 30) return "Fetching book metadata…";
                if (progress < 60) return "Downloading book file…";
                if (progress < 90) return "Parsing chapters…";
                return "Almost done…";
            case "completed": return "Ready to read!";
            case "failed": return "Download failed";
            default: return "Processing…";
        }
    };

    const isComplete = status === "completed";
    const isFailed = status === "failed";

    return (
        <div className="download-progress">
            <div className="progress-header">
                <span className="progress-icon">
                    {isComplete ? "✅" : isFailed ? "❌" : "📥"}
                </span>
                <span className="progress-label">{statusLabel()}</span>
            </div>

            {!isComplete && !isFailed && (
                <div className="progress-bar-container">
                    <div
                        className="progress-bar-fill"
                        style={{ width: `${Math.max(progress, 5)}%` }}
                    />
                    <span className="progress-percent">{progress}%</span>
                </div>
            )}

            {isComplete && (
                <div className="progress-actions">
                    <Link href={`/books/${bookId}`} className="btn-read-now">
                        📖 Read Now
                    </Link>
                </div>
            )}

            {isFailed && (
                <div className="progress-error">
                    <p className="error-text">{errorMessage || "An error occurred during download."}</p>
                    {onRetry && (
                        <button onClick={onRetry} className="btn-retry">
                            🔄 Try Again
                        </button>
                    )}
                </div>
            )}

            <style jsx>{`
                .download-progress {
                    margin-top: 1.5rem;
                    padding: 1.25rem 1.5rem;
                    background: linear-gradient(135deg, #faf5f0 0%, #f5ede4 100%);
                    border: 1px solid var(--brown-200, #d7ccc8);
                    border-radius: 12px;
                    animation: slideIn 0.3s ease-out;
                }
                @keyframes slideIn {
                    from { opacity: 0; transform: translateY(-10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .progress-header {
                    display: flex;
                    align-items: center;
                    gap: 0.6rem;
                    margin-bottom: 0.75rem;
                }
                .progress-icon {
                    font-size: 1.2rem;
                }
                .progress-label {
                    font-weight: 600;
                    font-size: 0.95rem;
                    color: var(--brown-800, #4e342e);
                }
                .progress-bar-container {
                    position: relative;
                    width: 100%;
                    height: 28px;
                    background: var(--brown-100, #d7ccc8);
                    border-radius: 14px;
                    overflow: hidden;
                }
                .progress-bar-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #8d6e63, #6d4c41, #5d4037);
                    border-radius: 14px;
                    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
                    position: relative;
                }
                .progress-bar-fill::after {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: linear-gradient(
                        90deg,
                        transparent 0%,
                        rgba(255, 255, 255, 0.15) 50%,
                        transparent 100%
                    );
                    animation: shimmer 2s infinite;
                }
                @keyframes shimmer {
                    0% { transform: translateX(-100%); }
                    100% { transform: translateX(100%); }
                }
                .progress-percent {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 0.8rem;
                    font-weight: 700;
                    color: white;
                    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
                }
                .progress-actions {
                    margin-top: 0.75rem;
                    display: flex;
                    gap: 0.75rem;
                }
                .btn-read-now {
                    display: inline-block;
                    padding: 0.65rem 1.5rem;
                    font-size: 1rem;
                    font-weight: 600;
                    background: linear-gradient(135deg, #5d4037, #4e342e);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    text-decoration: none;
                    transition: all 0.2s;
                    box-shadow: 0 2px 8px rgba(62, 39, 35, 0.25);
                }
                .btn-read-now:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 16px rgba(62, 39, 35, 0.35);
                }
                .progress-error {
                    margin-top: 0.5rem;
                }
                .error-text {
                    font-size: 0.9rem;
                    color: #c62828;
                    margin-bottom: 0.75rem;
                    line-height: 1.4;
                }
                .btn-retry {
                    padding: 0.5rem 1.25rem;
                    font-size: 0.9rem;
                    font-weight: 600;
                    background: white;
                    color: var(--brown-800, #4e342e);
                    border: 2px solid var(--brown-300, #bcaaa4);
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                .btn-retry:hover {
                    background: var(--brown-50, #efebe9);
                    border-color: var(--brown-500, #8d6e63);
                }
            `}</style>
        </div>
    );
}
