from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
import os
import hashlib
import initializing_data as init_data

# Import your integration module
import integration as logic

# Import database functions
from doc_hash_database import (
    create_tables, 
    new_user, 
    add_document, 
    get_user_documents, 
    get_user_document_hashes,
    con
)


app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

create_tables()

def get_user_by_email(email):
    result = con.execute("""
        SELECT user_id, username, email, Password 
        FROM users_duckdb 
        WHERE email = ?
    """, [email]).fetchone()
    return result


@app.route('/', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    
    # Get user documents and display
    user_docs = get_user_documents(user_id)
    uploaded_files = []
    
    for doc in user_docs:
        uploaded_files.append({
            'title': doc[2],  # title
            'hash': doc[1][:16] + '...',  # Document_Hash (short preview)
            'content_preview': doc[3][:100] + '...' if len(doc[3]) > 100 else doc[3]  # content preview
        })
    
    return render_template('dashboard.html', 
                         uploaded_files=uploaded_files,
                         username=session.get('user'))


# AJAX endpoint for file upload with progress
@app.route('/upload_files', methods=['POST'])
def upload_files():
    """
    Handle file uploads via AJAX with progress feedback
    """
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session.get('user_id')
    files = request.files.getlist('files')
    
    results = {
        'total': len(files),
        'uploaded': 0,
        'skipped': 0,
        'errors': 0,
        'details': []
    }
    
    for idx, file in enumerate(files):
        if file and file.filename:
            try:
                # Save file
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                
                # Read content
                with open(filepath, 'rb') as f:
                    file_content = f.read()
                
                try:
                    content_text = file_content.decode('utf-8', errors='ignore')
                except:
                    content_text = f"Binary file: {file.filename}"
                
                # Calculate hash
                document_hash = hashlib.sha256(file_content).hexdigest()
                
                # Check if document exists and add to Neo4j
                doc_exists = logic.if_doc_exists(filepath)
                
                if not doc_exists:
                    # ✅ FIXED: Use correct parameter order
                    # add_document(doc_hash, user_id, title, content)
                    add_document(
                        document_hash,  # doc_hash
                        user_id,        # user_id
                        file.filename,  # title
                        content_text    # content
                    )
                    results['uploaded'] += 1
                    results['details'].append({
                        'filename': file.filename,
                        'status': 'uploaded',
                        'message': 'Successfully uploaded and indexed to Neo4j'
                    })
                    print(f"✓ New document added to database: {file.filename}")
                else:
                    results['skipped'] += 1
                    results['details'].append({
                        'filename': file.filename,
                        'status': 'skipped',
                        'message': 'Document already exists in Neo4j'
                    })
                    print(f"⚠ Document already exists: {file.filename}")
                    
            except Exception as e:
                results['errors'] += 1
                results['details'].append({
                    'filename': file.filename,
                    'status': 'error',
                    'message': str(e)
                })
                print(f"❌ Error processing {file.filename}: {e}")
                import traceback
                traceback.print_exc()
    
    return jsonify(results)


@app.route('/chat', methods=['POST'])
def chat():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    user_message = data.get('message', '')
    user_id = session.get('user_id')
    
    # Get response from chatbot with Neo4j context
    response = logic.bot_chat_with_docs(user_message, user_id)
    print(f"DEBUG IN APP.PY - Response: {response}, Type: {type(response)}")
    
    return jsonify({
        'response': response,
        'status': 'success'
    })


@app.route('/chat/history', methods=['GET'])
def chat_history():
    """Get chat history for current user"""
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session.get('user_id')
    limit = request.args.get('limit', 10, type=int)
    
    history = logic.get_user_conversation_history(user_id, limit)
    
    return jsonify({
        'history': history,
        'status': 'success'
    })


@app.route('/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history for current user"""
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session.get('user_id')
    
    # Clear both memory and Neo4j history
    logic.clear_user_chat_history(user_id)
    logic.clear_user_neo4j_history(user_id)
    
    return jsonify({
        'message': 'Chat history cleared',
        'status': 'success'
    })


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        existing_user = get_user_by_email(email)
        
        if not existing_user:
            user_id = new_user(username, password, email)
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email already exists', 'error')
    
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = get_user_by_email(email)
        
        if user and user[3] == password:
            session['user'] = user[1]
            session['user_id'] = user[0]
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')


if __name__ == '__main__':
    init_data.clear_neo4j_database()
    init_data.clear_text_file('document_hashes.txt')
    app.run(debug=True, use_reloader=False)