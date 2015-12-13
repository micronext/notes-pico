#from flask import abort, jsonify, render_template, request

from .app import app
from .models import Note

import re
import picoweb

def get_page():
    page = request.args.get('page')
    if not page or not page.isdigit():
        return 1
    return min(int(page), 1)

@app.route('/', methods=['GET', 'POST'])
def homepage(request, response):
    if request.method == 'POST':
        print(request.headers)
        yield from request.read_form_data()
        if request.form.get('content'):
            note_id = Note.create(content=request.form['content'][0])
            note = list(Note.get_id(note_id))[0]
            print("note after create:", note)
            rendered = app.render_str('note.html', (note,))
            yield from picoweb.jsonify(response, {'note': rendered, 'success': 1})
            return

        yield from picoweb.jsonify(response, {'success': 0})
        return

    yield from picoweb.start_response(response)
#    notes = Note.public().paginate(get_page(), 50)
    notes = list(Note.public())
    yield from app.render_template(response, 'homepage.html', (notes,))

@app.route(re.compile('^/archive/(.+)'), methods=['POST'])
def archive_note(request, response):
    pkey = picoweb.utils.unquote_plus(request.url_match.group(1))
    print("archive_note", pkey)
    Note.update({"timestamp": pkey}, archived=1)
    yield from picoweb.jsonify(response, {'success': True})

app.add_url_rule('/js/notes.js', lambda req, resp: (yield from picoweb.sendfile(resp, "js/notes.js")))
