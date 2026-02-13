"use client";

import { useEffect, useState } from "react";
import { getAuthorBooks, getAuthor, Book, Author } from "@/lib/api";
import BookGrid from "@/components/BookGrid";
import BookCard from "@/components/BookCard";

export default function AuthorProfilePage({ params }: { params: { id: string } }) {
    const { id } = params;
    const [author, setAuthor] = useState<Author | null>(null);
    const [books, setBooks] = useState<Book[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const [authorData, booksData] = await Promise.all([
                    getAuthor(id),
                    getAuthorBooks(id)
                ]);
                setAuthor(authorData);
                setBooks(booksData.books);
            } catch (err) {
                console.error("Failed to fetch author data", err);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [id]);

    if (loading) return <div>Loading author profile...</div>;
    if (!author) return <div>Author not found.</div>;

    return (
        <div className="author-profile">
            <div className="profile-header">
                <div className="avatar">
                    <img src={author.profile_picture || "https://placehold.co/150x150?text=Author"} alt={author.name} />
                </div>
                <div className="details">
                    <h1>{author.name}</h1>
                    <p className="bio">{author.biography || "No biography available."}</p>
                </div>
            </div>

            <div className="books-section">
                <h2>Books by {author.name}</h2>
                {books.length > 0 ? (
                    <BookGrid>
                        {books.map(book => <BookCard key={book._id} book={book} />)}
                    </BookGrid>
                ) : (
                    <p>No books published yet.</p>
                )}
            </div>

            <style jsx>{`
        .author-profile {
          padding-top: 2rem;
        }
        .profile-header {
          display: flex;
          gap: 2rem;
          margin-bottom: 4rem;
          align-items: center;
          background-color: var(--white);
          padding: 2rem;
          border-radius: 8px;
          border: 1px solid var(--brown-100);
        }
        .avatar {
          width: 150px;
          height: 150px;
          border-radius: 50%;
          overflow: hidden;
          background-color: var(--brown-100);
          flex-shrink: 0;
        }
        .avatar img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .bio {
          font-size: 1.125rem;
          color: var(--brown-500);
          margin-top: 0.5rem;
          max-width: 600px;
        }
      `}</style>
        </div>
    );
}
