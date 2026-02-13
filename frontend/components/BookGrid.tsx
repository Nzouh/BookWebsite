import { ReactNode } from "react";

export default function BookGrid({ children }: { children: ReactNode }) {
    return (
        <div className="book-grid">
            {children}
            <style jsx>{`
        .book-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
          gap: 2rem;
          margin: 2rem 0;
        }
      `}</style>
        </div>
    );
}
