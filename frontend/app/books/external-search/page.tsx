"use client";

import { useState } from "react";
import { externalSearchBooks } from "@/lib/api";

interface ExternalBook {
    title: string;
    authors: string;
    format: string;
    size: string;
    cover_url: string;
    hash: string;
    year: string;
    language: string;
    url: string;
}

export default function ExternalSearchPage() {
    const [query, setQuery] = useState("");
    const [books, setBooks] = useState<ExternalBook[]>([]);
    const [loading, setLoading] = useState(false);
    const [source, setSource] = useState("");

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        try {
            const data = await externalSearchBooks(query);
            setBooks(data.books || []);
            setSource(data.source || "");
        } catch (error) {
            console.error("Search failed:", error);
            alert("Search failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <h1 className="page-title">Search Anna's Archive</h1>
            <p className="subtitle">Search millions of books from external sources</p>

            <form onSubmit={handleSearch} className="search-form">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search for books by title, author, topic..."
                    className="search-input"
                />
                <button type="submit" disabled={loading} className="search-button">
                    {loading ? "Searching..." : "Search"}
                </button>
            </form>

            {source && (
                <p className="source-info">
                    Found {books.length} results from <strong>{source}</strong>
                </p>
            )}

            {loading ? (
                <p className="loading-text">Searching external sources...</p>
            ) : books.length > 0 ? (
                <div className="books-grid">
                    {books.map((book, index) => (
                        <a
                            key={book.hash || index}
                            href={book.url || `https://annas-archive.li/md5/${book.hash}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="book-card-link"
                        >
                            <div className="book-card">
                                {book.cover_url ? (
                                    <img
                                        src={book.cover_url}
                                        alt={book.title}
                                        className="book-cover"
                                    />
                                ) : (
                                    <div className="book-cover-placeholder">
                                        <span>No Cover</span>
                                    </div>
                                )}
                                <div className="book-info">
                                    <h3 className="book-title" title={book.title}>
                                        {book.title}
                                    </h3>
                                    <p className="book-author">{book.authors || "Unknown Author"}</p>
                                    <div className="book-meta">
                                        {book.format && <span className="meta-tag">{book.format}</span>}
                                        {book.size && <span className="meta-tag">{book.size}</span>}
                                        {book.year && <span className="meta-tag">{book.year}</span>}
                                        {book.language && <span className="meta-tag">{book.language}</span>}
                                    </div>
                                </div>
                            </div>
                        </a>
                    ))}
                </div>
            ) : (
                !loading && query && <p className="no-results">No results found. Try a different search term.</p>
            )}

            <style jsx>{`
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }
                .page-title {
                    font-size: 2.5rem;
                    margin-bottom: 0.5rem;
                    color: var(--brown-900);
                }
                .subtitle {
                    font-size: 1.1rem;
                    color: var(--brown-600);
                    margin-bottom: 2rem;
                }
                .search-form {
                    display: flex;
                    gap: 1rem;
                    margin-bottom: 2rem;
                }
                .search-input {
                    flex: 1;
                    padding: 0.75rem 1rem;
                    font-size: 1rem;
                    border: 2px solid var(--brown-200);
                    border-radius: 8px;
                }
                .search-input:focus {
                    outline: none;
                    border-color: var(--brown-500);
                }
                .search-button {
                    padding: 0.75rem 2rem;
                    font-size: 1rem;
                    font-weight: 600;
                    background-color: var(--brown-700);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                }
                .search-button:hover:not(:disabled) {
                    background-color: var(--brown-800);
                }
                .search-button:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }
                .source-info {
                    margin-bottom: 1.5rem;
                    padding: 0.75rem;
                    background-color: var(--brown-50);
                    border-left: 4px solid var(--brown-500);
                    border-radius: 4px;
                }
                .loading-text {
                    text-align: center;
                    font-size: 1.1rem;
                    color: var(--brown-600);
                    padding: 3rem;
                }
                .no-results {
                    text-align: center;
                    font-size: 1.1rem;
                    color: var(--brown-600);
                    padding: 3rem;
                }
                .books-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                    gap: 2rem;
                }
                .book-card-link {
                    text-decoration: none;
                    color: inherit;
                    display: block;
                }
                .book-card {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                    transition: transform 0.2s;
                }
                .book-card:hover {
                    transform: translateY(-4px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }
                .book-cover {
                    width: 100%;
                    height: 350px;
                    object-fit: cover;
                }
                .book-cover-placeholder {
                    width: 100%;
                    height: 350px;
                    background: linear-gradient(135deg, var(--brown-200) 0%, var(--brown-300) 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: var(--brown-600);
                    font-weight: 600;
                }
                .book-info {
                    padding: 1rem;
                }
                .book-title {
                    font-size: 1rem;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                    color: var(--brown-900);
                    overflow: hidden;
                    text-overflow: ellipsis;
                    display: -webkit-box;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                    min-height: 2.4em;
                }
                .book-author {
                    font-size: 0.9rem;
                    color: var(--brown-600);
                    margin-bottom: 0.75rem;
                }
                .book-meta {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 0.5rem;
                }
                .meta-tag {
                    font-size: 0.75rem;
                    padding: 0.25rem 0.5rem;
                    background-color: var(--brown-100);
                    color: var(--brown-700);
                    border-radius: 4px;
                }
            `}</style>
        </div>
    );
}
