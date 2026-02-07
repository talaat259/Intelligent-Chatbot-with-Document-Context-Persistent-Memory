import hashlib

def hash_file(file_path: str) -> str:
    """Generate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# if __name__ == "__main__":
#     file="C:\\O3_CHATBOT_Workflow\\code\\Agent_Archetecture.drawio (1).pdf"
#     print(f"Hash of the file {file} is: {hash_file(file)}")
#     print(f"Hash of the file {file} is: {hash_file(file)}")
#     hash_value1 = hash_file(file)
#     hash_value2 = hash_file(file)
#     if(hash_value1 == hash_value2):
#         print("The hashes match. File integrity verified.")
    