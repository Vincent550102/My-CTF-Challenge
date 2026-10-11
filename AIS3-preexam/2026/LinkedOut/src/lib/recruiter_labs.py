from types import SimpleNamespace

from flask import Blueprint, abort, render_template, request

from . import admin_models


FORMULA_ALPHABET = "abcdefghijklmnopqrstuvwxyz_.[]"


def candidate_workbook():
    return {
        "candidate": {
            "name": "Jordan Lee",
            "headline": "Product security engineer",
            "location": "Local office",
        },
        "signals": [
            {"name": "score", "label": "Fit score", "value": 42},
            {"name": "connections", "label": "Shared connections", "value": 313},
        ],
        "profile_fields": [
            {"field": "headline", "value": "Product security engineer"},
            {"field": "location", "value": "Local office"},
            {"field": "availability", "value": "Interviewing"},
        ],
        "workflow": [
            {"label": "fit signal", "value": "score"},
            {"label": "network signal", "value": "connections"},
        ],
        "formula_reference": [
            {"label": "formula alphabet", "value": FORMULA_ALPHABET},
            {"label": "score signal", "value": "score"},
            {"label": "connection signal", "value": "connections"},
            {"label": "profile signal", "value": "profile.location"},
        ],
        "examples": [
            "score",
            "connections",
            "profile.location",
        ],
    }


def candidate_profile():
    return SimpleNamespace(
        headline="Product security engineer",
        location="Local office",
        availability="Interviewing",
    )


def formula_vocabulary(workbook):
    return set(FORMULA_ALPHABET)


def normalize_formula(expr, workbook):
    vocabulary = formula_vocabulary(workbook)
    return "".join(ch for ch in expr if ch in vocabulary)


def run_candidate_formula(expr, context, workbook):
    filtered = normalize_formula(expr, workbook)
    sandbox_globals = {"__builtins__": {}}
    sandbox_globals.update(context)
    return eval(filtered, sandbox_globals, {})


def create_blueprint(require_login):
    bp = Blueprint("recruiter_labs", __name__, template_folder="templates")

    @bp.route(admin_models.LABS_ROUTE, methods=["GET", "POST"])
    def recruiter_labs():
        user, response = require_login()
        if response is not None:
            return response
        if not admin_models.has_recruiter_labs_access(user):
            abort(403)

        workbook = candidate_workbook()
        formula_result = None
        formula_error = None
        normalized_formula = None
        if request.method == "POST":
            expr = request.form.get("formula", "")
            normalized_formula = normalize_formula(expr, workbook)
            context = {
                "score": 42,
                "connections": 313,
                "profile": candidate_profile(),
            }
            try:
                formula_result = repr(run_candidate_formula(expr, context, workbook))
            except Exception as exc:
                formula_error = exc.__class__.__name__

        return render_template(
            "recruiter_labs/labs.html",
            title="Recruiter Labs",
            user=user,
            trusted_domain=admin_models.TRUSTED_DOMAIN,
            workbook=workbook,
            formula_help=(
                "The legacy preview keeps only the characters listed in the formula alphabet."
            ),
            normalized_formula=normalized_formula,
            formula_result=formula_result,
            formula_error=formula_error,
        )

    return bp
