from flask import Flask, render_template, request
from gen import generator

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/gen', methods=['GET', 'POST'])
def get_input():
    message = None
    if request.method == 'POST':
        user_input = request.form['user_input']
        result = generator(user_input)
        message = f"result: \n{result}"
    return render_template('generate.html', message=message)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)
