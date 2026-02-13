"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { register, login } from "@/lib/api";
import { useAuth } from "@/lib/AuthContext";

export default function RegisterPage() {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isAuthor, setIsAuthor] = useState(false);
    const [error, setError] = useState("");
    const router = useRouter();
    const { login: authLogin } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        const roles = ["reader"];
        if (isAuthor) roles.push("author");

        try {
            // 1. Register
            await register({ username, email, password, roles });

            // 2. Auto-login on success
            const loginData = await login({ username, password });
            authLogin(loginData.access_token);
        } catch (err: any) {
            setError(err.message || "Registration failed");
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h1 className="title">Create an Account</h1>
                <p className="subtitle">Join our community of readers and authors</p>

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
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
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

                    <div className="form-group checkbox-group">
                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                checked={isAuthor}
                                onChange={(e) => setIsAuthor(e.target.checked)}
                            />
                            <span className="checkbox-text">I also want to publish books (Author Account)</span>
                        </label>
                    </div>

                    <button type="submit" className="btn btn-primary full-width">
                        Register
                    </button>
                </form>

                <p className="footer-text">
                    Already have an account? <Link href="/login" className="link">Log in here</Link>
                </p>
            </div>

            <style jsx>{`
        .auth-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: calc(100vh - 200px);
          padding: 2rem 0;
        }
        .auth-card {
          background-color: var(--white);
          padding: 2.5rem;
          border-radius: 8px;
          border: 1px solid var(--brown-100);
          width: 100%;
          max-width: 450px;
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
        input:not([type="checkbox"]) {
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
        .checkbox-group {
          margin-top: 1rem;
        }
        .checkbox-label {
          display: flex;
          align-items: center;
          cursor: pointer;
        }
        .checkbox-text {
          margin-left: 0.5rem;
          font-weight: 400;
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
