import hashlib
import hmac
import os
import secrets
import sqlite3
import threading
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import docker
import requests
from docker.errors import APIError, DockerException, NotFound
from flask import Flask, redirect, render_template_string, request, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix


CTFD_URL = os.environ.get("CTFD_URL", "https://pre-exam.ais3.org/").rstrip("/")
PUBLIC_DOMAIN = os.environ.get("PUBLIC_DOMAIN", "chals1.ais3.org")
PUBLIC_SCHEME = os.environ.get("PUBLIC_SCHEME", "http")
PORT_START = int(os.environ.get("PORT_START", "36000"))
PORT_END = int(os.environ.get("PORT_END", "37000"))
INSTANCE_TTL_SECONDS = int(os.environ.get("INSTANCE_TTL_SECONDS", "3600"))
WEB_IMAGE = os.environ.get("WEB_IMAGE", "linkedout-web:latest")
RENDERER_IMAGE = os.environ.get("RENDERER_IMAGE", "linkedout-renderer:latest")
WEB_NANO_CPUS = int(os.environ.get("WEB_NANO_CPUS", "500000000"))
RENDERER_NANO_CPUS = int(os.environ.get("RENDERER_NANO_CPUS", "250000000"))
FLAG_PATH = os.environ.get("LINKEDOUT_FLAG_PATH", "/srv/linkedout/flag.txt")
DB_PATH = os.environ.get("INSTANCER_DB_PATH", "/data/instancer.db")
INSTANCE_PREFIX = os.environ.get("INSTANCE_PREFIX", "linkedout")
CLEANUP_INTERVAL_SECONDS = int(os.environ.get("CLEANUP_INTERVAL_SECONDS", "60"))
RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", "60"))
LOGIN_RATE_LIMIT = int(os.environ.get("LOGIN_RATE_LIMIT", "12"))
INSTANCE_RATE_LIMIT = int(os.environ.get("INSTANCE_RATE_LIMIT", "20"))
CTFD_AUTH_SCHEMES = tuple(
    scheme.strip()
    for scheme in os.environ.get("CTFD_AUTH_SCHEMES", "Token,Bearer").split(",")
    if scheme.strip()
)
CTFD_ADMIN_TOKEN = os.environ.get("CTFD_ADMIN_TOKEN", "").strip()
CTFD_SITE_PASSWORD = os.environ.get("CTFD_SITE_PASSWORD", "").strip()
CTFD_SITE_PASSWORD_COOKIE = os.environ.get("CTFD_SITE_PASSWORD_COOKIE", "site_password").strip()
TRUST_PROXY = os.environ.get("TRUST_PROXY", "").lower() in {"1", "true", "yes"}


app = Flask(__name__)
app.secret_key = os.environ.get("INSTANCER_SECRET_KEY") or secrets.token_hex(32)
if TRUST_PROXY:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

docker_client = docker.from_env()
db_lock = threading.RLock()
instance_lock = threading.RLock()
rate_lock = threading.RLock()
rate_buckets = defaultdict(deque)


class RateLimitError(ValueError):
    pass


SCHEMA = """
CREATE TABLE IF NOT EXISTS instances (
    user_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    token_digest TEXT NOT NULL,
    port INTEGER NOT NULL UNIQUE,
    web_name TEXT NOT NULL,
    renderer_name TEXT NOT NULL,
    network_name TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL
)
"""


PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LinkedOut Instancer</title>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; background: #f3f2ef; color: #191919; }
    header { background: #0a66c2; color: white; padding: 16px 24px; font-weight: 700; }
    main { max-width: 860px; margin: 32px auto; padding: 0 18px; }
    .panel { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 22px; margin-bottom: 18px; }
    h1 { margin: 0 0 8px; font-size: 24px; }
    h2 { margin: 0 0 12px; font-size: 18px; }
    p { line-height: 1.5; }
    label { display: block; font-weight: 700; margin-bottom: 8px; }
    input[type=password] { width: 100%; box-sizing: border-box; font: inherit; padding: 10px; border: 1px solid #aaa; border-radius: 6px; }
    button, .button { display: inline-block; border: 0; border-radius: 20px; background: #0a66c2; color: white; padding: 10px 18px; font-weight: 700; text-decoration: none; cursor: pointer; }
    button.secondary { background: #eef3f8; color: #0a66c2; }
    button.danger { background: #b24020; }
    .row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
    .muted { color: #666; }
    .error { color: #b24020; font-weight: 700; }
    .ok { color: #057642; font-weight: 700; }
    code { background: #eef3f8; padding: 2px 6px; border-radius: 4px; }
    .url { font-size: 18px; word-break: break-all; }
    .meta { display: grid; grid-template-columns: 160px 1fr; gap: 8px; }
  </style>
</head>
<body>
  <header>LinkedOut Instancer</header>
  <main>
    {% if error %}
    <section class="panel"><p class="error">{{ error }}</p></section>
    {% endif %}

    {% if not user %}
    <section class="panel">
      <h1>Start Your Instance</h1>
      <p class="muted">Paste your CTFd token. The token is used once to verify your account.</p>
      <form method="post" action="{{ url_for('login') }}">
        <input type="hidden" name="csrf" value="{{ csrf }}">
        <label for="token">CTFd token</label>
        <input id="token" name="token" type="password" autocomplete="off" required>
        <p><button type="submit">Continue</button></p>
      </form>
    </section>
    {% else %}
    <section class="panel">
      <div class="row">
        <h1>{{ user.name }}</h1>
        <form method="post" action="{{ url_for('logout') }}">
          <input type="hidden" name="csrf" value="{{ csrf }}">
          <button class="secondary" type="submit">Log out</button>
        </form>
      </div>
      <p class="muted">One active LinkedOut instance is available per CTFd account.</p>
    </section>

    <section class="panel">
      <h2>Instance</h2>
      {% if instance %}
        <p class="ok">Running</p>
        <p class="url"><a href="{{ instance.url }}" target="_blank" rel="noopener">{{ instance.url }}</a></p>
        <div class="meta">
          <span class="muted">Port</span><code>{{ instance.port }}</code>
          <span class="muted">Remaining</span><span data-countdown data-expires="{{ instance.expires_at }}">{{ instance.remaining }}</span>
          <span class="muted">Created</span><span>{{ instance.created_at }}</span>
        </div>
        <p class="row">
          <form method="post" action="{{ url_for('renew') }}">
            <input type="hidden" name="csrf" value="{{ csrf }}">
            <button type="submit">Renew</button>
          </form>
          <form method="post" action="{{ url_for('stop') }}">
            <input type="hidden" name="csrf" value="{{ csrf }}">
            <button class="danger" type="submit">Stop</button>
          </form>
        </p>
      {% else %}
        <p class="muted">No active instance.</p>
        <form method="post" action="{{ url_for('start') }}">
          <input type="hidden" name="csrf" value="{{ csrf }}">
          <button type="submit">Start instance</button>
        </form>
      {% endif %}
    </section>
    {% endif %}
  </main>
  <script>
    function formatRemaining(seconds) {
      seconds = Math.max(0, Math.floor(seconds));
      const minutes = Math.floor(seconds / 60);
      const sec = seconds % 60;
      const hours = Math.floor(minutes / 60);
      const min = minutes % 60;
      if (hours > 0) {
        return `${hours}h ${min}m`;
      }
      return `${min}m ${sec}s`;
    }

    function updateCountdowns() {
      const now = Math.floor(Date.now() / 1000);
      document.querySelectorAll("[data-countdown]").forEach((node) => {
        const expiresAt = Number(node.dataset.expires);
        if (!Number.isFinite(expiresAt)) {
          return;
        }
        node.textContent = formatRemaining(expiresAt - now);
      });
    }

    updateCountdowns();
    setInterval(updateCountdowns, 1000);
  </script>
</body>
</html>
"""


@contextmanager
def db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with db_lock:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute(SCHEMA)
            yield conn
            conn.commit()
        finally:
            conn.close()


def now():
    return int(time.time())


def client_key():
    return request.remote_addr or "unknown"


def check_rate_limit(scope, key, limit):
    if limit <= 0:
        return
    timestamp = now()
    cutoff = timestamp - RATE_LIMIT_WINDOW_SECONDS
    bucket_key = (scope, key)
    with rate_lock:
        bucket = rate_buckets[bucket_key]
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= limit:
            retry_after = max(1, bucket[0] + RATE_LIMIT_WINDOW_SECONDS - timestamp)
            raise RateLimitError(f"too many requests; try again in {retry_after}s")
        bucket.append(timestamp)


def check_login_rate_limit():
    check_rate_limit("login", client_key(), LOGIN_RATE_LIMIT)


def check_instance_rate_limit(user):
    check_rate_limit("instance-ip", client_key(), INSTANCE_RATE_LIMIT)
    check_rate_limit("instance-user", user["id"], INSTANCE_RATE_LIMIT)


def csrf_token():
    token = session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(24)
        session["csrf"] = token
    return token


def require_csrf():
    if request.form.get("csrf") != session.get("csrf"):
        raise ValueError("invalid request token")


def digest_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def ctfd_cookies():
    if not CTFD_SITE_PASSWORD:
        return None
    return {CTFD_SITE_PASSWORD_COOKIE: CTFD_SITE_PASSWORD}


def ctfd_headers(token, scheme="Token"):
    return {
        "Authorization": f"{scheme} {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def parse_ctfd_json(resp, label):
    if resp.status_code in {301, 302, 303, 307, 308}:
        location = resp.headers.get("Location", "")
        raise ValueError(f"{label}:{resp.status_code} redirect to {location or 'unknown location'}")
    content_type = resp.headers.get("Content-Type", "")
    if resp.status_code != 200:
        raise ValueError(f"{label}:{resp.status_code} {content_type or 'unknown content-type'}")
    if "application/json" not in content_type:
        raise ValueError(f"{label}:200 non-json {content_type or 'unknown content-type'}")
    try:
        payload = resp.json()
    except ValueError as exc:
        raise ValueError(f"{label}:200 invalid-json") from exc
    if payload.get("success") is False:
        raise ValueError(f"{label}:api returned success=false")
    return payload


def admin_ctfd_get(path, params=None):
    if not CTFD_ADMIN_TOKEN:
        raise ValueError("CTFD_ADMIN_TOKEN is not configured")
    try:
        resp = requests.get(
            f"{CTFD_URL}{path}",
            params=params,
            headers=ctfd_headers(CTFD_ADMIN_TOKEN),
            cookies=ctfd_cookies(),
            allow_redirects=False,
            timeout=8,
        )
    except requests.RequestException as exc:
        raise ValueError(f"admin:{exc.__class__.__name__}") from exc
    return parse_ctfd_json(resp, f"admin:{path}")


def pagination_next(meta):
    pagination = (meta or {}).get("pagination") or {}
    page = pagination.get("page")
    pages = pagination.get("pages")
    try:
        if page is not None and pages is not None and int(page) < int(pages):
            return int(page) + 1
    except (TypeError, ValueError):
        return None
    return None


def find_ctfd_token_with_admin(token):
    page = 1
    saw_value_field = False
    while True:
        payload = admin_ctfd_get(
            "/api/v1/tokens",
            params={"page": page, "per_page": 100},
        )
        rows = payload.get("data") or []
        for row in rows:
            token_id = row.get("id")
            if token_id is None:
                continue
            detail = admin_ctfd_get(f"/api/v1/tokens/{token_id}")
            data = detail.get("data") or {}
            if "value" in data:
                saw_value_field = True
            if data.get("value") == token:
                return data
        page = pagination_next(payload.get("meta"))
        if page is None:
            break
    if not saw_value_field:
        raise ValueError("CTFd /api/v1/tokens did not expose token values to the admin API")
    raise ValueError("CTFd token was not found")


def verify_ctfd_token_with_admin(token):
    row = find_ctfd_token_with_admin(token)
    user_id = row.get("user_id")
    if user_id is None:
        raise ValueError("CTFd token record did not include a user id")

    payload = admin_ctfd_get(f"/api/v1/users/{user_id}")
    data = payload.get("data") or {}
    name = data.get("name") or data.get("email") or f"user-{user_id}"
    return {"id": str(user_id), "name": str(name)}


def instance_suffix(user_id):
    key = app.secret_key.encode()
    return hmac.new(key, str(user_id).encode(), hashlib.sha256).hexdigest()[:16]


def container_names(user_id):
    suffix = instance_suffix(user_id)
    return {
        "web": f"{INSTANCE_PREFIX}_{suffix}_web",
        "renderer": f"{INSTANCE_PREFIX}_{suffix}_renderer",
        "network": f"{INSTANCE_PREFIX}_{suffix}_net",
    }


def instance_labels(user_id, port):
    return {
        "linkedout.instancer": "1",
        "linkedout.user_id": str(user_id),
        "linkedout.host_port": str(port),
    }


def verify_ctfd_token(token):
    if not token:
        raise ValueError("missing CTFd token")

    errors = []
    for scheme in CTFD_AUTH_SCHEMES:
        try:
            resp = requests.get(
                f"{CTFD_URL}/api/v1/users/me",
                headers=ctfd_headers(token, scheme),
                cookies=ctfd_cookies(),
                allow_redirects=False,
                timeout=8,
            )
        except requests.RequestException as exc:
            errors.append(exc.__class__.__name__)
            continue

        if resp.status_code == 200:
            try:
                payload = parse_ctfd_json(resp, scheme)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            data = payload.get("data") or {}
            user_id = data.get("id")
            if user_id is None:
                raise ValueError("CTFd did not return a user id")
            name = data.get("name") or data.get("email") or f"user-{user_id}"
            return {"id": str(user_id), "name": str(name)}
        if resp.status_code in {301, 302, 303, 307, 308}:
            location = resp.headers.get("Location", "")
            errors.append(f"{scheme}:{resp.status_code} redirect to {location or 'unknown location'}")
            continue
        content_type = resp.headers.get("Content-Type", "")
        errors.append(f"{scheme}:{resp.status_code} {content_type or 'unknown content-type'}")

    direct_error = (
        "CTFd token verification failed. "
        "If every scheme redirects to /login, CTFd did not accept the API token; "
        "check the token and make sure the CTFd reverse proxy forwards the Authorization header. "
        f"Details: {', '.join(errors)}"
    )

    if CTFD_ADMIN_TOKEN:
        try:
            return verify_ctfd_token_with_admin(token)
        except ValueError as exc:
            raise ValueError(
                f"{direct_error} Admin-token fallback also failed: {exc}"
            ) from exc

    raise ValueError(
        direct_error
    )


def current_user():
    user = session.get("user")
    if not user:
        return None
    return {"id": str(user["id"]), "name": str(user["name"])}


def get_row(user_id):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM instances WHERE user_id = ?",
            (str(user_id),),
        ).fetchone()


def active_ports(conn):
    cutoff = now()
    rows = conn.execute("SELECT port FROM instances WHERE expires_at > ?", (cutoff,)).fetchall()
    ports = {int(row["port"]) for row in rows}
    try:
        for container in docker_client.containers.list(
            all=True,
            filters={"label": "linkedout.instancer=1"},
        ):
            port = container.labels.get("linkedout.host_port")
            if port and port.isdigit():
                ports.add(int(port))
    except DockerException:
        pass
    return ports


def allocate_port(conn):
    used = active_ports(conn)
    for port in range(PORT_START, PORT_END + 1):
        if port not in used:
            return port
    raise RuntimeError("no instance ports available")


def remove_container(name):
    try:
        docker_client.containers.get(name).remove(force=True)
    except NotFound:
        return


def remove_network(name):
    try:
        docker_client.networks.get(name).remove()
    except NotFound:
        return
    except APIError:
        return


def destroy_instance(row):
    if row is None:
        return
    remove_container(row["web_name"])
    remove_container(row["renderer_name"])
    remove_network(row["network_name"])
    with db() as conn:
        conn.execute("DELETE FROM instances WHERE user_id = ?", (row["user_id"],))


def cleanup_expired():
    with instance_lock:
        cutoff = now()
        with db() as conn:
            rows = conn.execute("SELECT * FROM instances WHERE expires_at <= ?", (cutoff,)).fetchall()
        for row in rows:
            destroy_instance(row)


def cleanup_loop():
    while True:
        try:
            cleanup_expired()
        except Exception:
            pass
        time.sleep(CLEANUP_INTERVAL_SECONDS)


def container_alive(name):
    try:
        container = docker_client.containers.get(name)
        return container.status in {"created", "running", "restarting"}
    except NotFound:
        return False


def get_active_instance(user_id):
    with instance_lock:
        row = get_row(user_id)
        if row is None:
            return None
        if row["expires_at"] <= now():
            destroy_instance(row)
            return None
        if not container_alive(row["web_name"]) or not container_alive(row["renderer_name"]):
            destroy_instance(row)
            return None
        return row


def create_instance(user, token_digest):
    with instance_lock:
        cleanup_expired()
        existing = get_active_instance(user["id"])
        if existing is not None:
            renew_instance(user["id"])
            return get_active_instance(user["id"])

        names = container_names(user["id"])
        remove_container(names["web"])
        remove_container(names["renderer"])
        remove_network(names["network"])

        with db() as conn:
            port = allocate_port(conn)

        labels = instance_labels(user["id"], port)
        network = docker_client.networks.create(
            names["network"],
            labels=labels,
            driver="bridge",
            options={"com.docker.network.bridge.enable_ip_masquerade": "false"},
        )
        renderer = None
        web = None
        try:
            renderer = docker_client.containers.run(
                RENDERER_IMAGE,
                command="python renderer.py",
                detach=True,
                name=names["renderer"],
                network=network.name,
                user="ctf",
                environment={"SERVICE_ROLE": "renderer"},
                labels=labels,
                nano_cpus=RENDERER_NANO_CPUS,
                mem_limit="256m",
                pids_limit=128,
                read_only=True,
                tmpfs={
                    "/tmp": "rw,nosuid,nodev,noexec,size=32m",
                },
                cap_drop=["ALL"],
                security_opt=["no-new-privileges:true"],
                restart_policy={"Name": "unless-stopped"},
            )
            web = docker_client.containers.run(
                WEB_IMAGE,
                command=(
                    "sh -c 'install -m 400 -o root -g root /flag-src /run/flag "
                    "&& su ctf -s /bin/sh -c \"python app.py\"'"
                ),
                detach=True,
                name=names["web"],
                network=network.name,
                ports={"8000/tcp": ("0.0.0.0", port)},
                environment={
                    "RENDERER_URL": f"http://{names['renderer']}:5001/render",
                    "SERVICE_ROLE": "web",
                    "SECRET_KEY": secrets.token_hex(32),
                },
                volumes={FLAG_PATH: {"bind": "/flag-src", "mode": "ro"}},
                labels=labels,
                nano_cpus=WEB_NANO_CPUS,
                mem_limit="384m",
                pids_limit=192,
                read_only=True,
                tmpfs={
                    "/tmp": "rw,nosuid,nodev,noexec,size=64m",
                    "/run": "rw,nosuid,nodev,noexec,size=1m,mode=755",
                },
                restart_policy={"Name": "unless-stopped"},
            )

            created_at = now()
            expires_at = created_at + INSTANCE_TTL_SECONDS
            with db() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO instances
                    (user_id, user_name, token_digest, port, web_name, renderer_name, network_name, created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user["id"],
                        user["name"],
                        token_digest,
                        port,
                        names["web"],
                        names["renderer"],
                        names["network"],
                        created_at,
                        expires_at,
                    ),
                )
        except Exception:
            if web is not None:
                remove_container(names["web"])
            if renderer is not None:
                remove_container(names["renderer"])
            remove_network(names["network"])
            raise

        return get_active_instance(user["id"])


def renew_instance(user_id):
    with instance_lock:
        with db() as conn:
            conn.execute(
                "UPDATE instances SET expires_at = ? WHERE user_id = ?",
                (now() + INSTANCE_TTL_SECONDS, str(user_id)),
            )


def stop_instance(user_id):
    with instance_lock:
        row = get_row(user_id)
        if row is not None:
            destroy_instance(row)


def format_remaining(expires_at):
    seconds = max(0, int(expires_at) - now())
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m {sec}s"


def view_instance(row):
    if row is None:
        return None
    created_at = datetime.fromtimestamp(
        int(row["created_at"]),
        tz=timezone(timedelta(hours=8)),
    )
    return {
        "port": row["port"],
        "url": f"{PUBLIC_SCHEME}://{PUBLIC_DOMAIN}:{row['port']}/",
        "remaining": format_remaining(row["expires_at"]),
        "expires_at": int(row["expires_at"]),
        "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S UTC+8"),
    }


def render(error=None):
    user = current_user()
    instance = view_instance(get_active_instance(user["id"])) if user else None
    return render_template_string(
        PAGE,
        user=user,
        instance=instance,
        csrf=csrf_token(),
        error=error,
    )


@app.get("/")
def index():
    return render()


@app.post("/login")
def login():
    try:
        require_csrf()
        check_login_rate_limit()
        token = request.form.get("token", "").strip()
        user = verify_ctfd_token(token)
        session["user"] = user
        session["token_digest"] = digest_token(token)
        csrf_token()
        return redirect(url_for("index"))
    except RateLimitError as exc:
        session.pop("user", None)
        session.pop("token_digest", None)
        return render(str(exc)), 429
    except Exception as exc:
        session.pop("user", None)
        session.pop("token_digest", None)
        return render(str(exc)), 400


@app.post("/logout")
def logout():
    try:
        require_csrf()
    except ValueError:
        pass
    session.clear()
    return redirect(url_for("index"))


@app.post("/instance/start")
def start():
    user = current_user()
    if not user:
        return redirect(url_for("index"))
    try:
        require_csrf()
        check_instance_rate_limit(user)
        create_instance(user, session.get("token_digest", ""))
        return redirect(url_for("index"))
    except RateLimitError as exc:
        return render(str(exc)), 429
    except Exception as exc:
        return render(str(exc)), 500


@app.post("/instance/renew")
def renew():
    user = current_user()
    if not user:
        return redirect(url_for("index"))
    try:
        require_csrf()
        check_instance_rate_limit(user)
        if get_active_instance(user["id"]) is None:
            create_instance(user, session.get("token_digest", ""))
        else:
            renew_instance(user["id"])
        return redirect(url_for("index"))
    except RateLimitError as exc:
        return render(str(exc)), 429
    except Exception as exc:
        return render(str(exc)), 500


@app.post("/instance/stop")
def stop():
    user = current_user()
    if not user:
        return redirect(url_for("index"))
    try:
        require_csrf()
        check_instance_rate_limit(user)
        stop_instance(user["id"])
        return redirect(url_for("index"))
    except RateLimitError as exc:
        return render(str(exc)), 429
    except Exception as exc:
        return render(str(exc)), 500


@app.get("/healthz")
def healthz():
    try:
        docker_client.ping()
    except DockerException as exc:
        return f"docker unavailable: {exc.__class__.__name__}\n", 503
    return "ok\n"


with db():
    pass

threading.Thread(target=cleanup_loop, daemon=True).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=35000)
