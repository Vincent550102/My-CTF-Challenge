from flask import Flask, request, send_from_directory, send_file, render_template_string
import subprocess
import os

app = Flask(__name__, static_folder='static')

def get_os():
    import ctypes.wintypes
    v = ctypes.windll.kernel32.GetVersion()
    return f"Windows {v & 0xFF}.{(v >> 8) & 0xFF}"

class User:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name

@app.route('/')
def index():
    with open('static/index.html', encoding='utf-8') as f:
        return render_template_string(f.read(), os_info=get_os())

@app.route('/api/preview', methods=['POST'])
def preview():
    data = request.get_json()
    url = data.get('url', '')
    user = User(data.get('username', 'Guest'))
    
    result = subprocess.run([r'.\lib\curl.exe', url], capture_output=True, text=True, encoding='utf-8', errors='replace')
    content = result.stdout or result.stderr
    
    try:
        return content.format(user=user)
    except:
        return content

@app.route('/api/templates/<name>')
def get_template(name):
    try:
        return send_file(f'templates/{name}.html')
    except Exception as e:
        return f'Template not found: {e}', 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
