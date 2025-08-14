from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# ✅ Load text from policy.txt
with open(r"D:\"C:\Users\Mehdi\Documents\GitHub\RMG_chatbot1\policy.txt", "r", encoding="utf-8") as f:
    full_text = f.read()

# ✅ Wrap it as a LangChain Document
doc = Document(page_content=full_text)

# ✅ Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents([doc])

# ✅ Optional: print some chunks to inspect
for i, chunk in enumerate(chunks[:3]):
    print(f"\n--- Chunk {i+1} ---\n{chunk.page_content}")

# ✅ Save chunk count
print(f"\n✅ Total chunks created: {len(chunks)}")
