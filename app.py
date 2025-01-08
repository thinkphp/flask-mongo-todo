from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import logging
import sys

# Configure logging to see all messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Direct MongoDB configuration
MONGO_URI = 'mongodb://localhost:27017'
DB_NAME = 'task_manager'

def get_db():
    """Get MongoDB database connection"""
    try:
        # Add timeout to fail fast if MongoDB is not available
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Test the connection
        client.server_info()
        logger.info("Successfully connected to MongoDB")
        return client[DB_NAME]
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise

def init_db():
    """Initialize MongoDB database if needed"""
    try:
        db = get_db()
        # Create an index on the title field (optional)
        db.tasks.create_index('title')
        logger.info("MongoDB initialization successful")
        # Try to insert a test document to verify write permissions
        test_result = db.tasks.insert_one({'test': True})
        db.tasks.delete_one({'_id': test_result.inserted_id})
        logger.info("Database write test successful")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

@app.route('/')
def index():
    """Display all tasks"""
    try:
        db = get_db()
        tasks = list(db.tasks.find().sort([('completed', 1), ('_id', -1)]))
        for task in tasks:
            task['_id'] = str(task['_id'])
        return render_template('index.html', tasks=tasks)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return f"Database error occurred: {str(e)}", 500

@app.route('/add', methods=['GET', 'POST'])
def add():
    """Add a new task"""
    if request.method == 'POST':
        try:
            task = {
                'title': request.form['title'],
                'description': request.form['description'],
                'completed': False
            }
            db = get_db()
            db.tasks.insert_one(task)
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            return f"Error adding task: {str(e)}", 500
    return render_template('add.html')

@app.route('/update/<task_id>', methods=['GET', 'POST'])
def update(task_id):
    """Update an existing task"""
    try:
        db = get_db()
        if request.method == 'POST':
            db.tasks.update_one(
                {'_id': ObjectId(task_id)},
                {
                    '$set': {
                        'title': request.form['title'],
                        'description': request.form['description']
                    }
                }
            )
            return redirect(url_for('index'))

        task = db.tasks.find_one({'_id': ObjectId(task_id)})
        if task:
            task['_id'] = str(task['_id'])
            return render_template('update.html', task=task)
        return "Task not found", 404
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return f"Error updating task: {str(e)}", 500

@app.route('/toggle/<task_id>')
def toggle_completion(task_id):
    """Toggle task completion status"""
    try:
        db = get_db()
        task = db.tasks.find_one({'_id': ObjectId(task_id)})
        if task:
            db.tasks.update_one(
                {'_id': ObjectId(task_id)},
                {'$set': {'completed': not task.get('completed', False)}}
            )
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error toggling task: {e}")
        return f"Error toggling task: {str(e)}", 500

@app.route('/delete/<task_id>', methods=['GET'])
def delete(task_id):
    """Delete a task"""
    try:
        db = get_db()
        db.tasks.delete_one({'_id': ObjectId(task_id)})
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return f"Error deleting task: {str(e)}", 500

if __name__ == '__main__':
    try:
        logger.info("Initializing MongoDB connection...")
        init_db()
        logger.info("Starting Flask server...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)
