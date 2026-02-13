"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { login } from "@/lib/api";
import { useAuth } from "@/lib/AuthContext";

export default function LoginPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const router = useRouter();
    const { login: authLogin } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        try {
            // The login API returns { access_token: string, token_type: string }
            const data = await login({ username, password });
            authLogin(data.access_token);
        } catch (err: any) {
            setError(err.message || "Login failed");
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h1 className="title">Welcome Back</h1>
                <p className="subtitle">Sign in to continue reading</p>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button type="submit" className="btn btn-primary full-width">
                        Log In
                    </button>
                </form>

                <p className="footer-text">
                    Don't have an account? <Link href="/register" className="link">Register here</Link>
                </p>
            </div>

            <style jsx>{`
        .auth-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: calc(100vh - 200px); /* Adjust for navbar */
          padding: 2rem 0;
        }
        .auth-card {
          background-color: var(--white);
          padding: 2.5rem;
          border-radius: 8px;
          border: 1px solid var(--brown-100);
          width: 100%;
          max-width: 400px;
          box-shadow: 0 4px 12px rgba(62, 39, 35, 0.05);
        }
        .title {
          text-align: center;
          margin-bottom: 0.5rem;
        }
        .subtitle {
          text-align: center;
          color: var(--brown-500);
          margin-bottom: 2rem;
        }
        .error-message {
          background-color: #fee;
          color: var(--danger);
          padding: 0.75rem;
          border-radius: 4px;
          border: 1px solid #fcc;
          margin-bottom: 1.5rem;
          font-size: 0.875rem;
        }
        .form-group {
          margin-bottom: 1.5rem;
        }
        label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
          color: var(--brown-700);
        }
        input {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid var(--brown-100);
          border-radius: 4px;
          background-color: var(--cream-light);
        }
        input:focus {
          outline: none;
          border-color: var(--brown-500);
        }
        .full-width {
          width: 100%;
          padding: 0.75rem;
          font-size: 1rem;
        }
        .footer-text {
          text-align: center;
          margin-top: 1.5rem;
          font-size: 0.875rem;
          color: var(--brown-500);
        }
        .link {
          color: var(--brown-700);
          font-weight: 600;
          text-decoration: underline;
        }
        .link:hover {
          color: var(--accent);
        }
      `}</style>
        </div>
    );
}
