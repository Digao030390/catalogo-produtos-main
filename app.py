from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_bcrypt import Bcrypt
import sqlite3
import base64
from functools import wraps

app = Flask(__name__)
app.secret_key = "troque-por-uma-chave-grande-e-aleatoria"  # obrigatório para usar session e flash
bcrypt = Bcrypt(app)

@app.route("/admin")
def index():
    return render_template("admin/index.html")

@app.route("/")
def ind2ex():
    conn = conexao()
    produto = conn.execute('''SELECT produto.*,
                           categoria.nome AS nome_categoria
                           FROM produto
                           LEFT JOIN categoria
                           ON produto.id_categoria = categoria.id
                           ORDER BY produto.preco ASC
                           LIMIT 3;''').fetchall()
    conn = conexao()
    categoria = conn.execute("select * from categoria")
    
    return render_template("site/index.html",produto = produto,categoria=categoria)



def conexao():
   conn=  sqlite3.connect('database.db')
   conn.row_factory = sqlite3.Row
   return conn

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = conexao()
        usuario = conn.execute('SELECT * FROM usuario WHERE username = ?',
                               (username,)).fetchone()
        conn.close()

        if usuario and bcrypt.check_password_hash(usuario['password_hash'], password):
            session['usuario'] = usuario['username']
            return redirect(url_for('index'))

        flash("Usuário ou senha inválidos.")

    return render_template('admin/login.html')


@app.route("/logout")
def logout():
    session.pop('usuario', None)
    flash("Você saiu do sistema.")
    return redirect(url_for('login'))

@app.route("/listar_categorias")
def listarCategoria():
    conn = conexao()
    categoria = conn.execute('select * from categoria')
    return render_template('admin/listar_categoria.html',
                           categorias = categoria)

@app.route("/cadastrar_categorias", methods=['GET','POST'])
def cadastrarCategoria():    

    if request.method == 'POST':
        nome_categoria = request.form.get('nome_categoria')
        descricao = request.form.get('descricao')
        ativo = request.form.get('ativo')
        imagem = request.files.get('imagem')              
        imagem_base64 = base64.b64encode(imagem.read()).decode('utf-8')
        if nome_categoria:
            conn = conexao()
            conn.execute('''INSERT INTO categoria (nome, descricao, 
             ativo, imagem )
              VALUES (?, ?, ?, ?)''',
                (nome_categoria, descricao, ativo, imagem_base64))            
            conn.commit()
            conn.close()
            return redirect(url_for('listarCategoria'))        
       
    return render_template('admin/cadastrar_categoria.html')



@app.route("/editarcategoria/<int:id>", methods=['GET','POST'])
def editarCategoria(id):
    conn = conexao()
    categoria = conn.execute('select * from categoria where id=?',
                             (id,)).fetchone()
    
    if request.method == 'POST':
        nome_categoria = request.form.get('nome_categoria')
        descricao = request.form.get('descricao')
        ativo = request.form.get('ativo')
        imagem = request.files.get('imagem')              
        imagem_base64 = base64.b64encode(imagem.read()).decode('utf-8')
        if nome_categoria:
            conn = conexao()
            if imagem:
                conn.execute('''UPDATE categoria SET nome=?, descricao=?,
                              ativo=?,
                              imagem=? WHERE id=?''',   
                (nome_categoria, descricao, ativo, imagem_base64, id,))           
            else:
                conn.execute('''UPDATE categoria SET nome=?, descricao=?,
                              ativo=? WHERE id=?''',   
                (nome_categoria, descricao, ativo, id,)) 

            conn.commit()
            conn.close()
            return redirect(url_for('listarCategoria'))

    return render_template('admin/editar_categoria.html',
                            categoria=categoria )


@app.route("/excluir_categoria/<int:id>", methods=['GET', 'POST'])
def excluirCategoria(id):
    conn = conexao()
    categoria = conn.execute('''SELECT * FROM categoria
          WHERE id = ?''', (id,)).fetchone()
    
    if request.method == 'POST':
        conn.execute('DELETE FROM categoria WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('listarCategoria'))    
  
    return render_template('admin/excluir_categoria.html', categoria = categoria )


@app.route("/listar_produtos")
def listarProduto():
    conn = conexao()
    produto = conn.execute('select * from produto')
    return render_template('admin/listar_produto.html',
                           produtos = produto)


@app.route("/excluir_produto/<int:id>", methods=['GET', 'POST'])
def excluirProduto(id):
    conn = conexao()
    produto = conn.execute('''SELECT * FROM produto
          WHERE id = ?''', (id,)).fetchone()
    
    if request.method == 'POST':
        conn.execute('DELETE FROM produto WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('listarProduto'))    
  
    return render_template('admin/excluir_produto.html', produto = produto )


@app.route("/editarproduto/<int:id>", methods=['GET','POST'])
def editarProduto(id):
    conn = conexao()
    produto = conn.execute('select * from produto where id=?',
                             (id,)).fetchone()
    
    if request.method == 'POST':
        nome_produto = request.form.get('nome_produto')
        preco = request.form.get('preco')
        ativo = request.form.get('ativo')
        imagem = request.files.get('imagem')              
        imagem_base64 = base64.b64encode(imagem.read()).decode('utf-8')
        if nome_produto:
            conn = conexao()
            if imagem:
                conn.execute('''UPDATE produto SET nome=?, preco=?,
                              ativo=?,
                              imagem=? WHERE id=?''',   
                (nome_produto, preco, ativo, imagem_base64, id,))           
            else:
                conn.execute('''UPDATE produto SET nome=?, preco=?,
                              ativo=? WHERE id=?''',   
                (nome_produto, preco, ativo, id,)) 

            conn.commit()
            conn.close()
            return redirect(url_for('listarProduto'))

    return render_template('admin/editar_produto.html',
                            produto=produto )

@app.route("/cadastrar_produto", methods=['GET','POST'])
def cadastrarProduto():
    if request.method == 'POST':
        nome_produto = request.form.get('nome_produto')
        preco = request.form.get('preco')
        ativo = request.form.get('ativo')
        id_categoria = request.form.get('id_categoria')
        imagem = request.files.get('imagem')
        
        if nome_produto:
            # Trata a imagem caso ela venha vazia
            imagem_base64 = base64.b64encode(imagem.read()).decode('utf-8') if imagem else ''
            
            conn = conexao()
            # Corrigida a ordem dos valores para bater com as colunas (nome, preco, ativo, imagem, id_categoria)
            conn.execute('''INSERT INTO produto (nome, preco, ativo, imagem, id_categoria)
                          VALUES (?, ?, ?, ?, ?)''',
                         (nome_produto, preco, ativo, imagem_base64, id_categoria))            
            conn.commit()
            conn.close()
            return redirect(url_for('listarProduto'))

    # Isso roda tanto no GET quanto se o POST falhar: busca os dados para exibir na tela
    conn = conexao()
    categorias = conn.execute("SELECT * FROM categoria").fetchall()
    produto = conn.execute("SELECT * FROM produto").fetchall()
    conn.close()
    
    return render_template('admin/cadastrar_produto.html', categorias=categorias, produto=produto)



@app.route("/verCategoria/<int:id>", methods=["GET", "POST"])
def verCategoria(id):
    conn = conexao()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM categoria WHERE id = ?", (id,))
    categoria = cursor.fetchone()
    
    cursor.execute("SELECT * FROM produto WHERE id_categoria = ?", (id,))
    produto = cursor.fetchall()
    
    conn.close()
        
    return render_template("site/verCategoria.html", categorias=categoria, produto=produto)
   

app.run(debug=True, port=5006 )