
import base64

from flask import Flask, request, render_template, make_response, redirect, url_for, Response
from dotenv import load_dotenv
import os
import socket
import re

load_dotenv()

app = Flask(__name__)

BOT_HOST = os.getenv('BOT_HOST')
BOT_PORT = os.getenv('BOT_PORT')


@app.route('/')
def home():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))
    return render_template('home.html', username=username)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))

    if request.method == 'POST':
        message = request.form.get('message')
        message_encoded = base64.b64encode(message.encode()).decode()
        return redirect(url_for('profile', message=message_encoded))

    return render_template('profile.html', username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        resp = make_response(redirect(url_for('home')))
        resp.set_cookie('username', user, httponly=True)
        return resp
    return render_template('login.html', username=request.cookies.get('username'))


@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('username', '', expires=0)
    return resp


@app.route('/report', methods=['GET', 'POST'])
def report():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))
    if request.method == 'POST':
        url = request.form.get('url')
        host = request.host.replace(".", "\\.")
        print(host)
        if not url or not re.match(f'^https?://{host}', url):
            return Response('Invalid URL', status=400)

        print(f'[+] Sending {url} to bot')

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((BOT_HOST, int(BOT_PORT)))
            client.sendall(url.encode())

            response = b''
            while True:
                data = client.recv(4096)
                if not data:
                    break
                response += data

            client.close()

            return Response(response.decode(), mimetype='text/plain')

        except Exception as e:
            print(e)
            return Response('Something is wrong...', status=500)
    return render_template('report.html', username=username)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
