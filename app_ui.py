import os
from typing import Optional

import requests
import streamlit as st


BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000")


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


def main():
    st.set_page_config(page_title="AI-Powered Online Library", layout="wide")
    st.title("AI-Powered Online Library System")

    # Sidebar controls
    with st.sidebar:
        st.header("Search & Actions")
        query = st.text_input("Search books")
        st.write("Backend:", BACKEND_URL)
        if st.button("Refresh List"):
            st.session_state["refresh_counter"] = st.session_state.get("refresh_counter", 0) + 1

        st.divider()
        st.subheader("Add a New Book")
        with st.form("new_book_form"):
            title = st.text_input("Title")
            author = st.text_input("Author")
            genre = st.text_input("Genre")
            description = st.text_area("Description")
            content = st.text_area("Content (optional)")
            submitted = st.form_submit_button("Create Book")
            if submitted:
                try:
                    create_book({"title": title, "author": author, "genre": genre, "description": description, "content": content})
                    st.success("Book created")
                    st.session_state["refresh_counter"] = st.session_state.get("refresh_counter", 0) + 1
                except Exception as e:
                    st.error(f"Error creating book: {e}")

    # Main area
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
            with st.expander(f"{b['title']} — {b['author']} ({b.get('genre') or 'Unknown'})"):
                st.caption(b.get('created_at', ''))
                st.write(b.get('description') or "No description.")
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("Summarize", key=f"sum-{b['id']}"):
                        with st.spinner("Summarizing with BART..."):
                            try:
                                res = summarize_book(b['id'])
                                st.session_state[f"summary-{b['id']}"] = res.get('summary')
                                st.success("Summarized")
                            except Exception as e:
                                st.error(f"Failed: {e}")
                with c2:
                    if st.button("Recommend", key=f"rec-{b['id']}"):
                        with st.spinner("Finding similar books..."):
                            try:
                                res = recommend_books(b['id'])
                                st.session_state[f"recs-{b['id']}"] = res.get('recommendations', [])
                                st.success("Done")
                            except Exception as e:
                                st.error(f"Failed: {e}")
                with c3:
                    if st.button("Delete", key=f"del-{b['id']}"):
                        try:
                            delete_book(b['id'])
                            st.warning("Book deleted")
                            st.session_state["refresh_counter"] = st.session_state.get("refresh_counter", 0) + 1
                        except Exception as e:
                            st.error(f"Failed: {e}")

                # Show results if present
                if (s := st.session_state.get(f"summary-{b['id']}")):
                    st.markdown("### Summary")
                    st.write(s)
                if (recs := st.session_state.get(f"recs-{b['id']}")):
                    st.markdown("### Recommendations")
                    for r in recs:
                        st.write(f"{r['title']} — {r['author']} ({r.get('genre') or 'Unknown'})  [score: {r['score']:.3f}]")

    with cols[1]:
        st.subheader("Edit Selected Book")
        book_ids = [b['id'] for b in books]
        book_map = {b['id']: b for b in books}
        selected_id = st.selectbox("Choose book", options=book_ids, format_func=lambda x: f"{book_map[x]['title']} — {book_map[x]['author']}") if books else None
        if selected_id:
            b = book_map[selected_id]
            title = st.text_input("Title", value=b['title'], key=f"edit-title-{selected_id}")
            author = st.text_input("Author", value=b['author'], key=f"edit-author-{selected_id}")
            genre = st.text_input("Genre", value=b.get('genre') or "", key=f"edit-genre-{selected_id}")
            description = st.text_area("Description", value=b.get('description') or "", key=f"edit-desc-{selected_id}")
            if st.button("Update", key=f"update-{selected_id}"):
                try:
                    update_book(selected_id, {"title": title, "author": author, "genre": genre, "description": description})
                    st.success("Updated")
                    st.session_state["refresh_counter"] = st.session_state.get("refresh_counter", 0) + 1
                except Exception as e:
                    st.error(f"Failed: {e}")


if __name__ == '__main__':
    main()


