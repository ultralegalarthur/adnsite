from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def ligar_banco():
    return psycopg2.connect(
        host="localhost",
        database="LojaRoupas",
        user="postgres",
        password="senai",
        port=5432
    )

# --- ROTAS DE NAVEGAÇÃO E PRODUTOS ---

@app.route('/')
def inicio():
    banco = ligar_banco()
    cursor = banco.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM produto ORDER BY id_produto')
    produtos = cursor.fetchall()
    cursor.close()
    banco.close()
    return render_template('index.html', produtos=produtos)

@app.route('/colecionadores')
def colecionadores():
    banco = ligar_banco()
    cursor = banco.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM produto WHERE categoria = 'colecionador' ORDER BY id_produto")
    produtos = cursor.fetchall()
    cursor.close()
    banco.close()
    return render_template('colecionadores.html', produtos=produtos)

@app.route('/novidades')
def novidades():
    banco = ligar_banco()
    cursor = banco.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM produto ORDER BY id_produto DESC LIMIT 6")
    produtos = cursor.fetchall()
    cursor.close()
    banco.close()
    return render_template('novidades.html', produtos=produtos)

@app.route('/starwars')
def starwars():
    banco = ligar_banco()
    cursor = banco.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM produto WHERE categoria = 'starwars' ORDER BY id_produto")
    produtos = cursor.fetchall()
    cursor.close()
    banco.close()
    return render_template('starwars.html', produtos=produtos)

# --- CRUD DE PRODUTOS ---

@app.route('/cadastro_produto')
def cadastro_produto():
    return render_template('cadastro_produto.html')

@app.route('/criar_produto', methods=['POST'])
def criar_produto():
    nome = request.form['nome']
    preco = request.form['preco']
    tamanho = request.form['tamanho']
    categoria = request.form['categoria']
    imagem = request.form['imagem']
    descricao = request.form['descricao']

    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute(
        '''
        INSERT INTO produto (nome, preco, tamanho, categoria, imagem, descricao)
        VALUES (%s, %s, %s, %s, %s, %s)
        ''',
        (nome, preco, tamanho, categoria, imagem, descricao)
    )
    banco.commit()
    cursor.close()
    banco.close()

    return redirect('/exibir_produtos')

@app.route('/exibir_produtos')
def exibir_produtos():
    banco = ligar_banco()
    cursor = banco.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM produto ORDER BY id_produto')
    produtos = cursor.fetchall()
    cursor.close()
    banco.close()
    return render_template('exibir_produtos.html', produtos=produtos)

@app.route('/editar_produto/<id_produto>')
def editar_produto(id_produto):
    banco = ligar_banco()
    cursor = banco.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM produto WHERE id_produto = %s', (id_produto,))
    produto = cursor.fetchone()
    cursor.close()
    banco.close()
    return render_template('editar_produto.html', produto=produto)

@app.route('/atualizar_produto', methods=['POST'])
def atualizar_produto():
    id_produto = request.form['id_produto']
    nome = request.form['nome']
    preco = request.form['preco']
    tamanho = request.form['tamanho']
    categoria = request.form['categoria']
    imagem = request.form['imagem']
    descricao = request.form['descricao']

    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute(
        '''
        UPDATE produto 
        SET nome=%s, preco=%s, tamanho=%s, categoria=%s, imagem=%s, descricao=%s
        WHERE id_produto=%s
        ''',
        (nome, preco, tamanho, categoria, imagem, descricao, id_produto)
    )
    banco.commit()
    cursor.close()
    banco.close()
    return redirect('/exibir_produtos')

@app.route('/excluir_produto/<id_produto>')
def excluir_produto(id_produto):
    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute('DELETE FROM produto WHERE id_produto = %s', (id_produto,))
    banco.commit()
    cursor.close()
    banco.close()
    return redirect('/exibir_produtos')

# --- CLIENTES E AUTENTICAÇÃO ---

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/criar_cliente', methods=['POST'])
def criar_cliente():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    cpf = request.form.get('cpf', '')
    telefone = request.form.get('telefone', '')

    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute(
        '''
        INSERT INTO cliente (nome, email, senha, cpf, telefone)
        VALUES (%s, %s, %s, %s, %s)
        ''',
        (nome, email, senha, cpf, telefone)
    )
    banco.commit()
    cursor.close()
    banco.close()
    return redirect('/login')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/autenticar', methods=['POST'])
def autenticar():
    email = request.form['email']
    senha = request.form['senha']

    banco = ligar_banco()
    cursor = banco.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM cliente WHERE email=%s AND senha=%s', (email, senha))
    usuario = cursor.fetchone()
    cursor.close()
    banco.close()

    if usuario:
        return redirect('/')
    return redirect('/login')

# --- CARRINHO ---

@app.route('/carrinho')
def carrinho():
    banco = ligar_banco()
    cursor = banco.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        '''
        SELECT item_carrinho.id_item, produto.nome, produto.preco, produto.imagem, item_carrinho.quantidade
        FROM item_carrinho, produto
        WHERE item_carrinho.produto_id = produto.id_produto
        '''
    )
    itens = cursor.fetchall()
    cursor.close()
    banco.close()
    return render_template('carrinho.html', itens=itens)

@app.route('/adicionar_carrinho/<id_produto>')
def adicionar_carrinho(id_produto):
    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute(
        'INSERT INTO item_carrinho (produto_id, quantidade) VALUES (%s, %s)',
        (id_produto, 1)
    )
    banco.commit()
    cursor.close()
    banco.close()
    return redirect('/carrinho')

@app.route('/remover_carrinho/<id_item>')
def remover_carrinho(id_item):
    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute('DELETE FROM item_carrinho WHERE id_item = %s', (id_item,))
    banco.commit()
    cursor.close()
    banco.close()
    return redirect('/carrinho')

@app.route('/contato')
def contato():
    return render_template('contato.html')

if __name__ == '__main__':
    app.run(debug=True)