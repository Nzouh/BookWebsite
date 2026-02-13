"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getBook, Book, addBookToList, getMyReaderProfile } from "@/lib/api";
import { useAuth } from "@/lib/AuthContext";

export default function BookDetailPage({ params }: { params: { id: string } }) {
    const { id } = params;
    const { isAuthenticated } = useAuth();
    const [book, setBook] = useState<Book | null>(null);
    const [loading, setLoading] = useState(true);
    const [readerId, setReaderId] = useState<string | null>(null);

    useEffect(() => {
        async function fetchData() {
            try {
                const bookData = await getBook(id);
                setBook(bookData);

                if (isAuthenticated) {
                    try {
                        const profile = await getMyReaderProfile();
                        setReaderId(profile._id);
                    } catch (e) {
                        console.error("Could not fetch reader ID", e);
                    }
                }
            } catch (err) {
                console.error("Failed to fetch book", err);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [id, isAuthenticated]);

    const handleAddToList = async (listName: string) => {
        if (!readerId) {
            alert("Please log in to add to lists.");
            return;
        }
        try {
            await addBookToList(readerId, id, listName);
            alert(`Added to ${listName}!`);
        } catch (err) {
            alert("Failed to add to list.");
        }
    };

    if (loading) return <div>Loading book details...</div>;
    if (!book) return <div>Book not found.</div>;

    return (
        <div className="book-detail">
            <div className="hero-section">
                <div className="cover-wrapper">
                    <img src={book.image || "https://placehold.co/300x450?text=Cover"} alt={book.title} />
                </div>
                <div className="info-wrapper">
                    <h1 className="title">{book.title}</h1>
                    <p className="author">by {book.author}</p>
                    <p className="bio">{book.biography || "No description available."}</p>

                    {isAuthenticated && (
                        <div className="actions">
                            <button onClick={() => handleAddToList("favorites")} className="btn btn-outline">♥ Favorites</button>
                            <button onClick={() => handleAddToList("in_progress")} className="btn btn-outline">📖 Reading</button>
                            <button onClick={() => handleAddToList("finished")} className="btn btn-outline">✓ Finished</button>
                        </div>
                    )}
                </div>
            </div>

            <div className="chapters-section">
                <h2>Chapters</h2>
                {book.chapters && book.chapters.length > 0 ? (
                    <ul className="chapter-list">
                        {book.chapters.map((chapter) => (
                            <li key={chapter.order} className="chapter-item">
                                <span className="chapter-title">
                                    {chapter.order}. {chapter.title}
                                </span>
                                <Link
                                    href={`/books/${id}/read/${chapter.order}`}
                                    className="btn btn-primary btn-sm"
                                >
                                    Read
                                </Link>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>No chapters available yet.</p>
                )}
            </div>

            <style jsx>{`
        .book-detail {
          padding-top: 2rem;
        }
        .hero-section {
          display: flex;
          gap: 3rem;
          margin-bottom: 4rem;
        }
        .cover-wrapper {
          flex: 0 0 300px;
        }
        .cover-wrapper img {
          width: 100%;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(62, 39, 35, 0.2);
        }
        .info-wrapper {
          flex: 1;
        }
        .title {
          font-size: 2.5rem;
          margin-bottom: 0.5rem;
        }
        .author {
          font-size: 1.25rem;
          color: var(--brown-500);
          margin-bottom: 2rem;
        }
        .bio {
          font-size: 1.125rem;
          line-height: 1.8;
          color: var(--brown-900);
          margin-bottom: 2rem;
        }
        .actions {
          display: flex;
          gap: 1rem;
        }
        .chapters-section {
          max-width: 800px;
        }
        .chapter-list {
          list-style: none;
          border: 1px solid var(--brown-100);
          border-radius: 8px;
          overflow: hidden;
        }
        .chapter-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem 1.5rem;
          border-bottom: 1px solid var(--brown-100);
          background-color: var(--white);
        }
        .chapter-item:last-child {
          border-bottom: none;
        }
        .chapter-item:hover {
          background-color: var(--cream-light);
        }
        .chapter-title {
          font-weight: 500;
        }
        .btn-sm {
          padding: 0.25rem 1rem;
          text-decoration: none;
          display: inline-block;
        }
      `}</style>
        </div>
    );
}
