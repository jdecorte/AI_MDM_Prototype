from src.backend.DomainController import DomainController
from flask import Flask



def main():
    app = Flask(__name__)
    dc = DomainController(app=app)
    DomainController.register(app, route_base="/")
    # dc.run_flask()
    return app

app = main()

if __name__ == "__main__":
    main()
