from flask import Flask, render_template, request, send_file
import subprocess

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/howtogen')
def howtogen():
    return send_file('gen.py', mimetype='text/plain', as_attachment=False)


@app.route('/hint')
def hint():
    return send_file('Dockerfile', mimetype='text/plain', as_attachment=False)


@app.route('/gen', methods=['GET', 'POST'])
def get_input():
    message = None
    if request.method == 'POST':
        user_input = request.form['user_input']
        if " " in user_input:
            result = "evil input"
        else:
            result = subprocess.run(
                f"python gen.py {user_input}", shell=True, capture_output=True, text=True).stdout.replace('\\n', '')
        message = f"result: \n{result}"
    return render_template('generate.html', message=message)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)
