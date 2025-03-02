from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  description TEXT,
                  status TEXT DEFAULT 'pending',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Helper function to connect to database
def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row  # This allows us to return rows as dictionaries
    return conn

# Create a new task
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO tasks (title, description) VALUES (?, ?)',
              (title, description))
    conn.commit()
    
    task_id = c.lastrowid
    conn.close()
    
    return jsonify({
        'id': task_id,
        'title': title,
        'description': description,
        'status': 'pending',
        'message': 'Task created successfully'
    }), 201

# Get all tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    tasks = c.fetchall()
    conn.close()
    
    tasks_list = [dict(task) for task in tasks]
    return jsonify(tasks_list), 200

# Get a single task
@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = c.fetchone()
    conn.close()
    
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
        
    return jsonify(dict(task)), 200

# Update a task
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    status = data.get('status')
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = c.fetchone()
    
    if task is None:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404
    
    # Update only provided fields
    update_fields = []
    values = []
    
    if title:
        update_fields.append('title = ?')
        values.append(title)
    if description is not None:  # Allow empty string
        update_fields.append('description = ?')
        values.append(description)
    if status:
        update_fields.append('status = ?')
        values.append(status)
    
    if update_fields:
        values.append(task_id)
        query = f'UPDATE tasks SET {", ".join(update_fields)} WHERE id = ?'
        c.execute(query, values)
        conn.commit()
    
    c.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    updated_task = c.fetchone()
    conn.close()
    
    return jsonify(dict(updated_task)), 200

# Delete a task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = c.fetchone()
    
    if task is None:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404
    
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Task deleted successfully'}), 200

if __name__ == '__main__':
    init_db()  # Initialize the database when the app starts
    app.run(debug=True, host='0.0.0.0', port=5000)