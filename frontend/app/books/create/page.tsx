"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createBook, Book, Chapter } from "@/lib/api";
import { useAuth } from "@/lib/AuthContext";

export default function CreateBookPage() {
    const { user, isAuthor } = useAuth();
    const router = useRouter();

    const [title, setTitle] = useState("");
    const [image, setImage] = useState("");
    const [biography, setBiography] = useState("");
    const [chapters, setChapters] = useState<Chapter[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [newChapterTitle, setNewChapterTitle] = useState("");
    const [newChapterContent, setNewChapterContent] = useState("");

    if (!isAuthor) {
        return <div className="error">You must be an author to view this page.</div>;
    }

    const handleAddChapter = () => {
        if (!newChapterTitle || !newChapterContent) {
            alert("Please provide both title and content for the chapter.");
            return;
        }
        const order = chapters.length + 1;
        setChapters([...chapters, { title: newChapterTitle, content: newChapterContent, order }]);
        setNewChapterTitle("");
        setNewChapterContent("");
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            if (!user?.sub) throw new Error("User not found");

            const bookData: Partial<Book> = {
                title,
                author: user.sub, // Assuming username is author name for simplicity, or we should fetch author profile name
                image,
                biography,
                chapters
            };

            await createBook(bookData);
            router.push("/dashboard"); // Redirect to dashboard to see the new book
        } catch (err: any) {
            setError(err.message || "Failed to create book");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="create-book-container">
            <h1>Publish a New Book</h1>
            {error && <div className="error-message">{error}</div>}

            <form onSubmit={handleSubmit} className="create-form">
                <div className="form-group">
                    <label>Title</label>
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        required
                    />
                </div>

                <div className="form-group">
                    <label>Cover Image URL</label>
                    <input
                        type="text"
                        value={image}
                        onChange={(e) => setImage(e.target.value)}
                        placeholder="https://example.com/cover.jpg"
                    />
                </div>

                <div className="form-group">
                    <label>Description (Biography)</label>
                    <textarea
                        value={biography}
                        onChange={(e) => setBiography(e.target.value)}
                        rows={4}
                    />
                </div>

                <div className="chapters-editor">
                    <h2>Chapters ({chapters.length})</h2>

                    <ul className="chapter-list">
                        {chapters.map((ch) => (
                            <li key={ch.order} className="chapter-item">
                                <strong>{ch.order}. {ch.title}</strong>
                            </li>
                        ))}
                    </ul>

                    <div className="new-chapter-form">
                        <h3>Add Chapter</h3>
                        <input
                            type="text"
                            placeholder="Chapter Title"
                            value={newChapterTitle}
                            onChange={(e) => setNewChapterTitle(e.target.value)}
                        />
                        <textarea
                            placeholder="Chapter Content..."
                            value={newChapterContent}
                            onChange={(e) => setNewChapterContent(e.target.value)}
                            rows={6}
                        />
                        <button type="button" onClick={handleAddChapter} className="btn btn-outline">
                            + Add Chapter
                        </button>
                    </div>
                </div>

                <div className="form-actions">
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? "Publishing..." : "Publish Book"}
                    </button>
                </div>
            </form>

            <style jsx>{`
        .create-book-container {
          max-width: 800px;
          margin: 2rem auto;
          background-color: var(--white);
          padding: 2rem;
          border-radius: 8px;
          border: 1px solid var(--brown-100);
        }
        h1 { margin-bottom: 2rem; }
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
        input, textarea {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid var(--brown-100);
          border-radius: 4px;
          background-color: var(--cream-light);
        }
        .chapters-editor {
          margin: 2rem 0;
          border-top: 1px solid var(--brown-100);
          padding-top: 2rem;
        }
        .chapter-list {
          margin-bottom: 2rem;
          list-style: none;
        }
        .chapter-item {
          padding: 0.5rem;
          border-bottom: 1px solid var(--brown-100);
        }
        .new-chapter-form {
          background-color: var(--cream-light);
          padding: 1.5rem;
          border-radius: 8px;
        }
        .new-chapter-form input, .new-chapter-form textarea {
          background-color: var(--white);
          margin-bottom: 1rem;
        }
        .error-message {
          color: var(--danger);
          margin-bottom: 1rem;
        }
      `}</style>
        </div>
    );
}
