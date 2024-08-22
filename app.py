from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy

load_dotenv()  # Charge les variables d'environnement depuis le fichier .env

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return 'Nom d’utilisateur ou mot de passe incorrect'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        result = localiser_numero(phone_number)
        return render_template('result.html', result=result)
    return render_template('index.html')

def localiser_numero(phone_number):
    api_key = os.getenv('API_KEY')  # Remplace 'API_KEY' par la clé API dans le fichier .env
    url = f"http://apilayer.net/api/validate?access_key={api_key}&number={phone_number}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'valid' in data and data['valid']:
            return {
                'number': data['number'],
                'local_format': data.get('local_format', 'Information non disponible'),
                'international_format': data.get('international_format', 'Information non disponible'),
                'country_prefix': data.get('country_prefix', 'Information non disponible'),
                'country_code': data.get('country_code', 'Information non disponible'),
                'country_name': data.get('country_name', 'Information non disponible'),
                'location': data.get('location', 'Information non disponible'),
                'carrier': data.get('carrier', 'Information non disponible'),
                'line_type': data.get('line_type', 'Information non disponible')
            }
        else:
            return {'error': 'Numéro invalide ou erreur dans la réponse'}
    except requests.exceptions.RequestException as e:
        return {'error': f"Erreur lors de la requête : {e}"}

if __name__ == '__main__':
    app.run(debug=True)
