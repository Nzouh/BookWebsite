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
      router.push(`/books/search?q=${encodeURIComponent(searchTerm)}`);
    }
  };

  return (
    <nav className="navbar">
      <div className="container nav-container">
        <Link href={isAuthenticated ? "/dashboard" : "/"} className="logo-container">
          <img src="/logo.png" alt="Mascot" className="nav-logo" />
          <span className="logo-text">BookWebsite</span>
        </Link>

        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Search books, authors, topics..."
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
        .logo-container {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          text-decoration: none;
          transition: transform 0.2s ease;
        }
        .logo-container:hover {
          transform: scale(1.02);
        }
        .nav-logo {
          width: 60px;
          height: 60px;
          object-fit: contain;
          position: relative;
          top: 10px;
          transition: transform 0.2s ease;
        }
        .logo-container:hover .nav-logo {
          transform: scale(1.1);
          cursor: pointer;
        }
        .logo-text {
          font-family: 'Playfair Display', serif;
          font-weight: 700;
          font-size: 1.5rem;
          color: var(--brown-900);
          position: relative;
          top: -10px;
        }
        .search-form {
          flex: 1;
          max-width: 450px;
          margin: 0 2rem;
        }
        .search-input {
          width: 100%;
          padding: 0.6rem 1.25rem;
          border: 2px solid var(--brown-100);
          border-radius: 24px;
          background-color: var(--cream-light);
          color: var(--brown-900);
          font-size: 0.95rem;
          transition: border-color 0.2s, box-shadow 0.2s;
        }
        .search-input:focus {
          outline: none;
          border-color: var(--brown-400);
          box-shadow: 0 0 0 3px rgba(141, 110, 99, 0.15);
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
