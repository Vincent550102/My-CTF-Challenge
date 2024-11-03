from flask import Flask, render_template_string, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return "Hello, World! <br><a href='/SsTiMe'>SSTI me</a> :/"


@app.route('/SsTiMe', methods=['GET'])
def showip():
    # WOW! There has a SSTI in Flask!!!
    q = request.args.get('q', "'7'*7")

    # prevent smuggling bad payloads!
    request.args = {}
    request.headers = {}
    request.cookies = {}
    request.data = {}
    request.query_string = b"#"+request.query_string

    if any([x in "._.|||" for x in q]) or len(q) > 88:
        return "Too long for me :/ my payload less than 73 chars"
    print(request.query_string, flush=True)

    res = render_template_string(f"{{{{{q}}}}}",
                                 # TODO: just for debugging, remove this in production
                                 breakpoint=breakpoint,
                                 str=str
                                 )

    # oops, I just type 'res' not res qq
    return 'res=7777777'
