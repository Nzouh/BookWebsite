# 📚 BookWebsite

**BookWebsite** is a modern, full-stack platform for authors to publish and update their books continuously and for readers to enjoy a seamless, lightweight reading experience. The platform uses a "Netflix-style" tiered data loading approach to ensure fast browsing even with a large library.

> ⚠️ **Status**: This project is currently in active development.

---

## 🏗️ Architecture

- **Backend**: Built with [FastAPI](https://fastapi.tiangolo.com/) (Python), providing a high-performance asynchronous API.
- **Database**: [MongoDB](https://www.mongodb.com/) for flexible document storage of books, authors, and reader profiles.
- **Frontend**: Built with [Next.js 14](https://nextjs.org/) (React), [TypeScript](https://www.typescriptlang.org/), and Vanilla CSS for a clean, "book-like" aesthetic.
- **Infrastructure**: Fully containerized using **Docker** and **Docker Compose**.

---

## ✨ Key Features

- **Tiered Data Loading**: Browse books using "Card View" (titles/images only) for maximum speed. Full content is only loaded when you start reading.
- **Chapter System**: Books are organized into chapters, allowing for organized reading and efficient data retrieval.
- **Author Panel**: Dedicated space for authors to create books, manage biographies, and publish new chapters.
- **Reader Lists**: Readers can save books to their "Favorites", "Currently Reading", or "Finished" lists.
- **Cloud Seeding**: Includes a utility script to seed the database with real book data from the Open Library API.

---

## 🚀 Getting Started

### Prerequisites

- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (Must be installed and running)
- **Git**

### Installation & Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nzouh/BookWebsite.git
   cd BookWebsite
   ```

2. **Run the entire stack**:
   ```bash
   docker compose up --build
   ```
   This will spin up:
   - **MongoDB** on `localhost:27017`
   - **Backend API** on `localhost:8000`
   - **Frontend App** on `localhost:3000`

3. **Seed the database** (Optional):
   If you want to quickly populate the site with books:
   ```bash
   # Make sure you have python installed locally for the script
   pip install -r requirements.txt
   python scripts/seed_books.py
   ```

---

## 🔮 Future Roadmap: AI Reading Assistant

One of the most exciting upcoming features is the **Context-Aware AI Assistant**.

### The Concept
When reading a book, users often encounter complex terms or forget character details from previous chapters. You will be able to ask an AI assistant for help while reading.

### Key Logic: No Spoilers!
Using **Redis** for high-speed context lookup, the AI will be engineered with a "Knowledge Guard":
- **Spoiler Prevention**: The AI only "knows" what the reader has already read. If a reader asks a question about a character while on Chapter 2, the AI will not reveal information from Chapter 10.
- **Book-Specific Knowledge**: The AI helps with definitions but focuses on the story's internal logic and character relationships based on the current progress level.

---

## 📄 License
This project is open-source and available under the MIT License.
