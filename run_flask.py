from src.backend.DomainController import DomainController
from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta
from flask_classful import FlaskView, route

def main():
    app = Flask(__name__)
    dc = DomainController(app=app)
    DomainController.register(app, route_base="/")
    dc.run_flask()
    return app

if __name__ == "__main__":
    main()