
import vlm_injetion as vlm
import hashing as hs
import user_chatbot as uc

# Create chatbot instance once and keep reference to the bot instance
bot_instance = uc.ChatUserBot()
chatbot = bot_instance.create_chatbot()


def if_doc_exists(doc):
    """
    Check if document exists by hash. If not, add to Neo4j.
    Returns True if document already exists, False if newly added.
    """
    document_hash = hs.hash_file(doc)
    
    try:
        with open("document_hashes.txt", "r") as f:
            file_content = f.read()
            if document_hash in file_content:
                return True  # Document already exists
    except FileNotFoundError:
        # File doesn't exist yet, create it
        pass
    
    # Add new document hash and ingest to Neo4j
    with open("document_hashes.txt", "a") as f:
        f.write(document_hash + "\n")
    
    vlm.add_multiple_pdfs([doc])
    return False  # Document was newly added


def bot_chat_with_docs(user_query, user_id):
    """
    Handle chatbot interaction with Neo4j knowledge graph.
    Retrieves relevant context from Neo4j and maintains conversation history.
    Returns response for web interface.
    """
    
    if not user_query or not user_query.strip():
        return "Please provide a message."
    
    user_input = user_query.strip()
    
    if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
        return "Goodbye! It was nice talking with you!"
    
    try:
        print(f"\n=== DEBUG: Starting query processing ===")
        print(f"User Query: {user_input}")
        print(f"User ID: {user_id}")
        
        # ✅ QUERY NEO4J KNOWLEDGE GRAPH
        from langchain_community.graphs import Neo4jGraph
        
        graph = Neo4jGraph(
            url="bolt://localhost:7687",
            username="neo4j",
            password="12345678"
        )
        
        # Extract keywords from query for better search
        keywords = user_input.lower().split()
        
        neo4j_context = ""
        try:
            # Search for relevant chunks in Neo4j using multiple keywords
            neo4j_result = graph.query("""
                MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
                WHERE ANY(keyword IN $keywords WHERE toLower(c.text) CONTAINS keyword)
                RETURN d.name as document, c.text as content, c.page as page, c.index as chunk_index
                ORDER BY c.index
                LIMIT 5
            """, {"keywords": keywords})
            
            if neo4j_result:
                neo4j_context = "Context from your documents:\n---\n"
                for result in neo4j_result:
                    neo4j_context += f"[{result['document']} - Page {result['page']}]\n{result['content']}\n\n"
                neo4j_context += "---\n"
                print(f"✓ Retrieved Neo4j context: {len(neo4j_result)} chunks")
            else:
                print("✗ No Neo4j context found")
                neo4j_context = ""
        except Exception as neo_error:
            print(f"Neo4j query error: {neo_error}")
            neo4j_context = ""
        
        # ✅ BUILD ENHANCED QUERY WITH NEO4J CONTEXT
        if neo4j_context:
            enhanced_query = f"""{neo4j_context}
Based on the above context from the documents, please answer: {user_input}"""
        else:
            enhanced_query = user_input
        
        # ✅ SEND TO CHATBOT WITH MEMORY
        print(f"\n=== DEBUG: Sending to chatbot ===")
        print(f"Session ID: user_{user_id}")
        
        # The chatbot maintains conversation history via session_id
        response = chatbot.invoke(
            {"input": enhanced_query},
            config={"configurable": {"session_id": f"user_{user_id}"}}
        )
        
        print(f"\n=== DEBUG: Chatbot response ===")
        print(f"Type: {type(response)}")
        print(f"Value preview: {str(response)[:200]}...")
        
        if response is None:
            print("ERROR: Response is None!")
            return "Error: Chatbot returned None"
        
        # ✅ STORE CONVERSATION IN NEO4J FOR PERSISTENCE
        try:
            graph.query("""
                MERGE (u:User {id: $user_id})
                CREATE (m:Message {
                    timestamp: datetime(),
                    query: $query,
                    response: $response
                })
                CREATE (u)-[:ASKED]->(m)
            """, {
                "user_id": str(user_id),
                "query": user_input,
                "response": str(response)
            })
            print("✓ Conversation stored in Neo4j")
        except Exception as store_error:
            print(f"Warning: Could not store conversation in Neo4j: {store_error}")
        
        return response
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return error_msg


def get_user_conversation_history(user_id, limit=10):
    """
    Retrieve user's conversation history from Neo4j.
    """
    from langchain_community.graphs import Neo4jGraph
    
    graph = Neo4jGraph(
        url="bolt://localhost:7687",
        username="neo4j",
        password="12345678"
    )
    
    try:
        result = graph.query("""
            MATCH (u:User {id: $user_id})-[:ASKED]->(m:Message)
            RETURN m.query as query, m.response as response, m.timestamp as timestamp
            ORDER BY m.timestamp DESC
            LIMIT $limit
        """, {"user_id": str(user_id), "limit": limit})
        
        return result
    except Exception as e:
        print(f"Error retrieving conversation history: {e}")
        return []


def clear_user_chat_history(user_id):
    """
    Clear chat history for a specific user from memory.
    Note: This clears the in-memory session, not Neo4j history.
    """
    try:
        session_id = f"user_{user_id}"
        
        # ✅ Use the SAME bot_instance from module level
        if hasattr(bot_instance, 'store') and session_id in bot_instance.store:
            bot_instance.store[session_id].clear()
            print(f"✓ Chat memory cleared for user {user_id}")
            return True
        else:
            print(f"✗ No chat memory found for user {user_id}")
            return False
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        return False


def clear_user_neo4j_history(user_id):
    """
    Clear conversation history from Neo4j database.
    """
    from langchain_community.graphs import Neo4jGraph
    
    graph = Neo4jGraph(
        url="bolt://localhost:7687",
        username="neo4j",
        password="12345678"
    )
    
    try:
        graph.query("""
            MATCH (u:User {id: $user_id})-[:ASKED]->(m:Message)
            DETACH DELETE m
        """, {"user_id": str(user_id)})
        
        print(f"✓ Neo4j conversation history cleared for user {user_id}")
        return True
    except Exception as e:
        print(f"Error clearing Neo4j history: {e}")
        return False

# # Create a single chatbot instance that persists across calls
# # This ensures chat memory is maintained between requests
# bot_instance = uc.ChatUserBot()
# chatbot = bot_instance.create_chatbot()  # <-- Remove graph parameter


# # integration.py (or backend_logic.py)
# def if_doc_exists(doc, user_id):
#     """Check if a document exists for the user."""
#     document_hash = hs.hash_file(doc)
#     user_documents = db.get_user_document_hashes(user_id)
    
#     if len(user_documents) == 0:
#         return False
    
#     for user_doc in user_documents:
#         if user_doc == document_hash:
#             return True
    
#     return False


# def create_new_doc(doc, user_id, title, content):
#     """Create a new document for the user and ingest into RAG."""
#     document_hash = hs.hash_file(doc)
    
#     #db.add_document(document_hash, user_id, title, content)
    
#     try:
#         vlm.indeer()
#     except Exception as e:
#         print(f"RAG ingestion error: {e}")
    
#     return "Document added successfully."


# def add_document_if_new(doc, user_id, title, content):
#     """Add document only if it doesn't exist."""
#     print("in the function")
#     vlm.indeer()
#     print("Document ingested.")
#     return "Document added successfully."
#     # if not if_doc_exists(doc, user_id):
#     #     return create_new_doc(doc, user_id, title, content)
#     # else:
#     #     vlm.indeer()
#     #     return "Document already exists."


# #def bot_chat(user_query, user_id):
# # integration.py - Fix bot_chat_with_docs

# def bot_chat(user_query, user_id):
#     """
#     Handle chatbot interaction with RAG retrieval.
#     Retrieves relevant context from LlamaIndex/Qdrant and sends to chatbot.
#     Returns response for web interface.
#     """
    
#     if not user_query or not user_query.strip():
#         return "Please provide a message."
    
#     user_input = user_query.strip()
    
#     if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
#         return "Goodbye! It was nice talking with you!"
    
#     try:
#         print(f"\n=== DEBUG: Querying RAG ===")
#         print(f"User Query: {user_input}")
        
#         # ✅ QUERY THE RAG SYSTEM
#         from vlm_injetion import query_index
        
#         rag_context = query_index(user_input, top_k=5)
        
#         if rag_context:
#             print(f"✓ Retrieved RAG context: {len(rag_context)} chars")
            
#             # Inject RAG context into the user query
#             enhanced_query = f"""Context from your documents:
# ---
# {rag_context}
# ---

# Based on the above context, please answer: {user_input}"""
            
#         else:
#             print("✗ No RAG context found")
#             enhanced_query = user_input
        
#         print(f"\n=== DEBUG: Sending to chatbot ===")
#         print(f"Session ID: user_{user_id}")
        
#         response = chatbot.invoke(
#             {"input": enhanced_query},
#             config={"configurable": {"session_id": f"user_{user_id}"}}
#         )
        
#         print(f"\n=== DEBUG: Chatbot response ===")
#         print(f"Type: {type(response)}")
#         print(f"Value preview: {str(response)[:200]}...")
        
#         if response is None:
#             print("ERROR: Response is None!")
#             return "Error: Chatbot returned None"
        
#         return response
        
#     except Exception as e:
#         error_msg = f"Error: {str(e)}"
#         print(error_msg)
#         import traceback
#         traceback.print_exc()
#         return error_msg


# # integration.py - Fix bot_chat_with_docs



# def clear_user_chat_history(user_id):
#     """Clear chat history for a specific user."""
#     try:
#         session_id = f"user_{user_id}"
#         if session_id in bot_instance.store:
#             bot_instance.store[session_id].clear()
#             print(f"Chat history cleared for user {user_id}")
#         else:
#             print(f"No chat history found for user {user_id}")
#     except Exception as e:
#         print(f"Error clearing chat history: {e}")


# def get_chat_history(user_id):
#     """Retrieve chat history for a specific user."""
#     try:
#         session_id = f"user_{user_id}"
#         if session_id in bot_instance.store:
#             history = bot_instance.store[session_id].messages
#             print(f"\nChat History for User {user_id}:")
#             print("=" * 60)
#             for msg in history:
#                 role = "Human" if msg.type == "human" else "AI"
#                 print(f"{role}: {msg.content}")
#             print("=" * 60)
#         else:
#             print(f"No chat history found for user {user_id}")
#     except Exception as e:
#         print(f"Error retrieving chat history: {e}")


# if __name__ == "__main__":
#     test_user_id = "test_user_123"
    
#     print("Testing chatbot with memory...")
#     print("=" * 60)
    
#     response = bot_chat("Hello, my name is John", test_user_id)
#     print(f"\nChatbot: {response}\n")
    
#     response = bot_chat("What's my name?", test_user_id)
#     print(f"\nChatbot: {response}\n")
    
#     response = bot_chat("What is the capital of France?", test_user_id)
#     print(f"\nChatbot: {response}\n")
    
#     get_chat_history(test_user_id)
#     clear_user_chat_history(test_user_id)
    
#     response = bot_chat("Do you remember my name?", test_user_id)
#     print(f"\nChatbot: {response}\n")