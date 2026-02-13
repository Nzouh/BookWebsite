import type { Metadata } from "next";
import "./globals.css";
import Navbar from "../components/Navbar";
import { AuthProvider } from "../lib/AuthContext";

export const metadata: Metadata = {
  title: "BookWebsite",
  description: "Discover and read your next favorite book.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <Navbar />
          <main className="container">
            {children}
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
