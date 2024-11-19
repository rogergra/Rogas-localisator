from app import app, db, User

def create_user(username, password):
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

# Créer la base de données et les tables
with app.app_context():
    db.create_all()
    # Ajouter un utilisateur par défaut
    create_user('testuser', 'password123')
