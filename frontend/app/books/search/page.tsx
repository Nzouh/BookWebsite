"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { searchBooks, Book, ExternalBook } from "@/lib/api";
import BookCard from "@/components/BookCard";
import BookGrid from "@/components/BookGrid";
import Link from "next/link";
import { Suspense } from "react";

function SearchContent() {
    const searchParams = useSearchParams();
    const query = searchParams.get("q") || searchParams.get("title") || "";
    const [localBooks, setLocalBooks] = useState<Book[]>([]);
    const [externalBooks, setExternalBooks] = useState<ExternalBook[]>([]);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState<"discover" | "library">("discover");

    useEffect(() => {
        if (query.trim()) {
            setLoading(true);
            searchBooks(query)
                .then((data) => {
                    setLocalBooks(data.local || []);
                    setExternalBooks(data.external || []);
                })
                .catch(console.error)
                .finally(() => setLoading(false));
        }
    }, [query]);

    return (
        <div className="search-container">
            <h1 className="search-title">
                {query ? <>Results for &ldquo;{query}&rdquo;</> : "Search Books"}
            </h1>

            {query && !loading && (
                <div className="tabs">
                    <button
                        className={`tab ${activeTab === "discover" ? "active" : ""}`}
                        onClick={() => setActiveTab("discover")}
                    >
                        🌍 Discover ({externalBooks.length})
                    </button>
                    <button
                        className={`tab ${activeTab === "library" ? "active" : ""}`}
                        onClick={() => setActiveTab("library")}
                    >
                        📚 In Your Library ({localBooks.length})
                    </button>
                </div>
            )}

            {loading ? (
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Searching across millions of books...</p>
                </div>
            ) : (
                <>
                    {activeTab === "discover" && (
                        <div className="results-section">
                            {externalBooks.length > 0 ? (
                                <div className="external-grid">
                                    {externalBooks.map((book, index) => (
                                        <Link
                                            key={book.hash || index}
                                            href={`/books/external/${book.hash}`}
                                            className="external-card-link"
                                        >
                                            <div className="external-card">
                                                {book.cover_url ? (
                                                    <img
                                                        src={book.cover_url}
                                                        alt={book.title}
                                                        className="external-cover"
                                                    />
                                                ) : (
                                                    <div className="cover-placeholder">
                                                        <span>📖</span>
                                                    </div>
                                                )}
                                                <div className="external-info">
                                                    <h3 className="external-title" title={book.title}>
                                                        {book.title}
                                                    </h3>
                                                    <p className="external-author">{book.authors || "Unknown Author"}</p>
                                                    <div className="meta-tags">
                                                        {book.format && <span className="meta-tag format">{book.format}</span>}
                                                        {book.size && <span className="meta-tag">{book.size}</span>}
                                                        {book.year && <span className="meta-tag">{book.year}</span>}
                                                        {book.language && <span className="meta-tag">{book.language}</span>}
                                                    </div>
                                                </div>
                                            </div>
                                        </Link>
                                    ))}
                                </div>
                            ) : (
                                query && <p className="no-results">No external results found. Try a different search term.</p>
                            )}
                        </div>
                    )}

                    {activeTab === "library" && (
                        <div className="results-section">
                            {localBooks.length > 0 ? (
                                <BookGrid>
                                    {localBooks.map((book) => (
                                        <BookCard key={book._id} book={book} />
                                    ))}
                                </BookGrid>
                            ) : (
                                query && <p className="no-results">No books in your library match this search.</p>
                            )}
                        </div>
                    )}
                </>
            )}

            <style jsx>{`
                .search-container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }
                .search-title {
                    font-size: 2rem;
                    color: var(--brown-900);
                    margin-bottom: 1.5rem;
                }
                .tabs {
                    display: flex;
                    gap: 0;
                    border-bottom: 2px solid var(--brown-100);
                    margin-bottom: 2rem;
                }
                .tab {
                    background: none;
                    border: none;
                    padding: 0.75rem 1.5rem;
                    font-size: 1rem;
                    color: var(--brown-500);
                    border-bottom: 3px solid transparent;
                    margin-bottom: -2px;
                    cursor: pointer;
                    transition: all 0.2s;
                    font-weight: 500;
                }
                .tab:hover {
                    color: var(--brown-700);
                    background-color: var(--brown-50, #faf5f0);
                }
                .tab.active {
                    color: var(--brown-900);
                    border-bottom-color: var(--brown-700);
                    font-weight: 600;
                }
                .loading-state {
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
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
                .no-results {
                    text-align: center;
                    padding: 3rem;
                    color: var(--brown-500);
                    font-size: 1.1rem;
                }
                .external-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
                    gap: 1.5rem;
                }
                .external-card-link {
                    text-decoration: none;
                    color: inherit;
                    display: block;
                }
                .external-card {
                    background: var(--white);
                    border-radius: 10px;
                    border: 1px solid var(--brown-100);
                    overflow: hidden;
                    transition: transform 0.2s, box-shadow 0.2s;
                    height: 100%;
                }
                .external-card:hover {
                    transform: translateY(-4px);
                    box-shadow: 0 8px 24px rgba(62, 39, 35, 0.12);
                }
                .external-cover {
                    width: 100%;
                    height: 320px;
                    object-fit: cover;
                }
                .cover-placeholder {
                    width: 100%;
                    height: 320px;
                    background: linear-gradient(135deg, var(--brown-100) 0%, var(--brown-200) 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 3rem;
                }
                .external-info {
                    padding: 1rem;
                }
                .external-title {
                    font-size: 0.95rem;
                    font-weight: 600;
                    margin-bottom: 0.4rem;
                    color: var(--brown-900);
                    overflow: hidden;
                    text-overflow: ellipsis;
                    display: -webkit-box;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                    line-height: 1.3;
                    min-height: 2.4em;
                }
                .external-author {
                    font-size: 0.85rem;
                    color: var(--brown-600);
                    margin-bottom: 0.6rem;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
                .meta-tags {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 0.4rem;
                }
                .meta-tag {
                    font-size: 0.7rem;
                    padding: 0.2rem 0.5rem;
                    background-color: var(--brown-50, #faf5f0);
                    color: var(--brown-700);
                    border-radius: 4px;
                    font-weight: 500;
                }
                .meta-tag.format {
                    background-color: var(--brown-200);
                    color: var(--brown-800);
                    text-transform: uppercase;
                    font-weight: 600;
                }
                .results-section {
                    min-height: 200px;
                }
            `}</style>
        </div>
    );
}

export default function SearchPage() {
    return (
        <Suspense fallback={<div style={{ padding: "2rem", textAlign: "center" }}>Loading search...</div>}>
            <SearchContent />
        </Suspense>
    );
}
