from flask import Flask, render_template, request, redirect, url_for, session, flash
from enum import Enum
from database_manager_mysql import DatabaseManager
import os

class StatusPedido(Enum):
    PENDENTE = 'Pendente'
    EM_PREPARACAO = 'Em Preparação'
    EM_TRANSITO = 'Em Trânsito'
    ENTREGUE = 'Entregue'
    CANCELADO = 'Cancelado'

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)
db = DatabaseManager()

@app.route('/')
def index():
    if 'user_id' in session and session.get('is_restaurante'):
        return redirect(url_for('painel_restaurante'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['username']
        senha = request.form['password']
        user_data = db.login_user(usuario, senha)
        if user_data and user_data.get('is_restaurante'):
            session['user_id'] = user_data['usuario_id']
            session['is_restaurante'] = True
            session['restaurante_id'] = user_data['restaurante_id']
            session['cliente_id'] = None
            return redirect(url_for('painel_restaurante'))
        flash('Usuário ou senha inválidos para restaurante.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/cadastro_restaurante', methods=['GET', 'POST'])
def cadastro_restaurante():
    if request.method == 'POST':
        usuario = request.form['usuario']
        email = request.form['email']
        senha = request.form['senha']
        nome = request.form['nome']
        telefone = request.form['telefone']
        tipo_culinaria = request.form['tipo_culinaria']
        taxa_entrega = request.form['taxa_entrega']
        tempo_estimado = request.form['tempo_estimado']
        endereco = {
            'rua': request.form['rua'],
            'num': request.form['num'],
            'bairro': request.form['bairro'],
            'cidade': request.form['cidade'],
            'estado': request.form['estado'],
            'cep': request.form['cep'],
        }
        novo_restaurante_data = db.create_restaurant(usuario, email, senha, nome, telefone, tipo_culinaria, endereco, taxa_entrega, tempo_estimado)
        if novo_restaurante_data:
            session['user_id'] = novo_restaurante_data['usuario_id']
            session['is_restaurante'] = True
            session['restaurante_id'] = novo_restaurante_data['restaurante_id']
            session['cliente_id'] = None
            flash('Restaurante cadastrado com sucesso!', 'success')
            return redirect(url_for('restaurante_horarios'))
        flash('Erro ao cadastrar restaurante.', 'danger')
        return redirect(url_for('cadastro_restaurante'))
    return render_template('cadastro_restaurante.html')

@app.route('/painel_restaurante')
def painel_restaurante():
    if 'user_id' not in session or not session.get('is_restaurante'):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('login'))
    id_restaurante = session['restaurante_id']
    pedidos = db.get_orders_for_restaurant(id_restaurante)
    restaurante_info = db.get_restaurant_details(id_restaurante)
    return render_template('painel_restaurante.html', pedidos=pedidos, statuses=StatusPedido, restaurante_info=restaurante_info)

@app.route('/painel_restaurante/cardapio')
def restaurante_cardapio():
    if 'user_id' not in session or not session.get('is_restaurante'):
        return redirect(url_for('login'))
    id_restaurante = session['restaurante_id']
    menu = db.get_full_restaurant_menu_for_admin(id_restaurante)
    return render_template('restaurante_cardapio.html', menu=menu)

@app.route('/painel_restaurante/categoria/adicionar', methods=['POST'])
def adicionar_categoria():
    if 'user_id' not in session or not session.get('is_restaurante'):
        return redirect(url_for('login'))
    nome_categoria = request.form.get('nome_categoria')
    if nome_categoria:
        db.add_dish_category(session['restaurante_id'], nome_categoria)
        flash(f"Categoria '{nome_categoria}' adicionada com sucesso!", 'success')
    else:
        flash('O nome da categoria não pode ser vazio.', 'danger')
    return redirect(url_for('restaurante_cardapio'))

@app.route('/painel_restaurante/prato/adicionar', methods=['GET', 'POST'])
def adicionar_prato():
    if 'user_id' not in session or not session.get('is_restaurante'):
        return redirect(url_for('login'))
    id_restaurante = session['restaurante_id']
    if request.method == 'POST':
        categoria_id = request.form.get('categoria_id')
        nome_prato = request.form.get('nome_prato')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        db.add_dish(categoria_id, nome_prato, descricao, preco)
        flash('Prato adicionado com sucesso!', 'success')
        return redirect(url_for('restaurante_cardapio'))
    categorias = db.get_restaurant_categories(id_restaurante)
    return render_template('restaurante_form_prato.html', categorias=categorias)

@app.route('/painel_restaurante/prato/editar/<int:prato_id>', methods=['GET', 'POST'])
def editar_prato(prato_id):
    if 'user_id' not in session or not session.get('is_restaurante'):
        return redirect(url_for('login'))
    id_restaurante = session['restaurante_id']
    if request.method == 'POST':
        nome = request.form.get('nome_prato')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        categoria_id = request.form.get('categoria_id')
        status = bool(int(request.form.get('status_disp')))
        db.edit_dish(prato_id, nome, descricao, preco, categoria_id)
        db.update_dish_availability(prato_id, status)
        flash('Prato atualizado com sucesso!', 'success')
        return redirect(url_for('restaurante_cardapio'))
    prato = db.get_dish_details(prato_id)
    if not prato:
        return 'Prato não encontrado', 404
    categorias = db.get_restaurant_categories(id_restaurante)
    return render_template('restaurante_form_prato.html', prato=prato, categorias=categorias)

@app.route('/painel_restaurante/endereco', methods=['GET', 'POST'])
def restaurante_endereco():
    if 'user_id' not in session or not session.get('is_restaurante'):
        return redirect(url_for('login'))
    id_restaurante = session['restaurante_id']
    restaurante = db.get_restaurant_details(id_restaurante)
    if request.method == 'POST':
        db.update_restaurant_details(id_restaurante, request.form['nome'], request.form['telefone'], request.form['tipo_culinaria'], request.form['taxa_entrega'], request.form['tempo_estimado'])
        endereco = {
            'rua': request.form['rua'],
            'num': request.form['num'],
            'bairro': request.form['bairro'],
            'cidade': request.form['cidade'],
            'estado': request.form['estado'],
            'cep': request.form['cep'],
        }
        db.update_restaurant_address(restaurante['id_end_rest'], endereco)
        flash('Dados atualizados com sucesso!', 'success')
        return redirect(url_for('painel_restaurante'))
    return render_template('restaurante_endereco.html', restaurante=restaurante)

@app.route('/painel_restaurante/horarios', methods=['GET', 'POST'])
def restaurante_horarios():
    if 'user_id' not in session or not session.get('is_restaurante'):
        return redirect(url_for('login'))
    id_restaurante = session['restaurante_id']
    if request.method == 'POST':
        horarios = {}
        dias_semana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
        erro_validacao = False
        for dia in dias_semana:
            if f'ativo_{dia}' in request.form:
                abertura = request.form.get(f'abertura_{dia}')
                fechamento = request.form.get(f'fechamento_{dia}')
                if not abertura or not fechamento:
                    flash(f'Para o dia "{dia}", é necessário preencher os horários.', 'danger')
                    erro_validacao = True
                horarios[dia] = {'abertura': abertura, 'fechamento': fechamento}
            else:
                horarios[dia] = {'abertura': None, 'fechamento': None}
        if erro_validacao:
            return redirect(url_for('restaurante_horarios'))
        if db.update_schedule(id_restaurante, horarios):
            flash('Horários atualizados com sucesso!', 'success')
        else:
            flash('Erro ao atualizar os horários.', 'danger')
        return redirect(url_for('restaurante_horarios'))
    horarios_atuais_lista = db.get_restaurant_schedule(id_restaurante)
    horarios_atuais = {h['dia_semana']: h for h in horarios_atuais_lista}
    dias_semana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
    return render_template('restaurante_horarios.html', horarios=horarios_atuais, dias_semana=dias_semana)

@app.route('/pedido/atualizar_status/<int:pedido_id>', methods=['POST'])
def atualizar_status_pedido(pedido_id):
    if 'user_id' not in session or not session.get('is_restaurante'):
        return redirect(url_for('login'))
    novo_status = request.form.get('status')
    if novo_status:
        db.update_order_status(pedido_id, novo_status)
        flash(f'Status do pedido #{pedido_id} atualizado para "{novo_status}"!', 'success')
    return redirect(url_for('painel_restaurante'))

@app.route('/painel_restaurante/avaliacoes')
def restaurante_avaliacoes():
    if 'user_id' not in session or not session.get('is_restaurante'):
        return redirect(url_for('login'))
    avaliacoes = db.get_reviews_for_restaurant(session['restaurante_id'])
    restaurante_info = db.get_restaurant_details(session['restaurante_id'])
    media = restaurante_info['media_avaliacoes'] if restaurante_info else 0
    return render_template('restaurante_avaliacoes.html', avaliacoes=avaliacoes, media_avaliacoes=media)

@app.route('/painel_restaurante/estoque')
def restaurante_estoque():
    if 'user_id' not in session or not session.get('is_restaurante'):
        return redirect(url_for('login'))
    # A gestão de estoque precisa ser adicionada ao banco de dados.
    return render_template('restaurante_estoque.html', produtos=[])

@app.route('/painel_restaurante/rotas')
def restaurante_rotas():
    if 'user_id' not in session or not session.get('is_restaurante'):
        return redirect(url_for('login'))
    # Rotas e entregadores serão adicionados como próxima camada de evolução.
    return render_template('restaurante_rotas.html', rotas=[])

if __name__ == '__main__':
    app.run(debug=True)
