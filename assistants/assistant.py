from phi.assistant import Assistant
from phi.knowledge.langchain import LangChainKnowledgeBase
from phi.vectordb.pgvector import PgVector2
from phi.llm.ollama.chat import Ollama

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings

from env import openai_key

# knowledge_base = TextKnowledgeBase(
#     path="./dataset",
#     vector_db=PgVector2(
#         collection="text_documents",
#         db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
#     ),
# )

chroma_db_dir = "./chroma"

def load_vector_store():
    # with open('./dataset/workflows/build.yml', 'r') as file:
    #     data = file.read()
    # -*- Load the document
    raw_documents = TextLoader('./dataset/worflows-test/vulnerability-scan.yml').load()
    # -*- Split it into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = text_splitter.split_documents(raw_documents)
    # -*- Embed each chunk and load it into the vector store
    Chroma.from_documents(documents, FastEmbedEmbeddings(), persist_directory=str(chroma_db_dir))

load_vector_store()

db = Chroma(embedding_function=FastEmbedEmbeddings(), persist_directory=str(chroma_db_dir))
retriever = db.as_retriever()

knowledge_base = LangChainKnowledgeBase(retriever=retriever)

assistant = Assistant(
    llm=Ollama(model="llama3"),
    knowledge_base=knowledge_base,
    add_references_to_prompt=True,
)

# Create a github action workflow to scan for vulnerabilities on ubuntu