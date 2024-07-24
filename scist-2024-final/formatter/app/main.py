from flask import (
    Flask,
    request,
    render_template,
    render_template_string,
)

app = Flask(__name__)
app.secret_key = open("/flag").read()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        rawtext = request.form.get("rawtext")
        mappings = {"{{": "", "}}": "", ".": "...", "(": ""}
        for mapping in mappings:
            rawtext = rawtext.replace(mapping, mappings[mapping])
        rawtext = "😺 " + rawtext + " 😺"
        return render_template_string(rawtext)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
