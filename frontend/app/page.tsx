"use client";

import { useEffect, useState } from "react";
import BookCard from "@/components/BookCard";
import BookGrid from "@/components/BookGrid";
import { getFeaturedBooks, Book } from "@/lib/api";

export default function Home() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getFeaturedBooks()
      .then(setBooks)
      .catch((err) => console.error("Failed to fetch featured books", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">Discover Your Next Read</h1>
          <p className="hero-subtitle">Explore our collection of stories from authors around the world.</p>
        </div>
      </section>

      <section className="featured-section">
        <h2 className="section-title">Featured Books</h2>
        {loading ? (
          <p>Loading books...</p>
        ) : books.length > 0 ? (
          <BookGrid>
            {books.map((book) => (
              <BookCard key={book._id} book={book} />
            ))}
          </BookGrid>
        ) : (
          <p>No books found. Check back later!</p>
        )}
      </section>

      <style jsx>{`
        .hero {
          background-color: var(--brown-900);
          color: var(--white);
          padding: 4rem 2rem;
          border-radius: 8px;
          margin-top: 2rem;
          margin-bottom: 3rem;
          text-align: center;
          background-image: linear-gradient(rgba(62, 39, 35, 0.8), rgba(62, 39, 35, 0.9)), url('https://images.unsplash.com/photo-1507842217153-e2129e102bc5?auto=format&fit=crop&q=80');
          background-size: cover;
          background-position: center;
        }
        .hero-title {
          font-size: 3rem;
          color: var(--white);
          margin-bottom: 1rem;
        }
        .hero-subtitle {
          font-size: 1.25rem;
          color: var(--brown-100);
          max-width: 600px;
          margin: 0 auto;
        }
        .section-title {
          font-size: 2rem;
          margin-bottom: 1.5rem;
          border-bottom: 2px solid var(--brown-100);
          padding-bottom: 0.5rem;
        }
      `}</style>
    </div>
  );
}
