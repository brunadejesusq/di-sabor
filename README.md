# Sistema de Delivery - Laboratório de Banco de Dados

## Descrição do Projeto

A plataforma simula um serviço de delivery de comida, permitindo que usuários se cadastrem como **clientes** e realizem pedidos apenas no restaurante **Di Sabor Caseiro**.

  * **Clientes** podem navegar pelo restaurante, visualizar seu cardápio, montar um carrinho, fazer pedidos e acompanhar o status da entrega.
  * Restaurante **Di Sabor Caseiro** possui um painel administrativo para gerenciar seus dados, cardápio, horários de funcionamento, receber e atualizar o status dos pedidos.

-----

## Funcionalidades Principais

### Para Clientes

  * Cadastro e Login de usuário.
  * Visualização de todas as informações do restaurante Di Sabor Caseiro, com indicador de "Aberto" ou "Fechado".
  * Navegação pelo cardápio completo do restaurante.
  * Sistema de carrinho de compras funcional, permitindo adicionar, remover e atualizar itens.
  * Gerenciamento de múltiplos endereços de entrega.
  * Finalização de pedido com seleção de endereço e forma de pagamento.
  * Acompanhamento do status do pedido (`Pendente`, `Em Preparação`, etc.).
  * Sistema de avaliação do pedido após a entrega.

### Para Restaurante Di Sabor Caseiro

  * Painel administrativo para gerenciamento.
  * Recebimento e visualização de pedidos.
  * Atualização do status dos pedidos.
  * Gerenciamento completo do cardápio: criação de categorias e adição/edição/remoção de pratos.
  * Edição das informações do restaurante (nome, telefone, taxa de entrega, etc.).
  * Definição e edição dos horários de funcionamento para cada dia da semana.
  * Visualização das avaliações recebidas dos clientes.

### Para Motoboy

  * Cadastro e Login de motoboy.
  * Visualização de rotas de entrega e status.
  * Visualização dos dados do cliente, com nome e endereço.
  * Detalhes da rota para cada entrega.
  * Espaço para cadastro de conta para recebimento de gorjetas.

-----

## Tecnologias Utilizadas

  * **Backend:**
      * **Python 3:** Linguagem de programação principal.
      * **Flask:** Micro-framework web para a criação das rotas e lógica da aplicação.
  * **Frontend:**
      * **HTML5:** Estrutura das páginas.
      * **CSS3:** Estilização e design.
      * **JavaScript:** Interatividade e navegação no cliente.
  * **Banco de Dados:**
      * **MySQL:** Sistema de gerenciamento de banco de dados relacional.
      * **Railway:** Plataforma de nuvem para hospedagem do banco de dados MySQL.

-----

## Como Executar o Projeto

Siga os passos abaixo para configurar e rodar a aplicação em seu ambiente local.

## Estrutura de Aplicações

O projeto foi dividido em três aplicações separadas:

- `customer_app.py`: app para cadastro e pedidos de clientes, consumindo apenas o restaurante Di Sabor Caseiro.
- `restaurant_app.py`: site de gerenciamento do restaurante, com pedidos, cardápio, horários e páginas de estoque/rotas para evoluir.
- `delivery_app.py`: app de motoboy para visualizar rotas de entrega e atualizar status de entregas.

> Nota: arquivos legados (`app.py`, `main.py`, `database_manager.py`) não fazem parte do fluxo atual com MySQL e foram realocados para manter o projeto concentrado nos três apps principais.

### 1\. Pré-requisitos

  * Python 3.x instalado.
  * Dependências (estão abaixo).
  * Instalar `mysql-connector-python` para conexão com MySQL.

2.  **Crie e ative um ambiente virtual:**

    ```bash
    # Para Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    O projeto usa Flask com MySQL. Instale com:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure a Conexão com o Banco de Dados:**
    Atualize o arquivo `my.cnf` com as credenciais do seu MySQL local ou remoto.
    Certifique-se de que o banco de dados esteja acessível e que as tabelas estejam criadas a partir de `restaurante.sql`.

### 2\. Executando a Aplicação

Com o ambiente configurado, inicie o servidor Flask com um dos apps:

```bash
python customer_app.py
```

```bash
python restaurant_app.py
```

```bash
python delivery_app.py
```

Abra seu navegador e acesse [http://127.0.0.1:5000](http://127.0.0.1:5000) para ver a aplicação funcionando.

-----

## Autores

  * Mariana
  * Anna Bheatryz
