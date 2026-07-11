from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)

# Este app é um esqueleto inicial para o motoboy. A integração com o banco de dados
# e com as rotas reais deverá ser feita com tabelas de entregadores e rotas no DB.

@app.route('/')
def index():
    if 'entregador_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entregador = request.form['username']
        senha = request.form['password']
        if entregador == 'motoboy' and senha == '1234':
            session['entregador_id'] = 1
            session['entregador_nome'] = entregador
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
    rotas = [
        {'rota_id': 1, 'descricao': 'Entrega 1 - Rua das Flores', 'status': 'Aguardando'},
        {'rota_id': 2, 'descricao': 'Entrega 2 - Av. Principal', 'status': 'Em trânsito'},
    ]
    return render_template('delivery_dashboard.html', rotas=rotas)

@app.route('/rota/<int:rota_id>')
def rota_detalhes(rota_id):
    if 'entregador_id' not in session:
        return redirect(url_for('login'))
    rota = {'rota_id': rota_id, 'descricao': f'Rota {rota_id} para entrega', 'status': 'Aguardando'}
    return render_template('delivery_route.html', rota=rota)

if __name__ == '__main__':
    app.run(debug=True)
