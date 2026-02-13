"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../lib/AuthContext";

export default function Navbar() {
    const { user, logout, isAuthenticated } = useAuth();
    const [searchTerm, setSearchTerm] = useState("");
    const router = useRouter();

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (searchTerm.trim()) {
            router.push(`/books/search?title=${encodeURIComponent(searchTerm)}`);
        }
    };

    return (
        <nav className="navbar">
            <div className="container nav-container">
                <Link href={isAuthenticated ? "/dashboard" : "/"} className="logo">
                    BookWebsite
                </Link>

                <form onSubmit={handleSearch} className="search-form">
                    <input
                        type="text"
                        placeholder="Search books..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="search-input"
                    />
                </form>

                <div className="nav-links">
                    {isAuthenticated ? (
                        <>
                            <span className="welcome-text">Hi, {user?.sub}</span>
                            <button onClick={logout} className="btn btn-outline">Log Out</button>
                        </>
                    ) : (
                        <>
                            <Link href="/login" className="btn btn-outline">Log In</Link>
                            <Link href="/register" className="btn btn-primary">Register</Link>
                        </>
                    )}
                </div>
            </div>

            <style jsx>{`
        .navbar {
          background-color: var(--white);
          border-bottom: 1px solid var(--brown-100);
          padding: 1rem 0;
          position: sticky;
          top: 0;
          z-index: 100;
        }
        .nav-container {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .logo {
          font-family: 'Playfair Display', serif;
          font-weight: 700;
          font-size: 1.5rem;
          color: var(--brown-900);
        }
        .search-form {
          flex: 1;
          max-width: 400px;
          margin: 0 2rem;
        }
        .search-input {
          width: 100%;
          padding: 0.5rem 1rem;
          border: 1px solid var(--brown-100);
          border-radius: 20px;
          background-color: var(--cream-light);
          color: var(--brown-900);
        }
        .search-input:focus {
          outline: none;
          border-color: var(--brown-500);
        }
        .nav-links {
          display: flex;
          gap: 1rem;
          align-items: center;
        }
        .welcome-text {
          font-weight: 500;
          color: var(--brown-700);
        }
      `}</style>
        </nav>
    );
}
