import streamlit as st
import os

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from langchain.schema import Document, HumanMessage, AIMessage
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

st.title('🗨️ Chatbot for Research Work Support on SPHERE testbed')

# — GROQ Key —
api_key = st.text_input('Enter your GROQ API key', type='password')
if not api_key:
    st.warning("Please enter your GROQ API key above.")
    st.stop()
llm = ChatGroq(groq_api_key=api_key, model_name='Gemma2-9b-It')

# — Session History Store —
session_id = st.text_input('Session ID', value='default_session')
st.session_state.setdefault('store', {})

def get_history(sid: str) -> BaseChatMessageHistory:
    return st.session_state.store.setdefault(sid, ChatMessageHistory())

# — Load & split Markdown docs —
docs_dir = 'docs'
if not os.path.isdir(docs_dir):
    st.error(f"Directory '{docs_dir}' not found.")
    st.stop()

md_files = [f for f in os.listdir(docs_dir) if f.lower().endswith('.md')]
if not md_files:
    st.error(f"No .md files found in '{docs_dir}'.")
    st.stop()

documents = []
for fn in md_files:
    with open(os.path.join(docs_dir, fn), 'r', encoding='utf-8') as f:
        documents.append(Document(page_content=f.read(), metadata={"source": fn}))

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = [c for c in splitter.split_documents(documents) if c.page_content.strip()]
if not splits:
    st.error("No non-empty text chunks after splitting your .md files.")
    st.stop()

# — Embedding & VectorStore —
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
persist_dir = "./chroma_persist"
os.makedirs(persist_dir, exist_ok=True)
try:
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=persist_dir
    )
except ValueError as e:
    st.error(f"Embedding failed: {e}")
    st.stop()
retriever = vectorstore.as_retriever()

# — Build RAG Chain —
contextualize = ChatPromptTemplate.from_messages([
    ("system",
     "You are a question-rewriting assistant.  Given the **chat history** and the latest user query, "
     "rewrite the query as a single, self-contained question.  "
     "Do NOT answer — only restate it clearly as if the history were not available."
     ),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])
history_aware = create_history_aware_retriever(llm, retriever, contextualize)

qa_system = (
    "You are an AI assistant. use the following retrieved passages"
    "Check for answer in retrieved documents first. If not found, you can use your knowledge to answer."
    "If you need more context information, then ask user but don't hallucinate/guess"
    "Keep your answer under three sentences.\n\n"
    "{context}"
)
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", qa_system),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])
qa_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(history_aware, qa_chain)

conv = RunnableWithMessageHistory(
    rag_chain,
    lambda _: get_history(session_id),
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer"
)

# — 1) First: handle any new input & invoke chain so history is updated immediately —
if user_input := st.chat_input("Type your question…"):
    conv.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}}
    )

# — 2) Then: render **all** messages (old + just-added) as chat bubbles —
for msg in get_history(session_id).messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)
