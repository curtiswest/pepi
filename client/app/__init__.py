from flask import Flask

app = Flask(__name__)
app.secret_key = 'not-very-secret-keys'

from . import views


