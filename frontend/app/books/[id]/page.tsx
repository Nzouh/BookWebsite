"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { getBook, Book, addBookToList, getMyReaderProfile, downloadBook } from "@/lib/api";
import { useAuth } from "@/lib/AuthContext";

export default function BookDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { isAuthenticated } = useAuth();
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);
  const [readerId, setReaderId] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);
  const [downloadStatus, setDownloadStatus] = useState("");

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

  const handleDownload = async () => {
    if (!isAuthenticated) {
      alert("Please log in to download books.");
      return;
    }
    setDownloading(true);
    setDownloadStatus("Queuing download...");
    try {
      const result = await downloadBook(id);
      if (result.status === "already_ready") {
        setDownloadStatus("Book is already ready to read!");
      } else {
        setDownloadStatus("Download queued! Check back soon for chapters.");
      }
    } catch (err: any) {
      setDownloadStatus(err.message || "Download failed");
    } finally {
      setDownloading(false);
    }
  };

  if (loading) return <div>Loading book details...</div>;
  if (!book) return <div>Book not found.</div>;

  const coverUrl = book.image || book.cover_url || "https://placehold.co/300x450?text=Cover";
  const description = book.biography || book.description || "No description available.";
  const isImported = book.status === "imported";
  const isReady = book.status === "ready";
  const isProcessing = book.status === "processing";
  const hasChapters = book.chapters && book.chapters.length > 0;

  return (
    <div className="book-detail">
      <div className="hero-section">
        <div className="cover-wrapper">
          <img src={coverUrl} alt={book.title} />
        </div>
        <div className="info-wrapper">
          <h1 className="title">{book.title}</h1>
          <p className="author">by {book.author}</p>

          {book.source === "external" && (
            <div className="source-badge">
              <span>📥 Imported from Anna&apos;s Archive</span>
            </div>
          )}

          <p className="bio">{description}</p>

          <div className="actions">
            {/* Download button for imported but not-yet-downloaded books */}
            {isImported && (
              <button
                onClick={handleDownload}
                disabled={downloading}
                className="btn btn-download"
              >
                {downloading ? "⏳ Processing..." : "⬇️ Download & Read"}
              </button>
            )}

            {isProcessing && (
              <div className="status-processing">
                <span className="pulse">⏳</span> Downloading... check back soon
              </div>
            )}

            {isAuthenticated && (
              <>
                <button onClick={() => handleAddToList("favorites")} className="btn btn-outline">♥ Favorites</button>
                <button onClick={() => handleAddToList("in_progress")} className="btn btn-outline">📖 Reading</button>
                <button onClick={() => handleAddToList("finished")} className="btn btn-outline">✓ Finished</button>
              </>
            )}
          </div>

          {downloadStatus && (
            <p className="download-feedback">{downloadStatus}</p>
          )}
        </div>
      </div>

      <div className="chapters-section">
        <h2>Chapters</h2>
        {hasChapters ? (
          <ul className="chapter-list">
            {book.chapters!.map((chapter) => (
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
        ) : isImported ? (
          <div className="no-chapters-hint">
            <p>📥 Download this book to unlock chapters for reading.</p>
          </div>
        ) : isProcessing ? (
          <p>Chapters will appear once the download completes.</p>
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
          margin-bottom: 1rem;
        }
        .source-badge {
          display: inline-block;
          padding: 0.3rem 0.75rem;
          background: var(--brown-50, #faf5f0);
          border: 1px solid var(--brown-200);
          border-radius: 20px;
          font-size: 0.8rem;
          color: var(--brown-600);
          margin-bottom: 1rem;
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
          flex-wrap: wrap;
          align-items: center;
        }
        .btn-download {
          padding: 0.75rem 1.5rem;
          font-size: 1rem;
          font-weight: 600;
          background: linear-gradient(135deg, var(--brown-700), var(--brown-800));
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }
        .btn-download:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(62, 39, 35, 0.3);
        }
        .btn-download:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .status-processing {
          padding: 0.5rem 1rem;
          background: var(--brown-50, #faf5f0);
          border-radius: 8px;
          font-size: 0.9rem;
          color: var(--brown-600);
        }
        .pulse {
          display: inline-block;
          animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
        .download-feedback {
          margin-top: 1rem;
          padding: 0.75rem;
          background: var(--brown-50, #faf5f0);
          border-left: 3px solid var(--brown-500);
          border-radius: 4px;
          font-size: 0.9rem;
          color: var(--brown-700);
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
        .no-chapters-hint {
          padding: 2rem;
          background: var(--cream-light, #fefaf5);
          border-radius: 8px;
          text-align: center;
          color: var(--brown-600);
        }
        @media (max-width: 768px) {
          .hero-section {
            flex-direction: column;
            gap: 1.5rem;
          }
          .cover-wrapper {
            flex: none;
            max-width: 250px;
            margin: 0 auto;
          }
        }
      `}</style>
    </div>
  );
}
