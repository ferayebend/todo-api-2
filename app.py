from flask import Flask, jsonify, request, abort, url_for
from celery import Celery 

from random import randint
from time import sleep

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name,
                broker=app.config['CELERY_BROKER_URL'],
                backend=app.config['CELERY_RESULT_BACKEND'])


tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

@app.route('/todo/api/v1.0/notes', methods=['GET'])
def get_notes():
    return jsonify(tasks)

@app.route('/todo/api/v1.0/notes', methods=['POST'])
def create_note():
    if not request.json or not 'title' in request.json:
        abort(404)

@app.route('/todo/api/v1.0/notes/<int:id>', methods=['GET'])
def get_note(id):
    # query db
    try:
        task = tasks[id]
    except:
        task = {}
    return jsonify(task)

@app.route('/todo/api/v1.0/notes/random',methods=['GET'])
def random_task():
    task = long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus',task_id=task.id)}

@app.route('/status/<task_id>',methods=['GET'])
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        print(task.state)
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'title' in task.info:
           response['result'] = task.info
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@celery.task(bind=True)
def long_task(self):
    titles = ['note1', 'note2', 'note3']
    descriptions = ['description1', 'desc2', 'baska bi description']

    found_task = {'title':titles[randint(0,len(titles)-1)],
                  'description':descriptions[randint(0,len(descriptions))-1]}

    self.update_state(state='PROGRESS', meta={'status':'querying...'})
    sleep(15)
    return found_task

if __name__ == "__main__":
    app.run(debug=True)
