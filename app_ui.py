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

    # Sidebar controls
    with st.sidebar:
        st.header("Search & Actions")
        query = st.text_input("Search books (text search)")
        st.write("Backend:", BACKEND_URL)
        if st.button("Refresh List"):
            st.session_state["refresh_counter"] = st.session_state.get("refresh_counter", 0) + 1

        st.divider()
        st.subheader("AI-Powered Search")
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


    # Main area
    # Show AI search results if available
    if st.session_state.get("ai_search_results"):
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
            with st.expander(f"{b['title']} — {b['author']} ({b.get('genre') or 'Unknown'})"):
                st.caption(b.get('created_at', ''))
                st.write(b.get('description') or "No description.")
                c1, c2 = st.columns(2)
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

                # Show results if present
                if (s := st.session_state.get(f"summary-{b['id']}")):
                    st.markdown("### Summary")
                    st.write(s)
                if (recs := st.session_state.get(f"recs-{b['id']}")):
                    st.markdown("### Recommendations")
                    for r in recs:
                        st.write(f"{r['title']} — {r['author']} ({r.get('genre') or 'Unknown'})  [score: {r['score']:.3f}]")

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
            # Get book details
            if selected_id in book_map:
                b = book_map[selected_id]
            else:
                try:
                    b = get_book(selected_id)
                except:
                    st.error("Book not found")
                    return
            
            st.markdown(f"### {b['title']}")
            st.write(f"**Author:** {b['author']}")
            st.write(f"**Genre:** {b.get('genre') or 'Unknown'}")
            st.write(f"**Description:** {b.get('description') or 'No description'}")
            
            # Auto-summarize when book is selected
            summary_key = f"auto_summary_{selected_id}"
            if summary_key not in st.session_state:
                with st.spinner("Generating summary with AI..."):
                    try:
                        res = summarize_book(selected_id)
                        st.session_state[summary_key] = res.get('summary')
                    except Exception as e:
                        st.session_state[summary_key] = None
                        st.error(f"Failed to generate summary: {e}")
            
            if st.session_state.get(summary_key):
                st.markdown("### 📝 AI-Generated Summary")
                st.info(st.session_state[summary_key])


if __name__ == '__main__':
    main()


