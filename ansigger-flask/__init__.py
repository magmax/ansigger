#!/usr/bin/env python
import os

from flask import Flask, Response, render_template, abort

from ansigger.utils import run_ansible


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev")

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    @app.route("/")
    def index():
        pb = [
            os.path.splitext(x)[0]
            for x in os.listdir("playbooks/")
            if x.endswith(".yaml")
        ]
        return render_template("index.html", playbooks=pb)

    @app.route("/test")
    def test():
        return "OK"

    @app.route("/ansible/<playbook>")
    def ansible(playbook):
        def generator():
            for line in run_ansible(playbook):
                yield f"[{line['timestamp']}] {line['kind']}: {line['line']}<br>"

        if any(x in playbook for x in "/."):
            app.logger.error(f"Invalid playbook {playbook}")
            abort(404)
        if f"{playbook}.yaml" not in os.listdir("playbooks/"):
            app.logger.error(f"Playbook {playbook} not found")
            abort(404)
        return Response(generator())

    @app.route("/html")
    def html():
        def generator():
            yield "<ul>"
            for line in run_ansible("foo"):
                color = "#000" if line["kind"] == "O" else "#f00"
                yield f'<li><b>{line["timestamp"]}</b> <span style="color:{color}">{line["line"]}</span>'
            yield "</ul>"

        return Response(generator())

    return app
