from neo4j import GraphDatabase
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

# -----------------------
# Neo4j connection
# -----------------------
URI =  "bolt://127.0.0.1:7687"
USER = "neo4j"
PASSWORD = "12345678"   # change if needed
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

# -----------------------
# PDF Upload and Processing
# -----------------------
PDF_PATH = "C:\\O3_CHATBOT_Workflow\\code\\smartcities-07-00121.pdf"  # Change this to your PDF path

# Load PDF
print(f"Loading PDF: {PDF_PATH}")
loader = PyPDFLoader(PDF_PATH)
documents = loader.load()

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(documents)

print(f"Loaded {len(documents)} pages, split into {len(chunks)} chunks")

# -----------------------
# Simple entity extraction (you can improve this later)
# -----------------------
def extract_entities_simple(text):
    """
    Simple entity extraction - extracts capitalized words/phrases
    You can replace this with NER later
    """
    import re
    # Find capitalized words (simple heuristic)
    words = text.split()
    entities = []
    for i, word in enumerate(words):
        # If word starts with capital and is not at sentence start
        if word[0].isupper() and len(word) > 2:
            # Check if it's not a common word
            if word.lower() not in ['the', 'this', 'that', 'these', 'those', 'and', 'but']:
                entities.append(word.strip('.,;:!?'))
    
    return list(set(entities))[:10]  # Return top 10 unique entities

# -----------------------
# Ingest function
# -----------------------
def ingest_pdf_to_neo4j(tx, doc_id, chunk_id, chunk_text, entities):
    # Create/merge document
    tx.run("""
    MERGE (d:Document {id: $doc_id})
    """, doc_id=doc_id)
    
    # Create chunk
    tx.run("""
    MERGE (c:Chunk {id: $chunk_id})
    SET c.text = $text
    """, chunk_id=chunk_id, text=chunk_text)
    
    # Link document to chunk
    tx.run("""
    MATCH (d:Document {id: $doc_id})
    MATCH (c:Chunk {id: $chunk_id})
    MERGE (d)-[:HAS_CHUNK]->(c)
    """, doc_id=doc_id, chunk_id=chunk_id)
    
    # Create entities and link to chunk
    for entity in entities:
        tx.run("""
        MERGE (e:Entity {name: $name})
        WITH e
        MATCH (c:Chunk {id: $chunk_id})
        MERGE (c)-[:MENTIONS]->(e)
        """, name=entity, chunk_id=chunk_id)

# -----------------------
# Process and ingest all chunks
# -----------------------
DOC_ID = os.path.basename(PDF_PATH).replace('.pdf', '')

print("\nIngesting chunks into Neo4j...")
with driver.session() as session:
    for idx, chunk in enumerate(chunks):
        chunk_id = f"{DOC_ID}_chunk_{idx}"
        chunk_text = chunk.page_content
        
        # Extract entities from this chunk
        entities = extract_entities_simple(chunk_text)
        
        print(f"Processing chunk {idx + 1}/{len(chunks)} - Found {len(entities)} entities")
        
        # Ingest to Neo4j
        session.execute_write(
            ingest_pdf_to_neo4j,
            doc_id=DOC_ID,
            chunk_id=chunk_id,
            chunk_text=chunk_text,
            entities=entities
        )

# -----------------------
# Verify ingestion
# -----------------------
print("\n" + "="*50)
print("Verification: Checking ingested data...")
print("="*50)

with driver.session() as session:
    # Count statistics
    stats = session.run("""
    MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)-[:MENTIONS]->(e:Entity)
    RETURN 
        count(DISTINCT d) AS num_documents,
        count(DISTINCT c) AS num_chunks,
        count(DISTINCT e) AS num_entities
    """).single()
    
    print(f"\nDocuments: {stats['num_documents']}")
    print(f"Chunks: {stats['num_chunks']}")
    print(f"Entities: {stats['num_entities']}")
    
    # Show sample data
    print("\nSample data (first 10 relationships):")
    result = session.run("""
    MATCH (d:Document)-[:HAS_CHUNK]->(c)-[:MENTIONS]->(e)
    RETURN d.id AS document, c.id AS chunk, e.name AS entity
    LIMIT 10
    """)
    
    for r in result:
        print(f"{r['document']} → {r['chunk']} → {r['entity']}")

driver.close()
print("\n✓ Ingestion complete!")