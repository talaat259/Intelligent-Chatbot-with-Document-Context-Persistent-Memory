
#####################################################
import os
from llama_index.core import StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
import qdrant_client
from langchain_ollama import ChatOllama
from langchain_community.graphs import Neo4jGraph
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_classic.memory import ChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.graphs import Neo4jGraph
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from llama_index.core import StorageContext, Settings, VectorStoreIndex

# class ChatUserBot:
#     def __init__(self):
#         self.store = {}
#         self.graph_chain = None
#         self.llm = None
#         self.query_engine = None
#         self.qdrant_client = None
        
#         # Configure embedding model (must match indexing)
#         embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
#         Settings.embed_model = embed_model
#         Settings.chunk_size = 512
#         Settings.chunk_overlap = 50

#     def load_document_index(self):
#         """Load the LlamaIndex document index from Qdrant"""
#         try:
#             if os.path.exists("./qdrant_storage"):
#                 print("Loading document index from Qdrant...")
                
#                 # Create Qdrant client
#                 self.qdrant_client = qdrant_client.QdrantClient(path="./qdrant_storage")
                
#                 # Create vector store
#                 vector_store = QdrantVectorStore(
#                     client=self.qdrant_client,
#                     collection_name="documents"
#                 )
                
#                 # Load index from vector store
#                 from llama_index.core import VectorStoreIndex
#                 index = VectorStoreIndex.from_vector_store(vector_store)
                
#                 self.query_engine = index.as_query_engine(
#                     similarity_top_k=3,
#                     response_mode="compact"
#                 )
#                 print("✓ Document index loaded successfully!")
#             else:
#                 print("⚠ Warning: No document index found at ./qdrant_storage")
#                 print("Please run the indexing script first.")
#                 self.query_engine = None
#         except Exception as e:
#             print(f"✗ Error loading document index: {e}")
#             self.query_engine = None

#     def query_documents(self, query: str) -> str:
#         """Query indexed documents"""
#         if self.query_engine is None:
#             return "No documents indexed."
#         try:
#             response = self.query_engine.query(query)
#             return str(response)
#         except Exception as e:
#             return f"Error querying documents: {e}"

#     def create_chatbot(self, graph=None):
#     # Initialize the LLM
#     self.llm = ChatOllama(
#         model="qwen3:4b",
#         temperature=0.3
#     )
    
#     # Load document index
#     self.load_document_index()
    
#     # Only create graph chain if graph is provided
#     if graph is not None:
#         self.graph_chain = GraphCypherQAChain.from_llm(
#             llm=self.llm,
#             graph=graph,
#             verbose=True,
#             return_intermediate_steps=False,
#             allow_dangerous_requests=True
#         )
    
#     prompt = PromptTemplate(
#         input_variables=["history", "input", "document_context"],
#         template="""You are a helpful AI assistant with access to indexed documents.
# Use the provided context to give accurate and detailed answers.

# Document Context: {document_context}

# Conversation so far:
# {history}""")
# class ChatUserBot:
#     def __init__(self):
#         self.store = {}
#         self.llm = None
#         self.query_engine = None
#         self.qdrant_client = None
        
#         # Configure embedding model (must match indexing)
#         embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
#         Settings.embed_model = embed_model
#         Settings.chunk_size = 512
#         Settings.chunk_overlap = 50

#     def load_document_index(self):
#         """Load the LlamaIndex document index from Qdrant"""
#         try:
#             if os.path.exists("./qdrant_storage"):
#                 print("Loading document index from Qdrant...")
                
#                 # Create Qdrant client
#                 self.qdrant_client = qdrant_client.QdrantClient(path="./qdrant_storage")
                
#                 # Create vector store
#                 vector_store = QdrantVectorStore(
#                     client=self.qdrant_client,
#                     collection_name="documents"
#                 )
                
#                 # Load index from vector store
#                 index = VectorStoreIndex.from_vector_store(vector_store)
                
#                 self.query_engine = index.as_query_engine(
#                     similarity_top_k=3,
#                     response_mode="compact"
#                 )
#                 print("✓ Document index loaded successfully!")
#             else:
#                 print("⚠ Warning: No document index found at ./qdrant_storage")
#                 print("Please run the indexing script first.")
#                 self.query_engine = None
#         except Exception as e:
#             print(f"✗ Error loading document index: {e}")
#             self.query_engine = None

#     def query_documents(self, query: str) -> str:
#         """Query indexed documents"""
#         if self.query_engine is None:
#             return "No documents indexed."
#         try:
#             response = self.query_engine.query(query)
#             return str(response)
#         except Exception as e:
#             return f"Error querying documents: {e}"

#     def get_session_history(self, session_id: str):
#         """Get or create session history"""
#         if session_id not in self.store:
#             self.store[session_id] = ChatMessageHistory()
#         return self.store[session_id]

#     def create_chatbot(self):
#         """Create chatbot with LlamaIndex document retrieval"""
#         # Initialize the LLM
#         self.llm = ChatOllama(
#             model="qwen3:4b",
#             temperature=0.3
#         )
        
#         # Load document index
#         self.load_document_index()
        
#         # Create prompt template
#         prompt = PromptTemplate(
#             input_variables=["history", "input", "document_context"],
#             template="""You are a helpful AI assistant with access to indexed documents.
#             Use the provided context to give accurate and detailed answers.

#             Document Context: {document_context}

#             Conversation so far:
#             {history}
#             Human: {input}
#             AI Assistant:"""
#         )
        
        
#         def get_document_context(inputs):
#             user_query = inputs["input"]
            
#             try:
#                 document_context = self.query_documents(user_query)
#             except Exception as e:
#                 document_context = f"Document query error: {str(e)}"
            
#             return {
#                 "document_context": document_context,
#                 **inputs
#             }
        
#         # Chain: get document context -> apply prompt -> LLM
#         chain = (
#             RunnablePassthrough() 
#             | get_document_context 
#             | prompt 
#             | self.llm 
#             | StrOutputParser()
#         )

#         # Add memory to chain
#         chain_with_memory = RunnableWithMessageHistory(
#             chain,
#             self.get_session_history,
#             input_messages_key="input",
#             history_messages_key="history"
#         )

#         return chain_with_memory
###################################################################
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
#from langchain_core.memory import ChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.graphs import Neo4jGraph
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain

graph = Neo4jGraph(
    url="bolt://localhost:7687",
    username="neo4j",
    password="12345678"
)

class ChatUserBot:
    def __init__(self):
        self.store = {}
        self.graph_chain = None
        self.llm = None

    def create_chatbot(self):
        # Initialize the LLM
        self.llm = ChatOllama(
            model="qwen3:4b",
            temperature=0.2
        )
        
        # Create Neo4j chain for graph queries
        self.graph_chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=graph,
            verbose=True,
            return_intermediate_steps=False,
            allow_dangerous_requests=True
        )
        
        prompt = PromptTemplate(
            input_variables=["history", "input", "graph_context"],
            template="""You are a helpful AI assistant with access to a knowledge graph. 
            Use the graph context when available to provide accurate answers,the output should be concise,in full details and clear.

            Graph Context: {graph_context}
            
            Conversation so far:
            {history}

            Human: {input}
            AI Assistant:"""
        )
        
        # Function to query graph and get context
        def get_graph_context(inputs):
            try:
                result = self.graph_chain.invoke({"query": inputs["input"]})
                return {"graph_context": result.get("result", "No graph data found"), **inputs}
            except Exception as e:
                return {"graph_context": "No graph data available", **inputs}
        
        # Chain: get graph context -> apply prompt -> LLM
        chain = (
            RunnablePassthrough() 
            | get_graph_context 
            | prompt 
            | self.llm 
            | StrOutputParser()
        )

        chain_with_memory = RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="history"
        )

        return chain_with_memory

    def get_session_history(self, session_id: str):
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]


def main():
    """Main function to run the chatbot"""
    print("=" * 60)
    print("Interactive Chatbot with LangChain and Neo4j")
    print("=" * 60)
    print("This chatbot remembers your conversation history!")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("=" * 60)
    print()
    
    # Create the chatbot
    try:
        bot = ChatUserBot()
        chatbot = bot.create_chatbot()
    except Exception as e:
        print(f"Error initializing chatbot: {e}")
        return
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
            print("\nChatbot: Goodbye! It was nice talking with you!")
            break
        
        # Skip empty inputs
        if not user_input:
            continue
        
        try:
            # Get response from chatbot with session_id in config
            response = chatbot.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": "user_session_1"}}
            )
            print(f"\nChatbot: {response}\n")
        except Exception as e:
            print(f"\nError: {e}\n")
            print("Please try again or type 'quit' to exit.\n")


if __name__ == "__main__":
    main()