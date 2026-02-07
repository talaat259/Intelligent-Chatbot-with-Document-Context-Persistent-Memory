from langchain_community.document_loaders import PyPDFLoader
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from vlm_System_Prompt import SYSTEM_PROMPT
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext, Document
import os
import qdrant_client
from llama_index.vector_stores.qdrant import QdrantVectorStore
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
import atexit
from tqdm import tqdm

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.graphs import Neo4jGraph
import os

# Initialize Neo4j connection
graph = Neo4jGraph(
    url="bolt://localhost:7687",
    username="neo4j",
    password="12345678"
)

def add_pdf_to_neo4j(pdf_path):
    """
    Read a PDF and add its content to Neo4j as nodes.
    
    Args:
        pdf_path (str): Path to the PDF file
    """
    
    # Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    
    # Get filename
    filename = os.path.basename(pdf_path)
    
    # Create Document node
    graph.query("""
        MERGE (d:Document {name: $filename})
        SET d.path = $path,
            d.total_pages = $pages
        """, 
        {
            "filename": filename,
            "path": pdf_path,
            "pages": len(documents)
        }
    )
    
    # Add chunks to Neo4j
    for i, chunk in enumerate(chunks):
        graph.query("""
            MATCH (d:Document {name: $filename})
            CREATE (c:Chunk {
                index: $index,
                text: $text,
                page: $page
            })
            CREATE (d)-[:HAS_CHUNK]->(c)
            """,
            {
                "filename": filename,
                "index": i,
                "text": chunk.page_content,
                "page": chunk.metadata.get('page', 0)
            }
        )
    
    print(f"✓ Added {len(chunks)} chunks from {filename} to Neo4j")


def add_multiple_pdfs(docs_list: list):
    """
    Add all PDFs from a list of paths to Neo4j.
    
    Args:
        docs_list (list): List of PDF file paths
    """
    for pdf_path in docs_list:
        try:
            add_pdf_to_neo4j(pdf_path)
        except Exception as e:
            print(f"✗ Error processing {pdf_path}: {e}")

# Example usage
if __name__ == "__main__":
    # Single PDF
    add_pdf_to_neo4j("document.pdf")
    
    # Or multiple PDFs from folder
    # add_multiple_pdfs("pdfs_folder")










# # Configure embedding model
# embed_model = HuggingFaceEmbedding(
#     model_name="BAAI/bge-m3"
# )
# Settings.embed_model = embed_model
# Settings.chunk_size = 512
# Settings.chunk_overlap = 50


# def get_all_files():
#     folder_path = "C:\\O3_CHATBOT_Workflow\\code\\uploads"
#     files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
#              if os.path.isfile(os.path.join(folder_path, f))]
#     return files


# def create_index(file_paths_list: list) -> VectorStoreIndex:
#     # Create Qdrant client (uses HNSW by default)
#     client = qdrant_client.QdrantClient(path="./qdrant_storage")
    
#     try:
#         # Check if collection already exists
#         collections = client.get_collections().collections
#         collection_exists = any(col.name == "documents" for col in collections)
        
#         if collection_exists:
#             # Load existing index
#             vector_store = QdrantVectorStore(
#                 client=client,
#                 collection_name="documents"
#             )
#             index = VectorStoreIndex.from_vector_store(vector_store)
#             print("Loaded existing Qdrant index")
#         else:
#             # Create new vector store
#             vector_store = QdrantVectorStore(
#                 client=client,
#                 collection_name="documents"
#             )
#             index = None
        
#         # Process each file
#         for file_path in file_paths_list:
#             print(f"Processing: {file_path}")
#             loader = PyPDFLoader(file_path)
#             langchain_documents = loader.load()
            
#             # Convert LangChain documents to LlamaIndex documents
#             llamaindex_documents = []
#             for doc in langchain_documents:
#                 llamaindex_doc = Document(
#                     text=doc.page_content,
#                     metadata=doc.metadata
#                 )
#                 llamaindex_documents.append(llamaindex_doc)
            
#             if index is None:
#                 # Create new index with Qdrant storage
#                 storage_context = StorageContext.from_defaults(vector_store=vector_store)
#                 index = VectorStoreIndex.from_documents(
#                     llamaindex_documents,
#                     storage_context=storage_context,
#                     show_progress=True
#                 )
#             else:
#                 # Add new documents to existing index
#                 for doc in llamaindex_documents:
#                     index.insert(doc)
        
#         print("Index saved to Qdrant (HNSW enabled)")
#         return index
    
#     finally:
#         # Always close the client to release the lock
#         client.close()


# def indeer():
#     files = get_all_files()
#     if not files:
#         print("No files found in uploads folder!")
#         return
    
#     print(f"Found {len(files)} files to process")
#     index = create_index(files)
#     print("Indexing complete with HNSW!")


# if __name__ == "__main__":
#     indeer()

#############################################################################
# # Configure embedding model
# embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
# Settings.embed_model = embed_model
# Settings.chunk_size = 512
# Settings.chunk_overlap = 50

# # Global singleton variables
# _qdrant_client = None
# _index = None


# def get_qdrant_client():
#     """Get or create singleton Qdrant client."""
#     global _qdrant_client
#     if _qdrant_client is None:
#         _qdrant_client = qdrant_client.QdrantClient(path="./qdrant_storage")
#         print("✓ Created Qdrant client (singleton)")
#     return _qdrant_client


# def get_or_create_index():
#     """Get or create the vector index."""
#     global _index
    
#     if _index is not None:
#         print("✓ Using existing index")
#         return _index
    
#     client = get_qdrant_client()
    
#     # Check if collection already exists
#     collections = client.get_collections().collections
#     collection_exists = any(col.name == "documents" for col in collections)
    
#     vector_store = QdrantVectorStore(
#         client=client,
#         collection_name="documents"
#     )
    
#     if collection_exists:
#         # Load existing index
#         _index = VectorStoreIndex.from_vector_store(vector_store)
#         print("✓ Loaded existing Qdrant index")
#     else:
#         # Create new index
#         storage_context = StorageContext.from_defaults(vector_store=vector_store)
#         _index = VectorStoreIndex.from_documents([], storage_context=storage_context)
#         print("✓ Created new Qdrant index")
    
#     return _index


# def cleanup_qdrant():
#     """Close Qdrant client on exit."""
#     global _qdrant_client, _index
#     if _qdrant_client is not None:
#         try:
#             _qdrant_client.close()
#             print("✓ Qdrant client closed")
#         except Exception as e:
#             print(f"Error closing client: {e}")
#         _qdrant_client = None
#         _index = None


# # Register cleanup function to run on exit
# atexit.register(cleanup_qdrant)


# def load_document(file_path: str):
#     """Load document based on file extension."""
#     file_extension = os.path.splitext(file_path)[1].lower()
    
#     if file_extension == '.pdf':
#         loader = PyPDFLoader(file_path)
#     elif file_extension in ['.docx', '.doc']:
#         loader = Docx2txtLoader(file_path)
#     elif file_extension == '.txt':
#         loader = TextLoader(file_path)
#     else:
#         raise ValueError(f"Unsupported file type: {file_extension}")
    
#     return loader.load()


# def add_document_to_index(file_path: str):
#     """Add a single document to the index (uses singleton client)."""
#     try:
#         index = get_or_create_index()
        
#         print(f"Processing: {file_path}")
#         langchain_documents = load_document(file_path)
        
#         # Convert LangChain documents to LlamaIndex documents
#         for doc in langchain_documents:
#             llamaindex_doc = Document(
#                 text=doc.page_content,
#                 metadata={**doc.metadata, "source": file_path}
#             )
#             index.insert(llamaindex_doc)
        
#         print(f"✓ Indexed: {file_path}")
#         return True
        
#     except Exception as e:
#         print(f"✗ Error indexing {file_path}: {e}")
#         import traceback
#         traceback.print_exc()
#         return False


# def create_index(file_paths_list: list) -> VectorStoreIndex:
#     """Add multiple documents to the index (uses singleton client)."""
#     index = get_or_create_index()
    
#     # Process each file
#     for file_path in file_paths_list:
#         add_document_to_index(file_path)
    
#     print("✓ Index saved to Qdrant (HNSW enabled)")
#     return index


# def query_index(query_text: str, top_k: int = 10):
#     """Query the index for relevant documents."""
#     try:
#         index = get_or_create_index()
#         query_engine = index.as_query_engine(similarity_top_k=top_k)
#         response = query_engine.query(query_text)
#         return str(response)
#     except Exception as e:
#         print(f"Query error: {e}")
#         import traceback
#         traceback.print_exc()
#         return None


# def get_all_files():
#     """Get all files from uploads folder."""
#     folder_path = "C:\\O3_CHATBOT_Workflow\\code\\uploads"
#     if not os.path.exists(folder_path):
#         return []
#     files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
#              if os.path.isfile(os.path.join(folder_path, f))]
#     return files


# def indeer():
#     """Index all files in uploads folder."""
#     files = get_all_files()
#     if not files:
#         print("No files found in uploads folder!")
#         return
    
#     print(f"Found {len(files)} files to process")
#     index = create_index(files)
#     print("✓ Indexing complete with HNSW!")


# if __name__ == "__main__":
#     indeer()