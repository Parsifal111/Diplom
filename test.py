from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

@app.route('/ovoshi')
def ovoshi():
    return render_template('ovoshi.html')

@app.route('/myaso')
def myaso():
    return render_template('myaso.html')

@app.route('/frukti')
def frukti():
    return render_template('frukti.html')

@app.route('/milk_prod')
def milk_prod():
    return render_template('milk_prod.html')

if __name__ == '__main__':
    app.run(debug=True)
