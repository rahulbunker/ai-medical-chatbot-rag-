import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DB_FAISS_PATH = "vectorstore/db_faiss"

PROMPT_TEMPLATE = """
You are a medical AI assistant. Answer ONLY from the provided context.
If the answer is not in the context, say "I don't know based on the provided information."
Do NOT make up answers.

Context:
{context}

Question:
{question}

Answer:
"""

def load_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
        temperature=0.5,
        max_tokens=512
    )

def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = FAISS.load_local(
        DB_FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

def get_answer(query):
    retriever = load_vectorstore()
    docs = retriever.invoke(query)
    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )
    llm = load_llm()
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"context": context, "question": query})
    return result, docs