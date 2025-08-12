import os
import logging
import traceback
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# LangChain / RAG imports
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI

# Load environment variables (for local testing or Render.com)
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Flask app setup
app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "*"}})

# Ensure script uses its own folder as working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("🛠 Loading FAISS index from:", os.getcwd())
print("🛠 Directory contents:", os.listdir())

# Load FAISS vector store
db = FAISS.load_local(
    "faiss_index",
    OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY")),
    allow_dangerous_deserialization=True
)
retriever = db.as_retriever()

# Load LLM
llm = ChatOpenAI(
    model_name="gpt-5",
    temperature=0.0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# RAG chain setup
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",  # simplest RAG chain type
    return_source_documents=False
)

# Serve frontend
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return render_template('index.html')  # Ensure /templates/index.html exists

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    logging.info("📩 User message: %s", user_message)

    if not user_message:
        return jsonify({"response": "Zəhmət olmasa bir mesaj daxil edin."})

    try:
        full_result = qa_chain({"query": user_message})
        result = full_result.get("result", "Sistemdə nasazlıq yarandı.")
        logging.info("📄 RAG Response: %s", result)
        return jsonify({"response": result})
    except Exception as e:
        logging.error("❌ Chat error:\n%s", traceback.format_exc())
        return jsonify({"response": f"Sistem xətası: {str(e)}"})

# Run locally or in Render.com
if __name__ == '__main__':
    if not os.path.exists("faiss_index"):
        print("📌 Embedding FAISS index...")
        exec(open("embed_chunks.py").read())

    app.run(host='0.0.0.0', port=10000)
