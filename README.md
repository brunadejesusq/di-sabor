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
      * **Firebase Admin SDK:** Conexão com o backend do Firebase.
  * **Frontend:**
      * **HTML5:** Estrutura das páginas.
      * **CSS3:** Estilização e design.
      * **JavaScript:** Interatividade e navegação no cliente.
  * **Banco de Dados:**
      * **Google Firestore:** Banco de documentos usado para armazenar dados da aplicação.

-----

## Como Executar o Projeto

Siga os passos abaixo para configurar e rodar a aplicação em seu ambiente local.

## Estrutura de Aplicações

O projeto foi dividido em três aplicações separadas:

- `customer_app.py`: app para cadastro e pedidos de clientes, consumindo apenas o restaurante Di Sabor Caseiro.
- `restaurant_app.py`: site de gerenciamento do restaurante, com pedidos, cardápio, horários e páginas de estoque/rotas para evoluir.
- `delivery_app.py`: app de motoboy para visualizar rotas de entrega e atualizar status de entregas.

> Cada app é independente e deve ser executado separadamente. Eles não compartilham a mesma página de entrada; cada um tem seu próprio servidor Flask e fluxo de navegação.
>
> Nota: arquivos legados (`app.py`, `main.py`, `database_manager_mysql.py`) não fazem parte do fluxo atual e foram deixados apenas para referência histórica. Os três apps principais usam `database_manager.py` com Firebase.

### 1\. Pré-requisitos

  * Python 3.x instalado.
  * Dependências listadas em `requirements.txt`.
  * Conta Firebase com projeto e credenciais de serviço.

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
    O projeto usa Flask com Firebase. Instale com:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure a conexão com o Firebase:**
    Coloque o arquivo de credenciais do Firebase `firebase_credentials.json` na raiz do projeto,
    ou defina a variável de ambiente `FIREBASE_CREDENTIALS` apontando para o caminho do arquivo.
    
    Exemplo no Windows:

    ```powershell
    setx FIREBASE_CREDENTIALS "C:\caminho\para\firebase_credentials.json"
    ```

    Exemplo no Linux/macOS:

    ```bash
    export FIREBASE_CREDENTIALS="/caminho/para/firebase_credentials.json"
    ```

5.  **Verifique se as credenciais estão acessíveis:**

    - Coloque `firebase_credentials.json` na raiz do projeto, ou
    - defina `FIREBASE_CREDENTIALS` apontando para o arquivo JSON válido.

6.  **Execute o app desejado:**

    ```bash
    python customer_app.py
    ```

    ou

    ```bash
    python restaurant_app.py
    ```

    ou

    ```bash
    python delivery_app.py
    ```

7.  **Alternativa no Windows:**

    ```powershell
    .\run_app.ps1 -App customer -CredentialsPath "C:\caminho\para\firebase_credentials.json"
    ```

    ```powershell
    .\run_app.ps1 -App restaurant
    ```

    ```powershell
    .\run_app.ps1 -App delivery
    ```

Abra seu navegador e acesse [http://127.0.0.1:5000](http://127.0.0.1:5000) para usar a aplicação.

-----

## Autores

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
