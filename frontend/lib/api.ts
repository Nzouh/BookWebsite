// Use env variable or fallback to current host:8000 for remote deployment
const API_URL = typeof window !== 'undefined'
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : "http://localhost:8000";

// --- Types ---

export interface Book {
    _id: string;
    title: string;
    author: string;
    image?: string;
    biography?: string;
    chapters?: Chapter[];
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
    // Returns { access_token: string, token_type: string }
    // Note: Standard login usually doesn't need auth header, but fetchWithAuth is fine here as it just adds if present
    // However, simpler to use fetch directly to avoid sending old token if any
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

// Books
export async function getFeaturedBooks(): Promise<Book[]> {
    return fetchWithAuth("/books/featured");
}

export async function searchBooks(title: string): Promise<{ result: string, books: Book[] }> {
    return fetchWithAuth(`/books/search?title=${encodeURIComponent(title)}`);
}

export async function getBook(id: string): Promise<Book> {
    return fetchWithAuth(`/books/${id}`);
}

export async function getBooksBatch(ids: string[]): Promise<Book[]> {
    if (!ids.length) return [];
    // FastAPI expects repeated query params: ?ids=1&ids=2
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
    // Assuming the user ID matches the username for now as per backend logic
    // But wait, the backend `get_reader` takes an _id (ObjectId) OR user_id?
    // Let's check crud/readers.py. get_reader takes _id (ObjectId).
    // But wait, get_reader_by_user_id exists.
    // The frontend needs to know how to get the reader profile.
    // Currently, the backend doesn't have an endpoint "get my reader profile".
    // The frontend has the username from the token.
    // We added `get_reader_by_user_id` in CRUD but did we expose an endpoint for it?
    // Checking api/readers.py... No. It has `get_reader(_id)` and `list_readers`.
    // Wait, `get_reader_by_user_id` was added to CRUD, but is it used?
    // Ah, I missed adding an endpoint to get the CURRENT user's reader profile.
    // For now, I'll add a TODO to fix this in the backend or I'll implement a workaround if possible.
    // Actually, I can use the `list_readers` and filter, but that's bad.
    // I should probably add an endpoint `GET /readers/me` or similar.
    // I'll proceed with `get_reader` taking an ID for now, and note to fix the backend.
    return fetchWithAuth(`/readers/${id}`);
}

export async function addBookToList(readerId: string, bookId: string, listName: string) {
    return fetchWithAuth(`/readers/${readerId}/add-book?book_id=${bookId}&list_name=${listName}`, {
        method: "POST"
    });
}
