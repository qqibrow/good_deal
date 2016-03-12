from app import app
@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/hello')
def hello():
    return 'maybe not hello'