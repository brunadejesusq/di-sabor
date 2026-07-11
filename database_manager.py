import os
import sys
from datetime import datetime, time
from typing import Any, Dict, List, Optional

import firebase_admin
from firebase_admin import credentials, firestore


class DatabaseManager:
    def __init__(self):
        self.db = self._init_firestore()

    def _init_firestore(self):
        cred_path = os.getenv(
            "FIREBASE_CREDENTIALS",
            os.path.join(os.path.dirname(__file__), "firebase_credentials.json"),
        )

        if not os.path.exists(cred_path):
            raise FileNotFoundError(
                f"Arquivo de credenciais Firebase não encontrado: {cred_path}. "
                "Defina FIREBASE_CREDENTIALS ou coloque firebase_credentials.json no diretório do projeto."
            )

        try:
            cred = credentials.Certificate(cred_path)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            return firestore.client()
        except Exception as e:
            print(f"Erro ao inicializar o Firebase: {e}")
            sys.exit(1)

    def _next_id(self, name: str) -> int:
        counter_ref = self.db.collection("counters").document(name)

        @firestore.transactional
        def increment(transaction, doc_ref):
            snapshot = doc_ref.get(transaction=transaction)
            if snapshot.exists and snapshot.get("value") is not None:
                next_id = snapshot.get("value") + 1
                transaction.update(doc_ref, {"value": next_id})
            else:
                next_id = 1
                transaction.set(doc_ref, {"value": next_id})
            return next_id

        transaction = self.db.transaction()
        return increment(transaction, counter_ref)

    def _format_time(self, value: Any) -> Optional[time]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.time()
        if isinstance(value, time):
            return value
        if isinstance(value, str):
            return datetime.strptime(value, "%H:%M:%S").time()
        return None

    # -------------------- CLIENTE --------------------
    def create_client(self, usuario, email, senha, nome_completo, telefone, cpf):
        usuario_exists = self.db.collection("users")
        usuario_query = usuario_exists.where("usuario", "==", usuario).limit(1).get()
        email_query = usuario_exists.where("email", "==", email).limit(1).get()
        if usuario_query or email_query:
            return None

        usuario_id = self._next_id("usuario")
        cliente_id = self._next_id("cliente")

        self.db.collection("users").document(str(usuario_id)).set(
            {
                "usuario_id": usuario_id,
                "usuario": usuario,
                "email": email,
                "senha": senha,
                "is_restaurante": False,
            }
        )
        self.db.collection("clients").document(str(cliente_id)).set(
            {
                "cliente_id": cliente_id,
                "usuario_id": usuario_id,
                "nome_completo": nome_completo,
                "email": email,
                "telefone": telefone,
                "cpf": cpf,
            }
        )
        return cliente_id

    # -------------------- RESTAURANTE --------------------
    def create_restaurant(self, usuario, email, senha, nome, telefone, tipo_culinaria, endereco, taxa_entrega, tempo_estimado):
        usuario_exists = self.db.collection("users")
        usuario_query = usuario_exists.where("usuario", "==", usuario).limit(1).get()
        email_query = usuario_exists.where("email", "==", email).limit(1).get()
        if usuario_query or email_query:
            return None

        usuario_id = self._next_id("usuario")
        restaurante_id = self._next_id("restaurante")
        id_end_rest = self._next_id("enderecos_restaurante")

        self.db.collection("users").document(str(usuario_id)).set(
            {
                "usuario_id": usuario_id,
                "usuario": usuario,
                "email": email,
                "senha": senha,
                "is_restaurante": True,
            }
        )

        self.db.collection("restaurant_addresses").document(str(id_end_rest)).set(
            {
                "id_end_rest": id_end_rest,
                "rua": endereco["rua"],
                "num": endereco["num"],
                "bairro": endereco["bairro"],
                "cidade": endereco["cidade"],
                "estado": endereco["estado"],
                "cep": endereco["cep"],
            }
        )

        self.db.collection("restaurants").document(str(restaurante_id)).set(
            {
                "id_restaurante": restaurante_id,
                "usuario_id": usuario_id,
                "id_end_rest": id_end_rest,
                "nome": nome,
                "telefone": telefone,
                "tipo_culinaria": tipo_culinaria,
                "taxa_entrega": float(taxa_entrega) if taxa_entrega else 0.0,
                "tempo_entrega_estimado": tempo_estimado,
            }
        )

        return {"restaurante_id": restaurante_id, "usuario_id": usuario_id}

    # -------------------- HORÁRIOS --------------------
    def add_schedule(self, id_restaurante, dia_semana, horario_abertura, horario_fechamento):
        doc_ref = self.db.collection("restaurant_schedules").document(str(id_restaurante))
        doc_ref.set(
            {
                dia_semana: {
                    "horario_abertura": horario_abertura,
                    "horario_fechamento": horario_fechamento,
                }
            },
            merge=True,
        )

    def get_restaurant_schedule(self, id_restaurante):
        doc = self.db.collection("restaurant_schedules").document(str(id_restaurante)).get()
        if not doc.exists:
            return []
        data = doc.to_dict()
        schedule = []
        for dia, tempos in data.items():
            schedule.append(
                {
                    "dia_semana": dia,
                    "horario_abertura": self._format_time(tempos.get("horario_abertura")),
                    "horario_fechamento": self._format_time(tempos.get("horario_fechamento")),
                }
            )
        return schedule

    def update_schedule(self, id_restaurante, horarios):
        try:
            doc_ref = self.db.collection("restaurant_schedules").document(str(id_restaurante))
            saved = {}
            for dia, tempos in horarios.items():
                if tempos["abertura"] and tempos["fechamento"]:
                    saved[dia] = {
                        "horario_abertura": tempos["abertura"],
                        "horario_fechamento": tempos["fechamento"],
                    }
            doc_ref.set(saved, merge=True)
            return True
        except Exception as e:
            print(f"Erro ao atualizar horários: {e}")
            return False

    def is_restaurant_open(self, id_restaurante):
        doc = self.db.collection("restaurant_schedules").document(str(id_restaurante)).get()
        if not doc.exists:
            return False

        data = doc.to_dict()
        fuso_horario_brasilia = datetime.now().astimezone().tzinfo
        agora = datetime.now()
        dia_semana_map = {
            0: "Segunda",
            1: "Terça",
            2: "Quarta",
            3: "Quinta",
            4: "Sexta",
            5: "Sábado",
            6: "Domingo",
        }
        dia_atual = dia_semana_map[agora.weekday()]
        horario = data.get(dia_atual)
        if not horario:
            return False

        abertura = self._format_time(horario.get("horario_abertura"))
        fechamento = self._format_time(horario.get("horario_fechamento"))
        if not abertura or not fechamento:
            return False

        hora_atual = agora.time()
        return abertura <= hora_atual < fechamento

    # -------------------- PEDIDOS --------------------
    def create_order(self, id_cliente, id_restaurante, id_forma_pagamento, endereco_id, taxa_entrega):
        pedido_id = self._next_id("pedido")
        self.db.collection("orders").document(str(pedido_id)).set(
            {
                "id_pedido": pedido_id,
                "id_cliente": id_cliente,
                "id_restaurante": id_restaurante,
                "id_forma_pagamento": id_forma_pagamento,
                "endereco_id": endereco_id,
                "dataHora": firestore.SERVER_TIMESTAMP,
                "status_pedido": "Pendente",
                "valor_total": float(taxa_entrega),
                "foi_avaliado": False,
            }
        )
        return pedido_id

    def add_order_item(self, id_pedido, id_prato, qtd, preco_item, observacoes):
        item_id = f"{id_pedido}_{id_prato}"
        self.db.collection("order_items").document(item_id).set(
            {
                "id_pedido": id_pedido,
                "id_prato": id_prato,
                "qtd": qtd,
                "preco_item": float(preco_item),
                "observacoes": observacoes,
            }
        )
        order_ref = self.db.collection("orders").document(str(id_pedido))
        order_snapshot = order_ref.get()
        if order_snapshot.exists:
            current = order_snapshot.to_dict().get("valor_total", 0.0)
            order_ref.update({"valor_total": current + float(qtd) * float(preco_item)})

    def update_order_status(self, id_pedido, status):
        self.db.collection("orders").document(str(id_pedido)).update({"status_pedido": status})

    def get_order_details(self, pedido_id):
        doc = self.db.collection("orders").document(str(pedido_id)).get()
        return doc.to_dict() if doc.exists else None

    # -------------------- AVALIAÇÃO --------------------
    def add_review(self, pedido_id, restaurante_id, cliente_id, nota, feedback):
        review_id = self._next_id("avaliacoes_restaurante")
        client_doc = self.db.collection("clients").document(str(cliente_id)).get()
        cliente_nome = client_doc.to_dict().get("nome_completo") if client_doc.exists else None
        self.db.collection("restaurant_reviews").document(str(review_id)).set(
            {
                "id_avaliacao": review_id,
                "id_restaurante": restaurante_id,
                "id_cliente": cliente_id,
                "nota": int(nota) if nota is not None else None,
                "feedback": feedback,
                "data_hora": firestore.SERVER_TIMESTAMP,
                "id_pedido": pedido_id,
                "nome_cliente": cliente_nome,
            }
        )
        return review_id

    def mark_order_as_reviewed(self, pedido_id):
        self.db.collection("orders").document(str(pedido_id)).update({"foi_avaliado": True})

    def get_reviews_for_restaurant(self, restaurante_id):
        query = self.db.collection("restaurant_reviews").where("id_restaurante", "==", restaurante_id).order_by("data_hora", direction=firestore.Query.DESCENDING)
        return [doc.to_dict() for doc in query.stream()]

    # -------------------- LOGIN --------------------
    def login_user(self, usuario, senha):
        users_ref = self.db.collection("users")
        query = users_ref.where("usuario", "==", usuario).limit(1).get()
        if not query:
            return None

        user_data = query[0].to_dict()
        if user_data.get("senha") != senha:
            return None

        result = {
            "usuario_id": user_data["usuario_id"],
            "is_restaurante": user_data["is_restaurante"],
            "cliente_id": None,
            "restaurante_id": None,
        }

        if user_data.get("is_restaurante"):
            restaurant_query = self.db.collection("restaurants").where("usuario_id", "==", user_data["usuario_id"]).limit(1).get()
            if restaurant_query:
                result["restaurante_id"] = restaurant_query[0].to_dict().get("id_restaurante")
        else:
            client_query = self.db.collection("clients").where("usuario_id", "==", user_data["usuario_id"]).limit(1).get()
            if client_query:
                result["cliente_id"] = client_query[0].to_dict().get("cliente_id")

        return result

    # -------------------- CARDÁPIO E CONSULTAS --------------------
    def add_dish_category(self, id_restaurante, nome_categoria):
        category_query = self.db.collection("restaurant_categories").where("id_restaurante", "==", id_restaurante).where("nome_categoria", "==", nome_categoria).limit(1).get()
        if category_query:
            return None
        categoria_id = self._next_id("categoria_pratos")
        self.db.collection("restaurant_categories").document(str(categoria_id)).set(
            {
                "categoria_id": categoria_id,
                "id_restaurante": id_restaurante,
                "nome_categoria": nome_categoria,
            }
        )
        return categoria_id

    # -------------------- ENTREGADORES E ROTAS --------------------
    def driver_login(self, usuario, senha):
        driver_query = self.db.collection("drivers").where("usuario", "==", usuario).limit(1).get()
        if not driver_query:
            return None
        driver = driver_query[0].to_dict()
        if driver.get("senha") != senha:
            return None
        return driver

    def get_routes_for_driver(self, id_entregador):
        routes = [doc.to_dict() for doc in self.db.collection("delivery_routes").where("id_entregador", "==", id_entregador).stream()]
        return routes

    def get_route_details(self, rota_id):
        doc = self.db.collection("delivery_routes").document(str(rota_id)).get()
        return doc.to_dict() if doc.exists else None

    def add_dish(self, categoria_id, nome_prato, descricao, preco):
        categoria_doc = self.db.collection("restaurant_categories").document(str(categoria_id)).get()
        if not categoria_doc.exists:
            return None
        categoria = categoria_doc.to_dict()
        dish_id = self._next_id("pratos")
        self.db.collection("dishes").document(str(dish_id)).set(
            {
                "id_prato": dish_id,
                "categoria_id": categoria_id,
                "nome_prato": nome_prato,
                "descricao": descricao,
                "preco": float(preco),
                "status_disp": True,
                "id_restaurante": categoria["id_restaurante"],
            }
        )
        return dish_id

    def get_all_restaurants(self):
        restaurants = [doc.to_dict() for doc in self.db.collection("restaurants").stream()]
        for restaurant in restaurants:
            restaurant["media_avaliacoes"] = self._calculate_average_rating(restaurant["id_restaurante"])
        return restaurants

    def _calculate_average_rating(self, restaurante_id):
        reviews = self.db.collection("restaurant_reviews").where("id_restaurante", "==", restaurante_id).stream()
        values = [doc.to_dict().get("nota", 0) for doc in reviews]
        return round(sum(values) / len(values), 2) if values else 0

    def get_restaurant_menu(self, id_restaurante):
        categories = {doc.to_dict()["categoria_id"]: doc.to_dict()["nome_categoria"] for doc in self.db.collection("restaurant_categories").where("id_restaurante", "==", id_restaurante).stream()}
        menu_items = self.db.collection("dishes").where("id_restaurante", "==", id_restaurante).where("status_disp", "==", True).stream()
        menu = {}
        for item in menu_items:
            dish = item.to_dict()
            categoria = categories.get(dish["categoria_id"], "Sem Categoria")
            menu.setdefault(categoria, []).append(dish)
        return menu

    def get_full_restaurant_menu_for_admin(self, id_restaurante):
        categories = {doc.to_dict()["categoria_id"]: doc.to_dict()["nome_categoria"] for doc in self.db.collection("restaurant_categories").where("id_restaurante", "==", id_restaurante).stream()}
        menu_items = self.db.collection("dishes").where("id_restaurante", "==", id_restaurante).stream()
        menu = {}
        for item in menu_items:
            dish = item.to_dict()
            categoria = categories.get(dish["categoria_id"], "Sem Categoria")
            menu.setdefault(categoria, []).append(dish)
        return menu

    def get_orders_for_restaurant(self, id_restaurante):
        orders = self.db.collection("orders").where("id_restaurante", "==", id_restaurante).stream()
        enriched = []
        for doc in orders:
            order = doc.to_dict()
            cliente_doc = self.db.collection("clients").document(str(order.get("id_cliente"))).get()
            order["nome_completo"] = cliente_doc.to_dict().get("nome_completo") if cliente_doc.exists else None
            enriched.append(order)
        return enriched

    def get_orders_for_client(self, id_cliente):
        orders = self.db.collection("orders").where("id_cliente", "==", id_cliente).stream()
        enriched = []
        for doc in orders:
            order = doc.to_dict()
            restaurante_doc = self.db.collection("restaurants").document(str(order.get("id_restaurante"))).get()
            order["nome_restaurante"] = restaurante_doc.to_dict().get("nome") if restaurante_doc.exists else None
            enriched.append(order)
        return enriched

    def get_payment_methods(self):
        methods = [doc.to_dict() for doc in self.db.collection("payment_methods").stream()]
        if not methods:
            return [
                {"id_forma_pagamento": 1, "formaPag": "Dinheiro"},
                {"id_forma_pagamento": 2, "formaPag": "Cartão de Crédito"},
                {"id_forma_pagamento": 3, "formaPag": "PIX"},
            ]
        return methods

    def get_client_addresses(self, cliente_id):
        addresses = self.db.collection("client_addresses").where("cliente_id", "==", cliente_id).stream()
        return [doc.to_dict() for doc in addresses]

    def get_address_details(self, endereco_id):
        doc = self.db.collection("client_addresses").document(str(endereco_id)).get()
        return doc.to_dict() if doc.exists else None

    def update_client_address(self, endereco_id, endereco):
        try:
            self.db.collection("client_addresses").document(str(endereco_id)).update(
                {
                    "rua": endereco["rua"],
                    "num": endereco["num"],
                    "bairro": endereco["bairro"],
                    "cidade": endereco["cidade"],
                    "estado": endereco["estado"],
                    "cep": endereco["cep"],
                }
            )
            return True
        except Exception as e:
            print(f"Erro ao atualizar endereço do cliente: {e}")
            return False

    def delete_client_address(self, endereco_id):
        try:
            self.db.collection("client_addresses").document(str(endereco_id)).delete()
            return True
        except Exception as e:
            print(f"Erro ao excluir endereço: {e}")
            return False

    def add_client_address(self, cliente_id, rua, num, bairro, cidade, estado, cep):
        endereco_id = self._next_id("enderecos_entrega")
        self.db.collection("client_addresses").document(str(endereco_id)).set(
            {
                "endereco_id": endereco_id,
                "cliente_id": cliente_id,
                "rua": rua,
                "num": num,
                "bairro": bairro,
                "cidade": cidade,
                "estado": estado,
                "cep": cep,
            }
        )
        return endereco_id

    def get_restaurant_categories(self, id_restaurante):
        categories = self.db.collection("restaurant_categories").where("id_restaurante", "==", id_restaurante).stream()
        return [doc.to_dict() for doc in categories]

    def get_dish_details(self, id_prato):
        doc = self.db.collection("dishes").document(str(id_prato)).get()
        return doc.to_dict() if doc.exists else None

    def edit_dish(self, id_prato, nome, descricao, preco, categoria_id):
        try:
            self.db.collection("dishes").document(str(id_prato)).update(
                {
                    "nome_prato": nome,
                    "descricao": descricao,
                    "preco": float(preco),
                    "categoria_id": categoria_id,
                }
            )
            return True
        except Exception as e:
            print(f"Erro ao editar o prato: {e}")
            return False

    def update_dish_availability(self, id_prato, is_available):
        try:
            self.db.collection("dishes").document(str(id_prato)).update({"status_disp": is_available})
            return True
        except Exception as e:
            print(f"Erro ao alterar disponibilidade do prato: {e}")
            return False

    def get_restaurant_by_name(self, nome_restaurante):
        query = self.db.collection("restaurants").where("nome", "==", nome_restaurante).limit(1).get()
        if not query:
            return None
        restaurante = query[0].to_dict()
        endereco_doc = self.db.collection("restaurant_addresses").document(str(restaurante["id_end_rest"])) .get()
        if endereco_doc.exists:
            restaurante.update(endereco_doc.to_dict())
        restaurante["media_avaliacoes"] = self._calculate_average_rating(restaurante["id_restaurante"])
        return restaurante

    def get_restaurant_details(self, restaurante_id):
        restaurante_doc = self.db.collection("restaurants").document(str(restaurante_id)).get()
        if not restaurante_doc.exists:
            return None
        restaurante = restaurante_doc.to_dict()
        endereco_doc = self.db.collection("restaurant_addresses").document(str(restaurante["id_end_rest"])) .get()
        if endereco_doc.exists:
            restaurante.update(endereco_doc.to_dict())
        restaurante["media_avaliacoes"] = self._calculate_average_rating(restaurante_id)
        return restaurante

    def update_restaurant_details(self, restaurante_id, nome, telefone, tipo_culinaria, taxa_entrega, tempo_estimado):
        try:
            self.db.collection("restaurants").document(str(restaurante_id)).update(
                {
                    "nome": nome,
                    "telefone": telefone,
                    "tipo_culinaria": tipo_culinaria,
                    "taxa_entrega": float(taxa_entrega),
                    "tempo_entrega_estimado": tempo_estimado,
                }
            )
            return True
        except Exception as e:
            print(f"Erro ao atualizar detalhes do restaurante: {e}")
            return False

    def update_restaurant_address(self, id_end_rest, endereco):
        try:
            self.db.collection("restaurant_addresses").document(str(id_end_rest)).update(
                {
                    "rua": endereco["rua"],
                    "num": endereco["num"],
                    "bairro": endereco["bairro"],
                    "cidade": endereco["cidade"],
                    "estado": endereco["estado"],
                    "cep": endereco["cep"],
                }
            )
            return True
        except Exception as e:
            print(f"Erro ao atualizar endereço do restaurante: {e}")
            return False

    # -------------------- FECHAR CONEXÃO --------------------
    def close(self):
        pass

    def __del__(self):
        self.close()
