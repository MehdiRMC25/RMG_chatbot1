import os
import logging
import traceback
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# --- Email dependencies & simple detectors ---
import os, re, smtplib
from email.message import EmailMessage

PHONE_RE = re.compile(r'(?:\+?\d[\d\-\s()]{7,}\d)')   # simple phone detector
EMAIL_RE = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')     # simple email detector

def send_lead_email(user_text: str, page_url: str = "", session_id: str = "") -> None:
    """Send lead email when phone/email detected in chatbot message."""

    host = os.getenv("SMTP_HOST")
    port_str = os.getenv("SMTP_PORT")
    user = os.getenv("SMTP_USER")
    pwd  = os.getenv("SMTP_PASS")
    to   = os.getenv("LEAD_TO_EMAIL")

    if not all([host, port_str, user, pwd, to]):
        print("❌ Lead email skipped: missing SMTP env vars")
        return

    try:
        port = int(port_str)
    except ValueError:
        print(f"❌ Invalid SMTP_PORT: {port_str}")
        return

    msg = EmailMessage()
    msg["Subject"] = "📩 New Lead from Chatbot"
    msg["From"]    = user
    msg["To"]      = to
    msg.set_content(
        f"Chatbot lead captured\n\n"
        f"Session: {session_id}\n"
        f"Page: {page_url}\n"
        f"Message: {user_text}\n"
    )

    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=10) as s:
                s.login(user, pwd)
                s.send_message(msg)
        else:  # assume 587
            with smtplib.SMTP(host, port, timeout=10) as s:
                s.starttls()
                s.login(user, pwd)
                s.send_message(msg)

        print("✅ Lead email sent.")
    except Exception as e:
        print("❌ Lead email error:", repr(e))

       
# LangChain / RAG imports
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

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
    model="gpt-5",
    temperature=1.0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# ---- System Prompt Guardrails ----
system_prompt = """You are RMG’s virtual assistant.
Keep answers under 3–4 sentences.
Guide visitors to understand services and encourage them to contact us.
Do not generate or share full or partial project plans, marketing strategies, frameworks, or documents.
Do not copy or summarise extracts from internal consulting materials.
Instead, explain services in general terms and redirect users to our team for tailored solutions."""

# Custom prompt template with system instruction
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "Use the following context to answer the question, but DO NOT copy it directly or provide extracts.\n\nContext:\n{context}\n\nQuestion: {question}")
])

# RAG chain setup
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",  # simplest RAG chain type
    return_source_documents=False,
    chain_type_kwargs={
        "prompt": prompt
    }
)

# Serve frontend
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return render_template('index.html')  # Ensure /templates/index.html exists

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    # Optional: capture page URL and session ID for context
    page_url   = data.get("page_url", request.headers.get("Referer", ""))
    session_id = request.cookies.get("session_id", "")

    user_message = data.get('message', '').strip()
    # Trigger email if the user message contains an email or phone number
    if EMAIL_RE.search(user_message) or PHONE_RE.search(user_message):
        print("Attempting to send email to:", "inquiry@rewiremodel.com")
        send_lead_email(user_message, page_url=page_url, session_id=session_id)

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
