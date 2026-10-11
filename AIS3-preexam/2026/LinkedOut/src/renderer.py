import jinja2
from flask import Flask, jsonify, request
from jinja2.sandbox import SandboxedEnvironment

from lib import admin_models


assert jinja2.__version__ == "3.1.5"

app = Flask(__name__)
env = SandboxedEnvironment(autoescape=False)


class Renderer:
    version = "linkedout-renderer/jinja-" + jinja2.__version__

    def render(self, body, user):
        return env.from_string(body).render(
            user=user,
            renderer=self,
        )


@app.post("/render")
def render_post():
    data = request.get_json(silent=True) or {}
    body = data.get("body", "")
    user = data.get("user", {})
    try:
        rendered = Renderer().render(body, user)
    except Exception as exc:
        rendered = f"render error: {exc.__class__.__name__}"
    return jsonify({"rendered": rendered})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
