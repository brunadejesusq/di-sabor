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
    if 'user_id' in session:
        if session.get('is_restaurante'):
            flash('Use o aplicativo de restaurante para entrar como restaurante.', 'danger')
            return redirect(url_for('logout'))
        return redirect(url_for('painel_cliente'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['username']
        senha = request.form['password']
        user_data = db.login_user(usuario, senha)
        if user_data and not user_data.get('is_restaurante'):
            session['user_id'] = user_data['usuario_id']
            session['is_restaurante'] = False
            session['cliente_id'] = user_data['cliente_id']
            session['restaurante_id'] = None
            return redirect(url_for('painel_cliente'))
        flash('Usuário ou senha inválidos para cliente.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/pre_cadastro')
def pre_cadastro():
    return render_template('pre_cadastro.html')

@app.route('/cadastro_cliente', methods=['GET', 'POST'])
def cadastro_cliente():
    if request.method == 'POST':
        usuario = request.form['usuario']
        nome_completo = request.form['nome_completo']
        email = request.form['email']
        telefone = request.form['telefone']
        cpf = request.form['cpf']
        senha = request.form['senha']
        cliente_id = db.create_client(usuario, email, senha, nome_completo, telefone, cpf)
        if cliente_id:
            flash('Cadastro realizado com sucesso! Faça seu login.', 'success')
            return redirect(url_for('login'))
        flash('Usuário ou email já existem. Tente novamente.', 'danger')
        return redirect(url_for('cadastro_cliente'))
    return render_template('cadastro_cliente.html')

@app.route('/painel_cliente')
def painel_cliente():
    if 'user_id' not in session or session.get('is_restaurante'):
        flash('Faça login para continuar.', 'danger')
        return redirect(url_for('login'))
    restaurante = db.get_restaurant_by_name('Di Sabor Caseiro')
    if not restaurante:
        return 'Restaurante Di Sabor Caseiro não encontrado', 404
    restaurante['aberto'] = db.is_restaurant_open(restaurante['id_restaurante'])
    restaurantes = [restaurante]
    return render_template('painel_cliente.html', restaurantes=restaurantes)

@app.route('/restaurante/<int:restaurante_id>')
def menu_restaurante(restaurante_id):
    if 'user_id' not in session or session.get('is_restaurante'):
        flash('Faça login para continuar.', 'danger')
        return redirect(url_for('login'))
    restaurante_info = db.get_restaurant_details(restaurante_id)
    if not restaurante_info:
        return 'Restaurante não encontrado', 404
    restaurante_esta_aberto = db.is_restaurant_open(restaurante_id)
    menu = db.get_restaurant_menu(restaurante_id)
    return render_template('menu_restaurante.html', menu=menu, restaurante=restaurante_info, aberto=restaurante_esta_aberto)

@app.route('/carrinho/adicionar', methods=['POST'])
def adicionar_ao_carrinho():
    if 'user_id' not in session or session.get('is_restaurante'):
        return redirect(url_for('login'))
    prato_id = request.form.get('prato_id')
    restaurante_id = int(request.form.get('restaurante_id'))
    if not db.is_restaurant_open(restaurante_id):
        flash('Desculpe, este restaurante está fechado.', 'danger')
        return redirect(url_for('menu_restaurante', restaurante_id=restaurante_id))
    if 'cart' not in session:
        session['cart'] = {'items': {}, 'restaurante_id': None, 'taxa_entrega': 0.0}
    if session['cart']['restaurante_id'] and session['cart']['restaurante_id'] != restaurante_id:
        flash('Você só pode adicionar itens de um restaurante por vez.', 'danger')
        return redirect(url_for('menu_restaurante', restaurante_id=restaurante_id))
    prato_details = db.get_dish_details(prato_id)
    if not prato_details:
        return 'Prato não encontrado', 404
    cart_items = session['cart']['items']
    if prato_id in cart_items:
        cart_items[prato_id]['quantidade'] += 1
    else:
        cart_items[prato_id] = {
            'nome': prato_details['nome_prato'],
            'preco': float(prato_details['preco']),
            'quantidade': 1
        }
    if not session['cart']['restaurante_id']:
        restaurante_info = db.get_restaurant_details(restaurante_id)
        if restaurante_info:
            session['cart']['restaurante_id'] = restaurante_id
            session['cart']['taxa_entrega'] = float(restaurante_info['taxa_entrega'])
    session.modified = True
    flash(f"'{prato_details['nome_prato']}' foi adicionado ao seu carrinho!", 'success')
    return redirect(request.referrer or url_for('painel_cliente'))

@app.route('/carrinho')
def ver_carrinho():
    if 'user_id' not in session or session.get('is_restaurante'):
        return redirect(url_for('login'))
    cart = session.get('cart', {'items': {}})
    subtotal = sum(item['preco'] * item['quantidade'] for item in cart.get('items', {}).values())
    taxa_entrega = cart.get('taxa_entrega', 0.0)
    total = subtotal + taxa_entrega
    return render_template('carrinho.html', cart=cart, subtotal=subtotal, total=total, taxa_entrega=taxa_entrega)

@app.route('/carrinho/remover/<prato_id>')
def remover_item_carrinho(prato_id):
    if 'cart' in session and prato_id in session['cart']['items']:
        session['cart']['items'].pop(prato_id)
        if not session['cart']['items']:
            session.pop('cart')
        session.modified = True
        flash('Item removido do carrinho.', 'info')
    return redirect(url_for('ver_carrinho'))

@app.route('/carrinho/atualizar', methods=['POST'])
def atualizar_carrinho():
    prato_id = request.form.get('prato_id')
    quantidade = int(request.form.get('quantidade', 1))
    if 'cart' in session and prato_id in session['cart']['items']:
        if quantidade > 0:
            session['cart']['items'][prato_id]['quantidade'] = quantidade
        else:
            session['cart']['items'].pop(prato_id)
        if not session['cart']['items']:
            session.pop('cart')
        session.modified = True
    return redirect(url_for('ver_carrinho'))

@app.route('/checkout')
def checkout():
    if 'user_id' not in session or not session.get('cart'):
        return redirect(url_for('painel_cliente'))
    cliente_id = session['cliente_id']
    enderecos = db.get_client_addresses(cliente_id)
    formas_pagamento = db.get_payment_methods()
    cart = session.get('cart', {'items': {}})
    subtotal = sum(item['preco'] * item['quantidade'] for item in cart.get('items', {}).values())
    taxa_entrega = cart.get('taxa_entrega', 0.0)
    total = subtotal + taxa_entrega
    return render_template('checkout.html', cart=cart, subtotal=subtotal, total=total, taxa_entrega=taxa_entrega, enderecos=enderecos, formas_pagamento=formas_pagamento)

@app.route('/adicionar_endereco', methods=['GET', 'POST'])
def adicionar_endereco():
    if 'user_id' not in session or session.get('is_restaurante'):
        flash('Faça login como cliente para continuar.', 'danger')
        return redirect(url_for('login'))
    cliente_id = session['cliente_id']
    origem = request.args.get('origem', 'painel_cliente')
    if request.method == 'POST':
        rua = request.form['rua']
        num = request.form['num']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        estado = request.form['estado']
        cep = request.form['cep']
        endereco_id = db.add_client_address(cliente_id, rua, num, bairro, cidade, estado, cep)
        if endereco_id:
            flash('Endereço cadastrado com sucesso!', 'success')
            return redirect(url_for(origem))
        flash('Erro ao cadastrar endereço. Tente novamente.', 'danger')
    return render_template('adicionar_endereco.html', origem=origem)

@app.route('/editar_endereco/<int:endereco_id>', methods=['GET', 'POST'])
def editar_endereco(endereco_id):
    if 'user_id' not in session or session.get('is_restaurante'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        endereco = {
            'rua': request.form['rua'],
            'num': request.form['num'],
            'bairro': request.form['bairro'],
            'cidade': request.form['cidade'],
            'estado': request.form['estado'],
            'cep': request.form['cep'],
        }
        if db.update_client_address(endereco_id, endereco):
            flash('Endereço atualizado com sucesso!', 'success')
        else:
            flash('Erro ao atualizar o endereço.', 'danger')
        return redirect(url_for('meus_enderecos'))
    endereco = db.get_address_details(endereco_id)
    if not endereco:
        return 'Endereço não encontrado', 404
    return render_template('editar_endereco.html', endereco=endereco)

@app.route('/excluir_endereco/<int:endereco_id>')
def excluir_endereco(endereco_id):
    if 'user_id' not in session or session.get('is_restaurante'):
        return redirect(url_for('login'))
    if db.delete_client_address(endereco_id):
        flash('Endereço excluído com sucesso!', 'success')
    else:
        flash('Erro ao excluir o endereço.', 'danger')
    return redirect(url_for('meus_enderecos'))

@app.route('/finalizar_pedido', methods=['POST'])
def finalizar_pedido():
    if 'user_id' not in session or not session.get('cart'):
        return redirect(url_for('login'))
    endereco_id = request.form.get('endereco_id')
    pagamento_id = request.form.get('pagamento_id')
    if not endereco_id or not pagamento_id:
        flash('Por favor, selecione um endereço e uma forma de pagamento.', 'danger')
        return redirect(url_for('checkout'))
    cart = session.get('cart')
    cliente_id = session['cliente_id']
    restaurante_id = cart['restaurante_id']
    taxa_entrega = cart['taxa_entrega']
    pedido_id = db.create_order(cliente_id, restaurante_id, pagamento_id, endereco_id, taxa_entrega)
    if pedido_id:
        for prato_id, item_details in cart['items'].items():
            db.add_order_item(pedido_id, prato_id, item_details['quantidade'], item_details['preco'], '')
        db.update_order_status(pedido_id, StatusPedido.PENDENTE.value)
        session.pop('cart', None)
        return redirect(url_for('pedido_confirmado', pedido_id=pedido_id))
    flash('Ocorreu um erro ao processar seu pedido. Tente novamente.', 'danger')
    return redirect(url_for('checkout'))

@app.route('/pedido_confirmado/<int:pedido_id>')
def pedido_confirmado(pedido_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('pedido_confirmado.html', pedido_id=pedido_id)

@app.route('/meus_pedidos')
def meus_pedidos():
    if 'user_id' not in session or session.get('is_restaurante'):
        flash('Faça login como cliente para ver seus pedidos.', 'danger')
        return redirect(url_for('login'))
    pedidos = db.get_orders_for_client(session['cliente_id'])
    return render_template('meus_pedidos.html', pedidos=pedidos)

@app.route('/avaliar_pedido/<int:pedido_id>', methods=['GET', 'POST'])
def avaliar_pedido(pedido_id):
    if 'user_id' not in session or session.get('is_restaurante'):
        return redirect(url_for('login'))
    cliente_id = session['cliente_id']
    pedidos_cliente = db.get_orders_for_client(cliente_id)
    pedido_info = next((p for p in pedidos_cliente if p['id_pedido'] == pedido_id), None)
    if not pedido_info or pedido_info['status_pedido'] != StatusPedido.ENTREGUE.value or pedido_info.get('foi_avaliado'):
        flash('Este pedido não pode ser avaliado.', 'danger')
        return redirect(url_for('meus_pedidos'))
    if request.method == 'POST':
        nota = request.form.get('nota')
        feedback = request.form.get('feedback')
        if 'id_restaurante' not in pedido_info:
            flash('Erro: Não foi possível identificar o restaurante.', 'danger')
            return redirect(url_for('meus_pedidos'))
        db.add_review(pedido_id, pedido_info['id_restaurante'], cliente_id, nota, feedback)
        db.mark_order_as_reviewed(pedido_id)
        flash('Obrigado pela sua avaliação!', 'success')
        return redirect(url_for('meus_pedidos'))
    return render_template('avaliar_pedido.html', pedido=pedido_info)

@app.route('/meus_enderecos')
def meus_enderecos():
    if 'user_id' not in session or session.get('is_restaurante'):
        flash('Faça login como cliente para continuar.', 'danger')
        return redirect(url_for('login'))
    enderecos = db.get_client_addresses(session['cliente_id'])
    return render_template('meus_enderecos.html', enderecos=enderecos)

if __name__ == '__main__':
    app.run(debug=True)
