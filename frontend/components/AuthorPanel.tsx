"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getMyAuthorProfile, getAuthorBooks, Book, Author, deleteBook } from "@/lib/api";

export default function AuthorPanel() {
  const [author, setAuthor] = useState<Author | null>(null);
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchData() {
      try {
        const profile = await getMyAuthorProfile();
        setAuthor(profile);

        if (profile) {
          const { books } = await getAuthorBooks(profile._id);
          setBooks(books);
        }
      } catch (err) {
        console.error("Failed to load author profile", err);
        setError("Could not load author details.");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const handleDeleteBook = async (id: string) => {
    if (!confirm("Are you sure you want to delete this book? This cannot be undone.")) return;
    try {
      await deleteBook(id);
      setBooks(books.filter(b => b._id !== id));
    } catch (err) {
      alert("Failed to delete book");
    }
  };

  if (loading) return <div>Loading author panel...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!author) return <div>Author profile not found.</div>;

  return (
    <div className="author-panel">
      <div className="panel-header">
        <div className="profile-info">
          <div className="profile-pic">
            <img src={author.profile_picture || "https://placehold.co/100x100?text=Author"} alt={author.name} />
          </div>
          <div>
            <h2>{author.name}</h2>
            <p className="bio">{author.biography || "No biography yet."}</p>
          </div>
        </div>
        <button className="btn btn-outline" disabled>Edit Profile (Coming Soon)</button>
      </div>

      <div className="books-section">
        <div className="section-header">
          <h3>My Books</h3>
          <Link href="/books/create" className="btn btn-primary">+ Create New Book</Link>
        </div>

        {books.length === 0 ? (
          <p>You haven't published any books yet.</p>
        ) : (
          <div className="books-list">
            {books.map(book => (
              <div key={book._id} className="book-item">
                <div className="book-info">
                  <img src={book.image || "https://placehold.co/50x75?text=Cover"} alt={book.title} className="tiny-cover" />
                  <span className="book-title">{book.title}</span>
                </div>
                <div className="actions">
                  <Link href={`/books/${book._id}`} className="btn btn-outline btn-sm">View</Link>
                  <button className="btn btn-outline btn-sm" disabled>Edit</button>
                  <button onClick={() => handleDeleteBook(book._id)} className="btn btn-danger btn-sm">Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <style jsx>{`
        .author-panel {
          background-color: var(--white);
          padding: 2rem;
          border-radius: 8px;
          border: 1px solid var(--brown-100);
        }
        .panel-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 3rem;
          border-bottom: 1px solid var(--brown-100);
          padding-bottom: 2rem;
        }
        .profile-info {
          display: flex;
          gap: 1.5rem;
          align-items: center;
        }
        .profile-pic {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          overflow: hidden;
          background-color: var(--brown-100);
        }
        .profile-pic img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .bio {
          color: var(--brown-500);
          max-width: 500px;
          margin-top: 0.5rem;
        }
        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        .books-list {
          border: 1px solid var(--brown-100);
          border-radius: 4px;
        }
        .book-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border-bottom: 1px solid var(--brown-100);
        }
        .book-item:last-child {
          border-bottom: none;
        }
        .book-info {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        .tiny-cover {
          width: 40px;
          height: 60px;
          object-fit: cover;
          border-radius: 2px;
        }
        .book-title {
          font-weight: 500;
        }
        .actions {
          display: flex;
          gap: 0.5rem;
        }
        .btn-sm {
          padding: 0.25rem 0.75rem;
          font-size: 0.875rem;
        }
      `}</style>
    </div>
  );
}
