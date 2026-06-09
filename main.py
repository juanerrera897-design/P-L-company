from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

app = Flask(__name__)
app.secret_key = 'P&L-secret-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(300), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    pl_id = db.Column(db.String(100), nullable=False, unique=True)
    points = db.Column(db.Integer, nullable=False, default=0)

challenges = [
    {'id': 1, 'title': 'Recicla 5 botellas', 'description': 'Recoge y recicla cinco botellas de plástico o vidrio.', 'difficulty': 'Fácil', 'points': 50},
    {'id': 2, 'title': 'Limpia una zona', 'description': 'Recoge basura en un parque, playa o calle cercana.', 'difficulty': 'Media', 'points': 120},
    {'id': 3, 'title': 'Planta un árbol', 'description': 'Planta una planta o árbol y cuida su crecimiento.', 'difficulty': 'Media', 'points': 140},
    {'id': 4, 'title': 'Reduce el agua', 'description': 'Usa menos agua durante un día y comparte tus resultados.', 'difficulty': 'Difícil', 'points': 200},
    {'id': 5, 'title': 'Inicia un hábito', 'description': 'Empieza a llevar una bolsa reutilizable o un termo contigo.', 'difficulty': 'Fácil', 'points': 70},
]

products = [
    {'id': 1, 'name': 'Pegatinas ecológicas', 'description': 'Un set de pegatinas con mensajes verdes y diseños cool.', 'price': 150},
    {'id': 2, 'name': 'Lápiz sostenible', 'description': 'Lápiz ecológico hecho con madera reciclada.', 'price': 220},
    {'id': 3, 'name': 'Bolsa reusable', 'description': 'Bolsa de tela resistente para compras y salidas.', 'price': 500},
    {'id': 4, 'name': 'Kit plantación', 'description': 'Kit para plantar un árbol o cuidar un huerto urbano.', 'price': 1200},
    {'id': 5, 'name': 'Mini viaje eco', 'description': 'Experiencia de día para limpiar un entorno natural.', 'price': 2800},
    {'id': 6, 'name': 'Viaje sostenible', 'description': 'Fin de semana eco con talleres y actividades verdes.', 'price': 5200},
]










def current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

@app.route('/')
def index():
    user = current_user()
    return render_template('index.html', user=user)

@app.route('/registro', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        pl_id = request.form['pl_id']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            error = 'El correo ya está en uso.'
        elif User.query.filter_by(pl_id=pl_id).first():
            error = 'Ese P&L ID ya está registrado.'
        else:
            new_user = User(name=name, email=email, pl_id=pl_id, password=password, points=0)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return redirect('/retos')

    return render_template('registro.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect('/retos')
        error = 'Correo o contraseña incorrectos.'
    return render_template('log_in.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/aprende')
def aprende():
    user = current_user()
    return render_template('aprende.html', user=user)

@app.route('/retos', methods=['GET', 'POST'])
def retos():
    user = current_user()
    if not user:
        return redirect('/login')
    msg = None
    if request.method == 'POST':
        challenge_id = int(request.form['challenge_id'])
        challenge = next((c for c in challenges if c['id'] == challenge_id), None)
        if challenge:
            user.points += challenge['points']
            db.session.commit()
            msg = f"¡Reto completado! Ganaste {challenge['points']} puntos."
    return render_template('retos.html', user=user, challenges=challenges, msg=msg)

@app.route('/tienda', methods=['GET', 'POST'])
def tienda():
    user = current_user()
    if not user:
        return redirect('/login')
    msg = None
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            if user.points >= product['price']:
                user.points -= product['price']
                db.session.commit()
                msg = f"Has canjeado {product['name']} por {product['price']} puntos."
            else:
                msg = 'No tienes puntos suficientes para ese premio.'
    return render_template('tienda.html', user=user, products=products, msg=msg)

if __name__ == '__main__':
    app.run(debug=True)



