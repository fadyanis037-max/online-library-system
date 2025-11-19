import os
from typing import Optional

import requests
import streamlit as st


BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "1234")
# Admin username is fixed for simplicity
ADMIN_USERNAME = "admin"
# User username is fixed for simplicity
USER_USERNAME = "user"
# Easy default password for user mode (override with env var)
USER_PASSWORD = os.environ.get("USER_PASSWORD", "1234")


def _init_session():
    if "auth_username" not in st.session_state:
        st.session_state["auth_username"] = None
    if "auth_role" not in st.session_state:
        st.session_state["auth_role"] = "user"  # 'user' or 'admin'
    if "view_mode" not in st.session_state:
        st.session_state["view_mode"] = "user"  # UI mode; admin can switch


def fetch_books(query: Optional[str] = None):
    params = {"q": query} if query else {}
    r = requests.get(f"{BACKEND_URL}/api/books/", params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def create_book(payload: dict):
    r = requests.post(f"{BACKEND_URL}/api/books/", json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


def get_book(book_id: int):
    r = requests.get(f"{BACKEND_URL}/api/books/{book_id}", timeout=60)
    r.raise_for_status()
    return r.json()


def update_book(book_id: int, payload: dict):
    r = requests.put(f"{BACKEND_URL}/api/books/{book_id}", json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


def delete_book(book_id: int):
    r = requests.delete(f"{BACKEND_URL}/api/books/{book_id}", timeout=60)
    r.raise_for_status()
    return r.json()


def summarize_book(book_id: int, max_length: int = 130, min_length: int = 30):
    r = requests.post(
        f"{BACKEND_URL}/api/books/{book_id}/summarize",
        json={"max_length": max_length, "min_length": min_length},
        timeout=600,
    )
    r.raise_for_status()
    return r.json()


def recommend_books(book_id: int, top_k: int = 5):
    r = requests.get(
        f"{BACKEND_URL}/api/books/{book_id}/recommendations",
        params={"top_k": top_k},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def search_by_description(description: str, top_k: int = 5):
    r = requests.post(
        f"{BACKEND_URL}/api/books/search-by-description",
        json={"description": description, "top_k": top_k},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def main():
    st.set_page_config(page_title="AI-Powered Online Library", layout="wide")
    st.title("AI-Powered Online Library System")
    _init_session()

    # Sidebar controls
    with st.sidebar:
        # Auth & Mode
        st.header("Account & Mode")
        if st.session_state["auth_username"]:
            st.session_state["view_mode"] = "admin" if st.session_state.get("auth_role") == "admin" else "user"
            st.success(f"Signed in as {st.session_state['auth_username']} ({st.session_state['auth_role']})")
            if st.button("Sign out"):
                st.session_state["auth_username"] = None
                st.session_state["auth_role"] = "user"
                st.session_state["view_mode"] = "user"
                st.session_state.pop("ai_search_results", None)
                st.session_state.pop("ai_search_query", None)
                st.session_state.pop("selected_book_id", None)
                st.rerun()
        else:
            st.warning(
                "You are browsing as a guest. Sign in as a user for the full experience or as an admin for full control — enjoy your time!"
            )
            username = st.text_input("Username", value="", autocomplete="off")
            password = st.text_input("Password", type="password", autocomplete="new-password")
            if st.button("Sign in"):
                username_input = username.strip()
                if not username_input:
                    st.warning("Please enter a username")
                elif username_input == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state["auth_username"] = ADMIN_USERNAME
                    st.session_state["auth_role"] = "admin"
                    st.session_state["view_mode"] = "admin"
                    st.rerun()
                elif username_input == USER_USERNAME and password == USER_PASSWORD:
                    st.session_state["auth_username"] = USER_USERNAME
                    st.session_state["auth_role"] = "user"
                    st.session_state["view_mode"] = "user"
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        is_authenticated = bool(st.session_state.get("auth_username"))
        is_admin = st.session_state.get("view_mode") == "admin"

        st.header("Search & Actions")
        query = st.text_input("Search books (text search)")
        st.write("Backend:", BACKEND_URL)
        if st.button("Refresh List"):
            st.session_state["refresh_counter"] = st.session_state.get("refresh_counter", 0) + 1

        st.divider()
        st.subheader("AI-Powered Search")
        if not is_authenticated:
            st.info("Sign in to describe what you're looking for and get AI-powered results.")
        else:
            st.write("Describe what you're looking for:")
            user_description = st.text_area("Description", placeholder="e.g., A story about time travel and adventure...", key="ai_search_desc")
            if st.button("Find Relevant Books", key="ai_search_btn"):
                if user_description.strip():
                    with st.spinner("Finding relevant books using AI..."):
                        try:
                            result = search_by_description(user_description.strip())
                            st.session_state["ai_search_results"] = result.get("results", [])
                            st.session_state["ai_search_query"] = user_description.strip()
                            st.success(f"Found {len(result.get('results', []))} relevant book(s)")
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Please enter a description")

        if is_admin:
            st.divider()
            st.subheader("Admin: Add Book")
            with st.form("admin_add_book"):
                new_title = st.text_input("Title", key="admin_add_title")
                new_author = st.text_input("Author", key="admin_add_author")
                new_genre = st.text_input("Genre", key="admin_add_genre")
                new_description = st.text_area("Description", key="admin_add_description")
                new_content = st.text_area("Content (optional, used for better summaries)", key="admin_add_content")
                submitted = st.form_submit_button("Add Book", use_container_width=True)
                if submitted:
                    title_val = new_title.strip()
                    author_val = new_author.strip()
                    if not title_val or not author_val:
                        st.warning("Title and author are required.")
                    else:
                        payload = {
                            "title": title_val,
                            "author": author_val,
                            "genre": new_genre.strip() or None,
                            "description": new_description.strip() or None,
                            "content": new_content.strip() or None,
                        }
                        with st.spinner("Creating book..."):
                            try:
                                create_book(payload)
                                st.success(f"Book \"{title_val}\" added.")
                                st.session_state["refresh_counter"] = st.session_state.get("refresh_counter", 0) + 1
                                for key in (
                                    "admin_add_title",
                                    "admin_add_author",
                                    "admin_add_genre",
                                    "admin_add_description",
                                    "admin_add_content",
                                ):
                                    st.session_state[key] = ""
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to create book: {e}")


    # Main area
    # Show AI search results if available
    if not is_authenticated:
        st.session_state.pop("ai_search_results", None)
        st.session_state.pop("ai_search_query", None)
    if is_authenticated and st.session_state.get("ai_search_results"):
        st.subheader(f"🔍 AI Search Results for: \"{st.session_state.get('ai_search_query', '')}\"")
        ai_results = st.session_state.get("ai_search_results", [])
        if ai_results:
            for result in ai_results:
                with st.expander(f"📚 {result['title']} — {result['author']} (Relevance: {result.get('score', 0):.3f})"):
                    st.write(f"**Genre:** {result.get('genre') or 'Unknown'}")
                    st.write(f"**Description:** {result.get('description') or 'No description'}")
                    if st.button("View Details & Summary", key=f"view-{result['id']}"):
                        st.session_state["selected_book_id"] = result['id']
                        st.rerun()
        st.divider()

    # Fetch regular books
    try:
        books = fetch_books(query=query)
    except Exception as e:
        st.error(f"Failed to fetch books: {e}")
        return

    cols = st.columns([2, 3])
    with cols[0]:
        st.subheader("Books")
        if not books:
            st.info("No books found.")
        for b in books:
            with st.expander(f"{b['title']} - {b['author']} ({b.get('genre') or 'Unknown'})"):
                st.caption(b.get('created_at', ''))
                st.write(b.get('description') or "No description.")
                if st.button("View Details", key=f"select-{b['id']}"):
                    st.session_state["selected_book_id"] = b['id']
                    st.rerun()

    with cols[1]:
        st.subheader("Book Details & Summary")
        book_ids = [b['id'] for b in books]
        book_map = {b['id']: b for b in books}
        
        # Check if a book was selected from AI search
        selected_id = st.session_state.get("selected_book_id")
        if selected_id and selected_id not in book_ids:
            # If selected from AI search, fetch the book
            try:
                selected_book = get_book(selected_id)
                selected_id = selected_id
                st.session_state["selected_book_id"] = None  # Clear after use
            except:
                selected_id = None
        
        if not selected_id and books:
            selected_id = st.selectbox("Choose book", options=book_ids, format_func=lambda x: f"{book_map[x]['title']} — {book_map[x]['author']}") if books else None
        
        if selected_id:
            # Always fetch fresh details so we have updated description/content
            try:
                b = get_book(selected_id)
            except Exception as err:
                st.error(f"Book not found: {err}")
                return
            
            st.markdown(f"### {b['title']}")
            st.write(f"**Author:** {b['author']}")
            st.write(f"**Genre:** {b.get('genre') or 'Unknown'}")
            st.write(f"**Description:** {b.get('description') or 'No description'}")

            content_key = f"show_content_{selected_id}"
            if not is_authenticated:
                st.info("Sign in to view the book's full content.")
            elif b.get("content"):
                label = "Hide Content" if st.session_state.get(content_key) else "View Content"
                if st.button(label, key=f"detail-content-{selected_id}"):
                    st.session_state[content_key] = not st.session_state.get(content_key, False)
                if st.session_state.get(content_key):
                    st.markdown("### Full Content")
                    st.write(b.get("content"))
            else:
                st.info("No content available for this book.")

            action_cols = st.columns(3 if is_admin else 2)
            with action_cols[0]:
                if st.button("Summarize", key=f"detail-sum-{selected_id}", disabled=not is_authenticated):
                    with st.spinner("Summarizing with BART..."):
                        try:
                            res = summarize_book(selected_id)
                            st.session_state[f"summary-{selected_id}"] = res.get('summary')
                            st.success("Summary ready")
                        except Exception as e:
                            st.error(f"Failed to summarize: {e}")
            with action_cols[1]:
                if st.button("Recommend", key=f"detail-rec-{selected_id}", disabled=not is_authenticated):
                    with st.spinner("Finding similar books..."):
                        try:
                            res = recommend_books(selected_id)
                            st.session_state[f"recs-{selected_id}"] = res.get('recommendations', [])
                            st.success("Recommendations ready")
                        except Exception as e:
                            st.error(f"Failed to recommend: {e}")
            if is_admin:
                with action_cols[2]:
                    if st.button("Delete Book", key=f"detail-del-{selected_id}"):
                        try:
                            delete_book(selected_id)
                            st.warning("Book deleted")
                            st.session_state["refresh_counter"] = st.session_state.get("refresh_counter", 0) + 1
                            st.session_state["selected_book_id"] = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete: {e}")
            
            # Auto-summarize when book is selected
            auto_summary_key = f"auto_summary_{selected_id}"
            if (
                auto_summary_key not in st.session_state
                and st.session_state.get("auto_summarize_on_select")
                and is_authenticated
            ):
                with st.spinner("Generating summary with AI..."):
                    try:
                        res = summarize_book(selected_id)
                        st.session_state[auto_summary_key] = res.get('summary')
                    except Exception as e:
                        st.session_state[auto_summary_key] = None
                        st.error(f"Failed to generate summary: {e}")
            
            if st.session_state.get(auto_summary_key):
                st.markdown("### 📝 AI-Generated Summary")
                st.info(st.session_state[auto_summary_key])

            if is_authenticated:
                manual_summary = st.session_state.get(f"summary-{selected_id}")
                if manual_summary:
                    st.markdown("### Summary")
                    st.write(manual_summary)

                recs = st.session_state.get(f"recs-{selected_id}")
                if recs:
                    st.markdown("### Recommendations")
                    for r in recs:
                        st.write(f"{r['title']} - {r['author']} ({r.get('genre') or 'Unknown'})  [score: {r['score']:.3f}]")


if __name__ == '__main__':
    main()


