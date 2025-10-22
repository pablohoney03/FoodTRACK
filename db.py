import sqlite3
from datetime import datetime, timedelta

# conecta ao banco de dados e retorna a conexão
def conectar():
    return sqlite3.connect("estoque.db")

# cria a tabela se ela não existir
def criar_tab():
    con = conectar()
    cursor = con.cursor()
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria TEXT NOT NULL, -- 'Produto' ou 'Ingrediente'
        quantidade REAL NOT NULL,
        unidade TEXT,
        validade DATE,
        preco_venda REAL,
        preco_compra REAL )""")

    con.commit()
    con.close()


def inserir_item(nome, categoria, quantidade, unidade, validade, preco_venda=None, preco_compra=None):
    con = conectar()
    cursor = con.cursor()

    cursor.execute("""
        SELECT id, quantidade FROM produtos
        WHERE nome = ? AND categoria = ?
    """, (nome, categoria))
    existente = cursor.fetchone()

    if existente:
        novo_valor = existente[1] + quantidade
        cursor.execute("""
            UPDATE produtos
            SET quantidade = ?, unidade = ?, validade = ?, preco_venda = ?, preco_compra = ?
            WHERE id = ?
        """, (novo_valor, unidade, validade, preco_venda, preco_compra, existente[0]))
        print(f"[ATUALIZADO] Produto '{nome}' já existia. Nova quantidade: {novo_valor} {unidade}.")
    else:
        cursor.execute("""
            INSERT INTO produtos (nome, categoria, quantidade, unidade, validade, preco_venda, preco_compra)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nome, categoria, quantidade, unidade, validade, preco_venda, preco_compra))
        print(f"[NOVO] Produto '{nome}' cadastrado com sucesso!")

    con.commit()
    con.close()

def buscar_todos():
    con = sqlite3.connect("estoque.db")
    cursor = con.cursor()
    cursor.execute("SELECT * FROM produtos")
    registros = cursor.fetchall()
    con.close()
    return registros

def atualizar_item(item_id, nome, categoria, quantidade, unidade, validade, preco_venda, preco_compra):
    con = conectar()
    cursor = con.cursor()
    cursor.execute("""
        UPDATE produtos
        SET nome=?, categoria=?, quantidade=?, unidade=?, validade=?, preco_venda=?, preco_compra=?
        WHERE id=?
    """, (nome, categoria, quantidade, unidade, validade, preco_venda, preco_compra, item_id))
    con.commit()
    con.close()
    
def deletar_item(item_id):
    con = conectar()
    cursor = con.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (item_id,))
    con.commit()
    con.close()

def buscar_validade(dias=7):
    con = conectar()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM produtos WHERE validade IS NOT NULL AND validade != ''")
    resultados = []

    hoje = datetime.now().date()
    limite = hoje + timedelta(days=dias)

    for row in cursor.fetchall():
        try:
            validade = datetime.strptime(row[5], "%d/%m/%Y").date()
            if hoje <= validade <= limite:
                resultados.append(row)
        except Exception:
            pass

    con.close()
    return resultados

def buscar_estoque(limite=5):
    con = conectar()
    cursor = con.cursor()
    cursor.execute("""
        SELECT * FROM produtos
        WHERE quantidade <= ?
    """, (limite,))
    registros = cursor.fetchall()
    con.close()
    return registros

