const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined'
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : "http://localhost:8000");

// --- Types ---

export interface Book {
    _id: string;
    title: string;
    author: string;
    image?: string;
    biography?: string;
    description?: string;
    chapters?: Chapter[];
    md5?: string;
    source?: string;       // "internal" | "external"
    status?: string;       // "imported" | "processing" | "ready" | "error"
    format?: string;
    size?: string;
    language?: string;
    publisher?: string;
    year?: string;
    isbn?: string;
    cover_url?: string;
}

export interface ExternalBook {
    title: string;
    authors: string;
    format: string;
    size: string;
    cover_url: string;
    hash: string;
    year: string;
    language: string;
    url: string;
}

export interface Chapter {
    title: string;
    content?: string;
    order: number;
}

export interface Author {
    _id: string;
    name: string;
    biography?: string;
    book_list: string[];
    profile_picture?: string;
    user_id?: string;
}

export interface Reader {
    _id: string;
    name: string;
    favorites: string[];
    in_progress: string[];
    finished: string[];
    user_id?: string;
}

// --- Helper wrapper for fetch calls ---

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
    const token = localStorage.getItem("token");
    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    } as HeadersInit;

    if (token) {
        (headers as any)["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Request failed: ${response.status}`);
    }

    return response.json();
}

// --- API Functions ---

// Auth
export async function register(data: any) {
    return fetchWithAuth("/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
    });
}

export async function login(data: any) {
    const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams(data),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Login failed");
    }
    return response.json();
}

// Books — Discovery & Search
export async function getFeaturedBooks(): Promise<Book[]> {
    return fetchWithAuth("/books/featured");
}

export async function searchBooks(query: string): Promise<{ local: Book[], external: ExternalBook[] }> {
    return fetchWithAuth(`/books/search?q=${encodeURIComponent(query)}`);
}

export async function externalSearchBooks(query: string): Promise<{ books: any[], source: string }> {
    return fetchWithAuth(`/books/external-search?query=${encodeURIComponent(query)}`);
}

export async function getExternalBookDetails(md5: string): Promise<{ book: any, source: string, local_id: string | null }> {
    return fetchWithAuth(`/books/external/${md5}`);
}

export async function importBook(md5: string): Promise<{ id: string, status: string }> {
    return fetchWithAuth(`/books/import/${md5}`, {
        method: "POST",
    });
}

export async function downloadBook(bookId: string): Promise<{ job_id?: string, status: string }> {
    return fetchWithAuth(`/books/${bookId}/download`, {
        method: "POST",
    });
}

// Books — CRUD
export async function getBook(id: string): Promise<Book> {
    return fetchWithAuth(`/books/${id}`);
}

export async function getBooksBatch(ids: string[]): Promise<Book[]> {
    if (!ids.length) return [];
    const query = ids.map(id => `ids=${id}`).join("&");
    return fetchWithAuth(`/books/batch?${query}`);
}

export async function getChapter(bookId: string, order: number): Promise<Chapter> {
    return fetchWithAuth(`/books/${bookId}/chapters/${order}`);
}

export async function createBook(bookData: Partial<Book>) {
    return fetchWithAuth("/books/", {
        method: "POST",
        body: JSON.stringify(bookData),
    });
}

export async function updateBook(id: string, bookData: Partial<Book>) {
    return fetchWithAuth(`/books/${id}`, {
        method: "PUT",
        body: JSON.stringify(bookData),
    });
}

export async function deleteBook(id: string) {
    return fetchWithAuth(`/books/${id}`, {
        method: "DELETE",
    });
}

// Authors
export async function getAuthor(id: string): Promise<Author> {
    return fetchWithAuth(`/authors/${id}`);
}

export async function getMyAuthorProfile(): Promise<Author> {
    return fetchWithAuth("/authors/me");
}

export async function getAuthorBooks(id: string): Promise<{ books: Book[], author: string }> {
    return fetchWithAuth(`/authors/${id}/books`);
}

export async function updateAuthor(id: string, data: Partial<Author>) {
    return fetchWithAuth(`/authors/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
}

export async function searchAuthors(name: string): Promise<{ result: string, authors: Author[] }> {
    return fetchWithAuth(`/authors/search?name=${encodeURIComponent(name)}`);
}

// Readers
export async function getMyReaderProfile(): Promise<Reader> {
    return fetchWithAuth("/readers/me");
}

export async function getReader(id: string): Promise<Reader> {
    return fetchWithAuth(`/readers/${id}`);
}

export async function addBookToList(readerId: string, bookId: string, listName: string) {
    return fetchWithAuth(`/readers/${readerId}/add-book?book_id=${bookId}&list_name=${listName}`, {
        method: "POST"
    });
}
