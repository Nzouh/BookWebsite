"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { searchAuthors, Author } from "@/lib/api";
import Link from "next/link";

import { Suspense } from "react";

function AuthorSearchContent() {
    const searchParams = useSearchParams();
    const name = searchParams.get("name");
    const [authors, setAuthors] = useState<Author[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (name) {
            setLoading(true);
            searchAuthors(name)
                .then((data) => {
                    setAuthors(data.authors || []);
                })
                .catch(console.error)
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, [name]);

    return (
        <div>
            <h1>Author Search Results for "{name}"</h1>
            {loading ? (
                <p>Searching...</p>
            ) : authors.length > 0 ? (
                <div className="author-grid">
                    {authors.map((author) => (
                        <Link key={author._id} href={`/authors/${author._id}`} className="author-card">
                            <div className="avatar">
                                <img src={author.profile_picture || "https://placehold.co/80x80?text=A"} alt={author.name} />
                            </div>
                            <h3>{author.name}</h3>
                        </Link>
                    ))}
                </div>
            ) : (
                <p>No authors found matching your search.</p>
            )}

            <style jsx>{`
        .author-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1.5rem;
          margin-top: 2rem;
        }
        .author-card {
          display: flex;
          flex-direction: column;
          align-items: center;
          background-color: var(--white);
          padding: 2rem;
          border-radius: 8px;
          border: 1px solid var(--brown-100);
          transition: transform 0.2s;
        }
        .author-card:hover {
          transform: translateY(-4px);
          border-color: var(--brown-300);
        }
        .avatar {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          overflow: hidden;
          margin-bottom: 1rem;
          background-color: var(--brown-100);
        }
        .avatar img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        h3 {
          font-size: 1.125rem;
          text-align: center;
          color: var(--brown-900);
        }
      `}</style>
        </div>
    );
}

export default function AuthorSearchPage() {
    return (
        <Suspense fallback={<div>Loading search...</div>}>
            <AuthorSearchContent />
        </Suspense>
    );
}
