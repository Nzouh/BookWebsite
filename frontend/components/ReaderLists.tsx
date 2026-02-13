"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getMyReaderProfile, getBooksBatch, Book, Reader } from "@/lib/api";
import BookCard from "@/components/BookCard";
import BookGrid from "@/components/BookGrid";

export default function ReaderLists() {
    const [lists, setLists] = useState<{
        favorites: Book[];
        in_progress: Book[];
        finished: Book[];
    }>({ favorites: [], in_progress: [], finished: [] });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function fetchData() {
            try {
                const profile = await getMyReaderProfile();

                // Collect all unique book IDs from all lists
                const allIds = new Set([
                    ...profile.favorites,
                    ...profile.in_progress,
                    ...profile.finished
                ]);

                if (allIds.size === 0) {
                    setLoading(false);
                    return;
                }

                // Fetch book details for all IDs in one batch
                const books = await getBooksBatch(Array.from(allIds));
                const bookMap = new Map(books.map(b => [b._id, b]));

                // Map back to lists
                setLists({
                    favorites: profile.favorites.map(id => bookMap.get(id)).filter((b): b is Book => !!b),
                    in_progress: profile.in_progress.map(id => bookMap.get(id)).filter((b): b is Book => !!b),
                    finished: profile.finished.map(id => bookMap.get(id)).filter((b): b is Book => !!b),
                });
            } catch (err) {
                console.error("Failed to load reader lists", err);
                setError("Could not load your lists.");
            } finally {
                setLoading(false);
            }
        }

        fetchData();
    }, []);

    if (loading) return <div>Loading your library...</div>;
    if (error) return <div className="error">{error}</div>;

    const hasBooks = lists.favorites.length > 0 || lists.in_progress.length > 0 || lists.finished.length > 0;

    if (!hasBooks) {
        return (
            <div className="empty-state">
                <p>You haven't added any books to your lists yet.</p>
                <Link href="/" className="btn btn-primary">Browse Books</Link>
                <style jsx>{`
          .empty-state {
            text-align: center;
            padding: 3rem;
            background-color: var(--white);
            border-radius: 8px;
            border: 1px solid var(--brown-100);
          }
          p { margin-bottom: 1rem; color: var(--brown-500); }
        `}</style>
            </div>
        );
    }

    return (
        <div className="lists-container">
            {lists.in_progress.length > 0 && (
                <section>
                    <h3>Currently Reading</h3>
                    <BookGrid>
                        {lists.in_progress.map(book => <BookCard key={book._id} book={book} />)}
                    </BookGrid>
                </section>
            )}

            {lists.favorites.length > 0 && (
                <section>
                    <h3>Favorites</h3>
                    <BookGrid>
                        {lists.favorites.map(book => <BookCard key={book._id} book={book} />)}
                    </BookGrid>
                </section>
            )}

            {lists.finished.length > 0 && (
                <section>
                    <h3>Finished</h3>
                    <BookGrid>
                        {lists.finished.map(book => <BookCard key={book._id} book={book} />)}
                    </BookGrid>
                </section>
            )}

            <style jsx>{`
        .lists-container {
          display: flex;
          flex-direction: column;
          gap: 3rem;
        }
        section h3 {
          border-bottom: 2px solid var(--brown-100);
          padding-bottom: 0.5rem;
          margin-bottom: 1.5rem;
        }
        .error { color: var(--danger); }
      `}</style>
        </div>
    );
}
