# === vectorstore/create_vectorstore.py ===
from db.database import get_db
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


def build_vectorstore():
    db = get_db()
    results = db._execute("""
        SELECT DISTINCT processName 
        FROM window_activity 
        WHERE processName IS NOT NULL
    """)
    titles = [row["processName"] for row in results]

    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(titles, embedding_model)

    vector_store.save_local("process_names_index")
    print("✅ Vector store built and saved.")


if __name__ == "__main__":
    build_vectorstore()
