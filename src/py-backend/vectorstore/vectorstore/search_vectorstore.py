from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.load_local("activities_index", embedding_model, allow_dangerous_deserialization=True)

results = vector_store.similarity_search("work unrelated")
for doc in results:
    print(doc.page_content)
