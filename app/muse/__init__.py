import json
from flask import Flask, request
from flask import render_template
from flask_socketio import SocketIO, send, emit
from muse.models import *

app = Flask(__name__)
app.config.from_object('config')
socketio = SocketIO(app, async_mode="eventlet")
db.init_app(app)

@socketio.on('connect')
def handle_connect():
    # using send() sends a message back to a single client
    # use socketio.send() to send to all clients
    # create a new composition for this session
    composition = Composition()
    db.session.add(composition)
    db.session.commit()

    # emit a message containing this sessions composition id
    emit('composition_init', {'composition_id' : composition.id})

@socketio.on('save_composition')
def handle_save_composition(data):
    d = json.loads(data)
    if 'composition_id' in d:
        print(d['composition_id'])
        composition = Composition.query.filter_by(id=d['composition_id']).first()
        if composition is not None:
            if 'sequences' in d:
                for sequence in d['sequences']:
                    instrument = sequence['instrument']
                    shape = sequence['shape']
                    toggles = sequence['toggles']
                    has_seq = False
                    for seq in composition.sequences.all():
                        if seq.instrument == instrument:
                            has_seq = True
                            print('Sequence for {} exists'.format(instrument))
                    if not has_seq:
                        print('Creating new sequence')
                        db.session.add(Sequence(shape[0], shape[1], toggles, instrument, composition))
                        db.session.commit()

@socketio.on('get_sequences')
def handle_get_sequences():
    sequences = Sequence.query.all()
    for sequence in sequences:
        print(sequence)

@socketio.on('sequence_update')
def handle_sequence_update(data):
    pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index2')
def index2():
    return render_template('index_2.html')

if __name__ == '__main__':
    socketio.run(app, debug=app.config['DEBUG'])
