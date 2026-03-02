"use client";

import { useEffect, useState, use, useCallback } from "react";
import { useRouter } from "next/navigation";
import { getExternalBookDetails, oneClickDownload } from "@/lib/api";
import DownloadProgress from "@/components/DownloadProgress";
import Link from "next/link";

export default function ExternalBookDetailPage({ params }: { params: Promise<{ md5: string }> }) {
    const { md5 } = use(params);
    const router = useRouter();
    const [book, setBook] = useState<any>(null);
    const [source, setSource] = useState<string>("");
    const [localId, setLocalId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // Download state
    const [downloading, setDownloading] = useState(false);
    const [jobId, setJobId] = useState<string | null>(null);
    const [bookId, setBookId] = useState<string | null>(null);

    useEffect(() => {
        async function fetchData() {
            try {
                const data = await getExternalBookDetails(md5);
                setBook(data.book);
                setSource(data.source);
                setLocalId(data.local_id);
            } catch (err: any) {
                console.error("Failed to fetch book details", err);
                setError(err.message || "Could not load book details");
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [md5]);

    const handleDownload = async () => {
        setDownloading(true);
        setError("");
        try {
            const result = await oneClickDownload(md5);
            if (result.status === "already_ready" && result.book_id) {
                router.push(`/books/${result.book_id}`);
                return;
            }
            if (result.job_id) {
                setJobId(result.job_id);
                setBookId(result.book_id || null);
            } else if (result.book_id) {
                // Processing — no job id, but book exists
                setBookId(result.book_id);
            }
        } catch (err: any) {
            setError(err.message || "Failed to start download");
            setDownloading(false);
        }
    };

    const handleRetry = () => {
        setJobId(null);
        setBookId(null);
        setDownloading(false);
        setError("");
        handleDownload();
    };

    const handleComplete = useCallback(() => {
        // Progress component will show "Read Now" link
    }, []);

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Loading book details...</p>
                <style jsx>{`
                    .loading-container {
                        text-align: center;
                        padding: 4rem 2rem;
                        color: var(--brown-600);
                    }
                    .spinner {
                        width: 40px;
                        height: 40px;
                        border: 3px solid var(--brown-100);
                        border-top-color: var(--brown-600);
                        border-radius: 50%;
                        animation: spin 0.8s linear infinite;
                        margin: 0 auto 1rem;
                    }
                    @keyframes spin { to { transform: rotate(360deg); } }
                `}</style>
            </div>
        );
    }

    if (error && !book) {
        return (
            <div className="error-container">
                <h2>Something went wrong</h2>
                <p>{error}</p>
                <Link href="/books/search" className="btn btn-outline">← Back to Search</Link>
                <style jsx>{`
                    .error-container {
                        text-align: center;
                        padding: 4rem 2rem;
                    }
                    h2 { color: var(--brown-900); margin-bottom: 1rem; }
                    p { color: var(--brown-600); margin-bottom: 2rem; }
                `}</style>
            </div>
        );
    }

    if (!book) return <div>Book not found.</div>;

    // If we already have this book locally, redirect the user
    if (source === "local" && localId) {
        router.push(`/books/${localId}`);
        return <div>Redirecting to your library...</div>;
    }

    const coverUrl = book.cover_url || book.image;
    const description = book.description || book.biography || "";
    const authorName = book.authors || book.author || "Unknown Author";

    return (
        <div className="detail-container">
            <div className="back-nav">
                <Link href="/books/search" className="back-link">← Back to Search</Link>
            </div>

            <div className="book-detail">
                <div className="cover-section">
                    {coverUrl ? (
                        <img src={coverUrl} alt={book.title} className="book-cover" />
                    ) : (
                        <div className="cover-placeholder">
                            <span>📖</span>
                        </div>
                    )}
                </div>

                <div className="info-section">
                    <h1 className="book-title">{book.title}</h1>
                    <p className="book-author">by {authorName}</p>

                    <div className="meta-row">
                        {book.format && <span className="meta-badge format">{book.format}</span>}
                        {book.size && <span className="meta-badge">{book.size}</span>}
                        {book.language && <span className="meta-badge">{book.language}</span>}
                        {book.year && <span className="meta-badge">{book.year}</span>}
                    </div>

                    {book.publisher && (
                        <p className="publisher">Published by {book.publisher}</p>
                    )}
                    {book.isbn && (
                        <p className="isbn">ISBN: {book.isbn}</p>
                    )}

                    {description && (
                        <div className="description">
                            <h3>About this book</h3>
                            <p>{description}</p>
                        </div>
                    )}

                    {/* Download action area */}
                    {!jobId && !downloading && (
                        <div className="actions">
                            <button
                                onClick={handleDownload}
                                className="btn-download"
                            >
                                ⬇️ Download & Read
                            </button>
                        </div>
                    )}

                    {downloading && !jobId && !error && (
                        <div className="initializing">
                            <div className="mini-spinner"></div>
                            <span>Starting download...</span>
                        </div>
                    )}

                    {error && !jobId && (
                        <div className="error-inline">
                            <p>❌ {error}</p>
                            <button onClick={handleRetry} className="btn-retry-inline">🔄 Try Again</button>
                        </div>
                    )}

                    {jobId && bookId && (
                        <DownloadProgress
                            jobId={jobId}
                            bookId={bookId}
                            onComplete={handleComplete}
                            onRetry={handleRetry}
                        />
                    )}

                    <p className="source-note">
                        Source: Anna&apos;s Archive
                    </p>
                </div>
            </div>

            <style jsx>{`
                .detail-container {
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 2rem;
                }
                .back-nav {
                    margin-bottom: 2rem;
                }
                .back-link {
                    color: var(--brown-500);
                    font-weight: 500;
                    text-decoration: none;
                }
                .back-link:hover {
                    color: var(--brown-900);
                    text-decoration: underline;
                }
                .book-detail {
                    display: flex;
                    gap: 3rem;
                }
                .cover-section {
                    flex: 0 0 280px;
                }
                .book-cover {
                    width: 100%;
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(62, 39, 35, 0.2);
                }
                .cover-placeholder {
                    width: 100%;
                    aspect-ratio: 2/3;
                    background: linear-gradient(135deg, var(--brown-100), var(--brown-200));
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 4rem;
                }
                .info-section {
                    flex: 1;
                }
                .book-title {
                    font-size: 2.25rem;
                    color: var(--brown-900);
                    margin-bottom: 0.5rem;
                    line-height: 1.2;
                }
                .book-author {
                    font-size: 1.2rem;
                    color: var(--brown-500);
                    margin-bottom: 1.25rem;
                }
                .meta-row {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 0.5rem;
                    margin-bottom: 1.25rem;
                }
                .meta-badge {
                    font-size: 0.8rem;
                    padding: 0.3rem 0.75rem;
                    background-color: var(--brown-50, #faf5f0);
                    color: var(--brown-700);
                    border-radius: 20px;
                    font-weight: 500;
                }
                .meta-badge.format {
                    background-color: var(--brown-200);
                    color: var(--brown-900);
                    text-transform: uppercase;
                    font-weight: 700;
                }
                .publisher, .isbn {
                    font-size: 0.9rem;
                    color: var(--brown-600);
                    margin-bottom: 0.5rem;
                }
                .description {
                    margin: 1.5rem 0;
                    padding: 1.5rem;
                    background: var(--cream-light, #fefaf5);
                    border-radius: 8px;
                    border-left: 4px solid var(--brown-300);
                }
                .description h3 {
                    font-size: 1rem;
                    color: var(--brown-900);
                    margin-bottom: 0.75rem;
                }
                .description p {
                    font-size: 1rem;
                    line-height: 1.7;
                    color: var(--brown-800);
                }
                .actions {
                    margin-top: 2rem;
                    display: flex;
                    gap: 1rem;
                }
                .btn-download {
                    padding: 0.9rem 2rem;
                    font-size: 1.05rem;
                    font-weight: 600;
                    background: linear-gradient(135deg, var(--brown-700), var(--brown-800));
                    color: white;
                    border: none;
                    border-radius: 10px;
                    cursor: pointer;
                    transition: all 0.2s;
                    box-shadow: 0 2px 8px rgba(62, 39, 35, 0.2);
                }
                .btn-download:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 16px rgba(62, 39, 35, 0.3);
                }
                .initializing {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    margin-top: 1.5rem;
                    padding: 1rem 1.25rem;
                    background: var(--brown-50, #faf5f0);
                    border-radius: 8px;
                    color: var(--brown-700);
                    font-weight: 500;
                }
                .mini-spinner {
                    width: 20px;
                    height: 20px;
                    border: 2.5px solid var(--brown-200);
                    border-top-color: var(--brown-600);
                    border-radius: 50%;
                    animation: spin 0.8s linear infinite;
                }
                @keyframes spin { to { transform: rotate(360deg); } }
                .error-inline {
                    margin-top: 1.5rem;
                    padding: 1rem 1.25rem;
                    background: #fef2f2;
                    border: 1px solid #fecaca;
                    border-radius: 8px;
                }
                .error-inline p {
                    color: #991b1b;
                    font-size: 0.9rem;
                    margin-bottom: 0.75rem;
                }
                .btn-retry-inline {
                    padding: 0.45rem 1rem;
                    font-size: 0.85rem;
                    font-weight: 600;
                    background: white;
                    color: var(--brown-800);
                    border: 2px solid var(--brown-300);
                    border-radius: 6px;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                .btn-retry-inline:hover {
                    background: var(--brown-50, #efebe9);
                }
                .source-note {
                    margin-top: 1.5rem;
                    font-size: 0.8rem;
                    color: var(--brown-400);
                }
                @media (max-width: 768px) {
                    .book-detail {
                        flex-direction: column;
                        gap: 1.5rem;
                    }
                    .cover-section {
                        flex: none;
                        max-width: 250px;
                        margin: 0 auto;
                    }
                }
            `}</style>
        </div>
    );
}
