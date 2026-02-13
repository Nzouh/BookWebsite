import Link from "next/link";
import { Book } from "../lib/api";

export default function BookCard({ book }: { book: Book }) {
    // Use a placeholder if no image is provided
    const imageUrl = book.image || "https://placehold.co/200x300?text=No+Cover";

    return (
        <Link href={`/books/${book._id}`} className="book-card">
            <div className="image-wrapper">
                <img src={imageUrl} alt={book.title} />
            </div>
            <div className="info">
                <h3 className="title">{book.title}</h3>
                <p className="author">{book.author}</p>
            </div>

            <style jsx>{`
        .book-card {
          display: block;
          background-color: var(--white);
          border-radius: 8px;
          overflow: hidden;
          transition: transform 0.2s, box-shadow 0.2s;
          height: 100%;
          border: 1px solid var(--brown-100);
        }
        .book-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 4px 12px rgba(62, 39, 35, 0.15);
        }
        .image-wrapper {
          width: 100%;
          aspect-ratio: 2/3;
          background-color: var(--cream);
          overflow: hidden;
        }
        .image-wrapper img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .info {
          padding: 1rem;
        }
        .title {
          font-size: 1rem;
          font-weight: 600;
          margin-bottom: 0.25rem;
          color: var(--brown-900);
          /* Truncate long titles */
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .author {
          font-size: 0.875rem;
          color: var(--brown-500);
        }
      `}</style>
        </Link>
    );
}
