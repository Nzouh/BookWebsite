"use client";

import { useState } from "react";
import { useAuth } from "@/lib/AuthContext";
import ReaderLists from "@/components/ReaderLists";
import AuthorPanel from "@/components/AuthorPanel";
import BookGrid from "@/components/BookGrid";
import BookCard from "@/components/BookCard";
import { getFeaturedBooks, Book } from "@/lib/api";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Dashboard() {
    const { user, isAuthor, isAuthenticated } = useAuth();
    const router = useRouter();
    const [activeTab, setActiveTab] = useState("browse");
    const [featuredBooks, setFeaturedBooks] = useState<Book[]>([]);

    useEffect(() => {
        if (!isAuthenticated) {
            router.push("/login");
            return;
        }

        if (activeTab === "browse") {
            getFeaturedBooks().then(setFeaturedBooks).catch(console.error);
        }
    }, [isAuthenticated, activeTab, router]);

    if (!isAuthenticated) return null;

    return (
        <div className="dashboard">
            <h1 className="welcome">Welcome back, {user?.sub}</h1>

            <div className="tabs">
                <button
                    className={`tab ${activeTab === "browse" ? "active" : ""}`}
                    onClick={() => setActiveTab("browse")}
                >
                    Browse Books
                </button>
                <button
                    className={`tab ${activeTab === "lists" ? "active" : ""}`}
                    onClick={() => setActiveTab("lists")}
                >
                    My Lists
                </button>
                {isAuthor && (
                    <button
                        className={`tab ${activeTab === "author" ? "active" : ""}`}
                        onClick={() => setActiveTab("author")}
                    >
                        Author Panel
                    </button>
                )}
            </div>

            <div className="tab-content">
                {activeTab === "browse" && (
                    <div>
                        <h2>Featured Books</h2>
                        <BookGrid>
                            {featuredBooks.map(book => <BookCard key={book._id} book={book} />)}
                        </BookGrid>
                    </div>
                )}

                {activeTab === "lists" && <ReaderLists />}

                {activeTab === "author" && <AuthorPanel />}
            </div>

            <style jsx>{`
        .dashboard {
          padding-top: 2rem;
        }
        .welcome {
          margin-bottom: 2rem;
        }
        .tabs {
          display: flex;
          gap: 1rem;
          border-bottom: 1px solid var(--brown-100);
          margin-bottom: 2rem;
        }
        .tab {
          background: none;
          border: none;
          padding: 1rem 1.5rem;
          font-size: 1rem;
          color: var(--brown-500);
          border-bottom: 2px solid transparent;
        }
        .tab:hover {
          color: var(--brown-700);
        }
        .tab.active {
          color: var(--brown-900);
          border-bottom-color: var(--brown-900);
          font-weight: 600;
        }
        .tab-content {
          min-height: 400px;
        }
      `}</style>
        </div>
    );
}
