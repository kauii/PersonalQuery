from db.database import get_db
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

db = get_db()
print(db.get_usable_table_names())

results = db._execute("SELECT DISTINCT windowTitle FROM window_activity WHERE windowTitle IS NOT NULL")
titles = [row["windowTitle"] for row in results]

activities = ["Uncategorized",
              "DevCode",
              "DevDebug",
              "DevReview",
              "DevVc",
              "Planning",
              "ReadWriteDocument",
              "Design",
              "GenerativeAI",
              "PlannedMeeting",
              "Email",
              "InstantMessaging",
              "WorkRelatedBrowsing",
              "WorkUnrelatedBrowsing",
              "SocialMedia",
              "FileManagement",
              "Other",
              "OtherRdp",
              "Idle",
              "Unknown"]

embedding_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vector_store = FAISS.from_texts(activities, embedding_model)

vector_store.save_local("activities_index")
