"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getChapter, Chapter } from "@/lib/api";

export default function ChapterReaderPage({ params }: { params: { id: string, chapter: string } }) {
    const { id, chapter: chapterOrderStr } = params;
    const chapterOrder = parseInt(chapterOrderStr, 10);
    const [chapter, setChapter] = useState<Chapter | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function fetchData() {
            try {
                const data = await getChapter(id, chapterOrder);
                setChapter(data);
            } catch (err) {
                console.error("Failed to load chapter", err);
                setError("Chapter not found.");
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [id, chapterOrder]);

    if (loading) return <div>Loading chapter...</div>;
    if (error) return <div className="error">{error}</div>;
    if (!chapter) return <div>Chapter unavailable.</div>;

    return (
        <div className="reader-container">
            <div className="reader-nav">
                <Link href={`/books/${id}`} className="back-link">
                    ← Back to Book
                </Link>
            </div>

            <article className="chapter-content">
                <h1 className="chapter-title">{chapter.title}</h1>
                <div className="text-body">
                    {chapter.content?.split('\n').map((paragraph, idx) => (
                        <p key={idx}>{paragraph}</p>
                    ))}
                </div>
            </article>

            <div className="chapter-controls">
                <Link
                    href={`/books/${id}/read/${chapterOrder - 1}`}
                    className={`btn btn-outline ${chapterOrder <= 1 ? "disabled" : ""}`}
                    aria-disabled={chapterOrder <= 1}
                    onClick={(e) => chapterOrder <= 1 && e.preventDefault()}
                >
                    Previous Chapter
                </Link>
                <Link
                    href={`/books/${id}/read/${chapterOrder + 1}`}
                    className="btn btn-primary"
                >
                    Next Chapter
                </Link>
            </div>

            <style jsx>{`
        .reader-container {
          max-width: 800px;
          margin: 0 auto;
          padding: 2rem 0;
        }
        .reader-nav {
          margin-bottom: 2rem;
        }
        .back-link {
          color: var(--brown-500);
          font-weight: 500;
        }
        .back-link:hover {
          color: var(--brown-900);
          text-decoration: underline;
        }
        .chapter-content {
          background-color: var(--white);
          padding: 4rem;
          border-radius: 2px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.05);
          margin-bottom: 3rem;
        }
        .chapter-title {
          text-align: center;
          margin-bottom: 3rem;
          font-size: 2.5rem;
        }
        .text-body {
          font-size: 1.25rem;
          line-height: 1.8;
          color: var(--brown-900);
          font-family: 'Georgia', serif; /* Use serif for long reading */
        }
        .text-body p {
          margin-bottom: 1.5rem;
        }
        .chapter-controls {
          display: flex;
          justify-content: space-between;
          padding-top: 2rem;
          border-top: 1px solid var(--brown-100);
        }
        .disabled {
          opacity: 0.5;
          cursor: not-allowed;
          pointer-events: none;
        }
      `}</style>
        </div>
    );
}
