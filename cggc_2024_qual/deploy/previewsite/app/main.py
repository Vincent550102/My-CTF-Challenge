from flask import Flask, request, redirect, render_template, session, url_for, flash
import urllib.request
import urllib.error
import urllib.parse
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

users = {'guest': 'guest'}

def send_request(url, follow=True):
    try:
        response =  urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        response = e
    redirect_url = response.geturl()
    if redirect_url != url and follow:
        return send_request(redirect_url, follow=False)
    return response.read().decode('utf-8')


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next', url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            session['username'] = username
            flash('login success')
            return redirect(next_url)
        else:
            error = 'login failed'
            return render_template('login.html', error=error, next=next_url)
    return render_template('login.html', next=next_url)

@app.route('/logout')
def logout():
    session.pop('username', None)
    next_url = request.args.get('next', url_for('index'))
    return redirect(next_url)

@app.route('/fetch', methods=['GET', 'POST'])
def fetch():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            flash('Please provide a URL.')
            return render_template('fetch.html')
        try:
            if not url.startswith(os.getenv("DOMAIN", "http://previewsite/")):
                raise ValueError('badhacker')
            resp = send_request(url)
            return render_template('fetch.html', content=resp)
        except Exception as e:
            error = f'error：{e}'
            return render_template('fetch.html', error=error)
    return render_template('fetch.html')

@app.route('/')
def index():
    username = session.get('username')
    return render_template('index.html', username=username)
