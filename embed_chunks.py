import os
from dotenv import load_dotenv

# LangChain imports
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# ✅ Load API key
load_dotenv()

# ✅ Set script directory and file path
script_dir = os.path.dirname(os.path.abspath(__file__))
policy_path = os.path.join(script_dir, "policy.txt")

# ✅ Load policy text
try:
    with open(policy_path, "r", encoding="utf-8") as f:
        text = f.read()
except FileNotFoundError:
    raise FileNotFoundError(f"❌ 'policy.txt' not found at: {policy_path}")

if not text.strip():
    raise ValueError("⚠️ 'policy.txt' is empty. Add content to generate meaningful embeddings.")

# ✅ Wrap text as LangChain Document
doc = Document(page_content=text)

# ✅ Chunking
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents([doc])
print(f"🔹 Total chunks created: {len(chunks)}")

# ✅ Embed and store
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embeddings)

# ✅ Save FAISS index
vectorstore.save_local(os.path.join(script_dir, "faiss_index"))
print("✅ Embeddings complete. Stored in 'faiss_index'.")

