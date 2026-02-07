from langchain_community.graphs import Neo4jGraph

def clear_neo4j_database():
    """
    Clear all nodes and relationships from Neo4j database
    """
    graph = Neo4jGraph(
        url="bolt://localhost:7687",
        username="neo4j",
        password="12345678"
    )
    
    try:
        # Delete all nodes and relationships
        graph.query("MATCH (n) DETACH DELETE n")
        print("✓ Neo4j database cleared successfully")
        return True
    except Exception as e:
        print(f"❌ Error clearing Neo4j database: {e}")
        return False

def clear_text_file(filepath):
    """
    Clear all contents from a text file (file remains empty)
    """
    try:
        with open(filepath, 'w') as f:
            f.write('')  # Write empty string
        print(f"✓ Cleared contents of {filepath}")
        return True
    except FileNotFoundError:
        print(f"⚠️  File not found: {filepath}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Usage
clear_text_file('document_hashes.txt')