import cgi

from flask import flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import safe_str_cmp
try:
    import ujson as json
except ImportError:
    import json

from messenger import app

@app.route('/')
def home():
    total = g.redis.get('question_counter')
    if total is not None:
        keys = ['message:{}'.format(i) for i in xrange(1, int(total)+1)]
        questions = g.redis.mget(keys)
        #return repr(questions)
    else:
        questions = False
    return render_template('home.html', questions=questions)


@app.route('/listen')
def listen():
    questions = session.get('messages')
    if questions is not None and isinstance(questions, list):
        rv = []
        for q in questions:
            key = 'message:{}'.format(q)
            rv.append((q, g.redis.get(key)))
    else:
        rv = []
    return render_template('listen.html', questions=rv)


@app.route('/question/<int:id>')
def question(id):
    question = g.redis.get('message:{}'.format(id))
    resp_count = g.redis.get('response:{}:count'.format(id))
    if resp_count is not None:
        keys = ['response:{}:{}'.format(id, i) 
                            for i in xrange(1, int(resp_count)+1)]
        responses = g.redis.mget(keys)
    else:
        responses = False
    resp_type = request.headers.get('X-Requested-With')
    if resp_type is not None and 'XMLHttpRequest' == resp_type:
        rv = {'question': cgi.escape(question, True), 'id': id}
        if responses:
            rv['responses'] = []
            for i, r in enumerate(responses):
                rv['responses'].append({
                    'id': i+1,
                    'content': cgi.escape(r, True)
                })
        return json.dumps(rv)
    return render_template('question.html', 
                          id=id, question=question, responses=responses)
   
    
@app.route('/add-question', methods=['POST'])
def add_message():
    try:
        token, uses = session.get('csrf', '').split(':', 1)
    except:
        flash('Whoa! Looks like there was a problem', 'error')
        return redirect(url_for('home'))
    else:
        _token = request.form.get('_token', '')
        _token, uses = _token.split(':', 1)
        if not safe_str_cmp(token, _token) or not int(uses) <= 10:
            flash('Looks like there was a problem', 'error')
            return redirect(url_for('home'))
        else:
            session['csrf'] = '{}:{}'.format(token, int(uses) + 1)
    
    msg = request.form.get('your-question')
    if msg is None or '' == msg:
        flash('Please ask a question', 'warning')
        return redirect(url_for('home'))
    
    count = g.redis.incr('question_counter')
    if 'messages' not in session:
        session['messages'] = [count]
    else:
        session['messages'].append(count)
    
    g.redis.set('message:{}'.format(count), msg)
    
    flash('Your question has been asked, just hang out here (or come back '
        'later for your answers')
    return redirect(url_for('listen'))


@app.route('/add-response', methods=['POST'])
def add_response():
    try:
        token, uses = session.get('csrf', '').split(':', 1)
    except:
        flash('Whoa! Looks like there was a problem', 'error')
        return redirect(url_for('home'))
    else:
        _token = request.form.get('_token', '')
        _token, uses = _token.split(':', 1)
        if not safe_str_cmp(token, _token) or not int(uses) <= 10:
            flash('Looks like there was a problem', 'error')
            return redirect(url_for('home'))
        else:
            session['csrf'] = '{}:{}'.format(token, int(uses) + 1)
    
    qid = request.form.get('question', 0)
    resp = request.form.get('your-answer', '')
    if resp is None or '' == resp:
        flash('Whoa there, enter a response.', 'error')
        return redirect(url_for('question', id=qid))
    
    
    resp_count = g.redis.incr('response:{}:count'.format(qid))
    
    g.redis.set('response:{}:{}'.format(qid, resp_count), resp)
    flash('Your response has been added!')
    return redirect(url_for('question', id=qid))
    
