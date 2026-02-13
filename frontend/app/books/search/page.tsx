"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { searchBooks, Book } from "@/lib/api";
import BookGrid from "@/components/BookGrid";
import BookCard from "@/components/BookCard";

import { Suspense } from "react";

function SearchContent() {
    const searchParams = useSearchParams();
    const title = searchParams.get("title");
    const [books, setBooks] = useState<Book[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (title) {
            setLoading(true);
            searchBooks(title)
                .then((data) => {
                    setBooks(data.books || []);
                })
                .catch(console.error)
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, [title]);

    return (
        <div>
            <h1>Search Results for "{title}"</h1>
            {loading ? (
                <p>Searching...</p>
            ) : books.length > 0 ? (
                <BookGrid>
                    {books.map((book) => (
                        <BookCard key={book._id} book={book} />
                    ))}
                </BookGrid>
            ) : (
                <p>No books found matching your search.</p>
            )}
        </div>
    );
}

export default function SearchPage() {
    return (
        <Suspense fallback={<div>Loading search...</div>}>
            <SearchContent />
        </Suspense>
    );
}
