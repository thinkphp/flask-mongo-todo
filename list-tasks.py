from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['task_manager']

# List all tasks
tasks = list(db.tasks.find())
for task in tasks:
    print(task)

# Count tasks
count = db.tasks.count_documents({})
print(f"Total tasks: {count}")
