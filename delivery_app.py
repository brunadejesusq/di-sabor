from flask import Flask, render_template, request, redirect, url_for, session, flash
from database_manager import DatabaseManager
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)
db = DatabaseManager()

@app.route('/')
def index():
    if 'entregador_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['username']
        senha = request.form['password']
        entregador = db.driver_login(usuario, senha)
        if entregador:
            session['entregador_id'] = entregador['id_entregador']
            session['entregador_nome'] = entregador['nome']
            return redirect(url_for('dashboard'))
        flash('Usuário ou senha inválidos.', 'danger')
    return render_template('delivery_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'entregador_id' not in session:
        return redirect(url_for('login'))
    rotas = db.get_routes_for_driver(session['entregador_id'])
    return render_template('delivery_dashboard.html', rotas=rotas)

@app.route('/rota/<int:rota_id>')
def rota_detalhes(rota_id):
    if 'entregador_id' not in session:
        return redirect(url_for('login'))
    rota = db.get_route_details(rota_id)
    if not rota or rota.get('id_entregador') != session['entregador_id']:
        return 'Rota não encontrada ou acesso negado', 404
    return render_template('delivery_route.html', rota=rota)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
