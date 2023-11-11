from bottle import run, Bottle
from app_login import login_app
from app_esb_bus import esb_bus_app


mainApp = Bottle()

if __name__ == '__main__':
    mainApp.mount('/login', login_app)
    mainApp.mount('/esb', esb_bus_app)

    mainApp.run(host='localhost', port=8080, debug=True)
