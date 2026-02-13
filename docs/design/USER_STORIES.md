# User Stories

## User Story 1: Sarah the Reader

### Scene 1: Landing Page
Sarah visits **BookWebsite** for the first time. She sees a clean landing page with a
**hero section** showing the site name and tagline, a row of **featured books**
(covers + titles), and a prominent **"Log In" / "Register"** button in the top-right navbar.

- **Page**: `/` (Landing / Home)
- **API**: `GET /books/featured`
- **Components**: Navbar (Login/Register buttons), Hero section, Featured Books grid

### Scene 2: Registration
Sarah clicks "Register". A **registration form** appears. She fills in her username,
email, password, and selects her role as **"Reader"**. She clicks Submit.

- **Page**: `/register`
- **API**: `POST /auth/register` with `roles: ["reader"]`
- **Components**: Registration form (username, email, password, role selector)

### Scene 3: Login
After registering, she's redirected to the **login page**. She enters her username and
password and clicks "Log In". The frontend receives a JWT token and stores it in localStorage.

- **Page**: `/login`
- **API**: `POST /auth/login` → returns `access_token`
- **Components**: Login form (username, password)

### Scene 4: Reader Dashboard (Home)
After logging in, Sarah lands on her **Reader Dashboard**. The navbar now shows her
username and a "Log Out" button. She sees:
- **Featured Books** section (alphabetical)
- **Search bar** at the top
- **"My Lists"** section (Favorites, In Progress, Finished)

- **Page**: `/dashboard`
- **API**: `GET /books/featured`, `GET /readers/{id}`
- **Components**: Navbar (username + Logout), Search bar, Featured Books grid, My Lists sidebar

### Scene 5: Searching for a Book
Sarah types "Harry" into the search bar. Results show matching books with their
**cover image**, **title**, and **author name**.

- **Page**: `/books/search?title=Harry`
- **API**: `GET /books/search?title=Harry`
- **Components**: Search results (book cards)

### Scene 6: Viewing a Book
Sarah clicks on a book. She sees the **cover image**, **title**, **author** (clickable),
**description**, and **chapter list**. She can add the book to her Favorites, In Progress,
or Finished lists.

- **Page**: `/books/{book_id}`
- **API**: `GET /books/{book_id}`, `POST /readers/{reader_id}/add-book`
- **Components**: Book detail card, "Add to List" buttons, Chapter list

### Scene 7: Browsing an Author
Sarah clicks the author's name. She sees their **profile picture**, **name**,
**biography**, and a grid of **all their books**.

- **Page**: `/authors/{author_id}`
- **API**: `GET /authors/{id}`, `GET /authors/{id}/books`
- **Components**: Author profile header, Author's Books grid

### Scene 8: Searching for Authors
Sarah searches for authors by name. Results show author cards with profile pictures and names.

- **Page**: `/authors/search?name=...`
- **API**: `GET /authors/search?name=...`
- **Components**: Author search results (author cards)

---

## User Story 2: Marcus the Author

### Scene 1–3: Same Registration & Login
Marcus registers with `roles: ["reader", "author"]`. His JWT contains both roles.

- **API**: `POST /auth/register` with `roles: ["reader", "author"]`

### Scene 4: Author Dashboard
Marcus has everything Sarah has, PLUS an **"Author Panel"** tab. This panel shows:
- **His profile** (name, biography, profile picture) with "Edit Profile" button
- **His books** with "Edit" and "Delete" buttons
- **"Create New Book"** button

- **Page**: `/dashboard` (Author Panel tab visible because `roles` includes `"author"`)
- **API**: `GET /authors/{id}`, `GET /authors/{id}/books`

### Scene 5: Editing His Profile
Marcus clicks "Edit Profile". A form appears pre-filled with his current info.

- **API**: `PUT /authors/{id}` (ownership enforced)

### Scene 6: Creating a New Book
Marcus clicks "Create New Book". He fills in title, content/chapters, description,
and cover image URL.

- **API**: `POST /books/` (requires author role)

### Scene 7: Editing a Book
Marcus fixes a typo in one of his books.

- **API**: `PUT /books/{id}` (ownership enforced)

### Scene 8: Deleting a Book
Marcus removes a draft.

- **API**: `DELETE /books/{id}` (ownership enforced)
