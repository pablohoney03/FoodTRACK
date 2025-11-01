import tkinter as tk
from tkinter import ttk, messagebox
#import customtkinter as ctk
from datetime import datetime
from db import criar_tab, inserir_item, buscar_todos, atualizar_item, deletar_item, buscar_validade, buscar_estoque, verificar_login, registrar_usuario
from utils import centralizar_janela, destacar_item, mostrar_alertas, formatar_quantidade, formatar_validade, normalizar_data

criar_tab()
modo = None
item_atualizando = None  
frame_login = None
frame_cadastro = None
alerta_pop = False

# --- TELA DE LOGIN ---
def abrir_login():
    global frame_login, entry_user, entry_senha, frame_cadastro
    if frame_login is None:
        frame_login = tk.Frame(root)
        tk.Label(frame_login, text="Login", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(frame_login, text="Usuário:").pack()
        entry_user = tk.Entry(frame_login, width=30)
        entry_user.pack(pady=5)

        tk.Label(frame_login, text="Senha:").pack()
        entry_senha = tk.Entry(frame_login, width=30, show="*")
        entry_senha.pack(pady=5)

        tk.Button(frame_login, text="Entrar", width=20, command=tentar_login).pack(pady=10)
        tk.Button(frame_login, text="Cadastrar novo usuário", width=20, command=abrir_tela_registro).pack(pady=5)

    if frame_cadastro:
        frame_cadastro.pack_forget()  # esconde registro
    frame_login.pack(fill="both", expand=True)
    centralizar_janela(root, 300, 300)

def tentar_login():
        usuario = entry_user.get().strip()
        senha = entry_senha.get().strip()

        if not usuario or not senha:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        if verificar_login(usuario, senha):
            messagebox.showinfo("Sucesso", f"Bem-vindo, {usuario}!")
            frame_login.pack_forget()
            frame_inicial.pack(fill="both", expand=True)
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")

def abrir_resgistraru():
        frame_login.pack_forget()
        abrir_tela_registro()

        tk.Button(frame_login, text="Entrar", width=20, command=tentar_login).pack(pady=10)
        tk.Button(frame_login, text="Cadastrar novo usuário", command=abrir_tela_registro).pack(pady=5)

        frame_login.pack(fill="both", expand=True)
        centralizar_janela(root, 300, 300)

def abrir_tela_registro():
    frame_cadastro_user = tk.Frame(root)

    tk.Label(frame_cadastro_user, text="Cadastro de Usuário", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Label(frame_cadastro_user, text="Usuário:").pack()
    entry_user = tk.Entry(frame_cadastro_user, width=30)
    entry_user.pack(pady=5)

    tk.Label(frame_cadastro_user, text="Senha:").pack()
    entry_senha = tk.Entry(frame_cadastro_user, width=30, show="*")
    entry_senha.pack(pady=5)

    def registrar():
        usuario = entry_user.get().strip()
        senha = entry_senha.get().strip()

        if not usuario or not senha:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        if registrar_usuario(usuario, senha):
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            frame_cadastro_user.pack_forget()
            abrir_login()
        else:
            messagebox.showerror("Erro", "Usuário já existe!")

    tk.Button(frame_cadastro_user, text="Cadastrar", width=20, command=registrar).pack(pady=10)
    tk.Button(frame_cadastro_user, text="Voltar", width=20, command=lambda: (frame_cadastro_user.pack_forget(), abrir_login())).pack()

    frame_login.pack_forget()  # esconde login
    frame_cadastro_user.pack(fill="both", expand=True)
    centralizar_janela(root, 300, 300)


# === FUNÇÕES DE NAVEGAÇÃO === #
def abrir_cadastro(acao, dados=None):
    global modo, item_atualizando
    modo = acao  # "novo" ou "atualizar"

    frame_inicial.pack_forget()

    root.geometry("400x400")
    root.resizable(False, False)

    if 'frame_consulta' in globals():
        frame_consulta.pack_forget()

    criar_tela_cadastro(dados)
    
def voltar_inicio():
    root.state('normal')
    root.geometry("350x250")
    root.resizable(True, True)

     # reposiciona a janela no centro da tela
    centralizar_janela(root, 350, 250)

    if 'frame_cadastro' in globals() and frame_cadastro:
        frame_cadastro.pack_forget()
    if 'frame_consulta' in globals() and frame_consulta:
        frame_consulta.pack_forget()
    if 'frame_login' in globals() and frame_login:
        frame_login.pack_forget()

    frame_inicial.pack(fill="both", expand=True)

# === SALVAR (INSERIR OU ATUALIZAR) === #
def salvar():
    global modo, item_atualizando
    nome = entry_nome.get().strip()
    categoria = combo_categoria.get()
    unidade = combo_unidade.get().strip()
    validade = normalizar_data(entry_validade.get().strip())

    try:
        quantidade = float(entry_quantidade.get())
    except ValueError:
        messagebox.showerror("Erro", "Quantidade inválida!")
        return

    preco_venda = None
    preco_compra = None

    try:
        preco_input = entry_preco.get().replace("R$", "").replace(",", ".").strip()
        if preco_input:  # Só converte se não estiver vazio
            preco_valor = float(preco_input)
            
            if categoria == "Produto":
                preco_venda = preco_valor
            elif categoria == "Ingrediente":
                preco_compra = preco_valor
    except ValueError:
        messagebox.showerror("Erro", "Preço inválido!")
        return

    if modo == "atualizar":
        atualizar_item(item_atualizando, nome, categoria, quantidade, unidade, validade, preco_venda, preco_compra)
        messagebox.showinfo("Sucesso", f"Item ID {item_atualizando} atualizado com sucesso!")

        # Atualiza a visualização
        frame_cadastro.pack_forget()
        criar_tela_consulta()
        
        # Destaca o item atualizado
        if 'tree' in globals():
            root.after(200, lambda: destacar_item(tree, root, item_atualizando))

    else:  # modo novo
        inserir_item(nome, categoria, quantidade, unidade, validade, preco_venda, preco_compra)
        messagebox.showinfo("Sucesso", f"{categoria} cadastrado com sucesso!")
        voltar_inicio()

# === TELA DE CADASTRO === #
def criar_tela_cadastro(dados=None):
    global entry_nome, combo_categoria, entry_quantidade, combo_unidade, entry_validade, entry_preco, frame_cadastro, label_modo

    frame_cadastro = tk.Frame(root)

    label_modo = tk.Label(frame_cadastro, text=f"Modo: {modo.upper()}", font=("Arial", 12))
    label_modo.pack(pady=5)

    tk.Label(frame_cadastro, text="Nome: ").pack()
    entry_nome = tk.Entry(frame_cadastro, width=40)
    entry_nome.pack()

    tk.Label(frame_cadastro, text="Categoria: ").pack()
    combo_categoria = ttk.Combobox(frame_cadastro, values=["Produto", "Ingrediente"])
    combo_categoria.pack()

    tk.Label(frame_cadastro, text="Quantidade: ").pack()
    entry_quantidade = tk.Entry(frame_cadastro, width=20)
    entry_quantidade.pack()

    tk.Label(frame_cadastro, text="Unidade:").pack()
    combo_unidade = ttk.Combobox(frame_cadastro, values=["un", "kg", "g", "l", "ml"])
    combo_unidade.pack()

    tk.Label(frame_cadastro, text="Validade (DD-MM-AAAA): ").pack()
    entry_validade = tk.Entry(frame_cadastro, width=20)
    entry_validade.pack()

    tk.Label(frame_cadastro, text="Preço:").pack()
    entry_preco = tk.Entry(frame_cadastro, width=20)
    entry_preco.pack()

    # Preenche automaticamente se for modo de atualização
    if dados:
        entry_nome.insert(0, dados["nome"])
        combo_categoria.set(dados["categoria"])
        entry_quantidade.insert(0, dados["quantidade"])
        combo_unidade.insert(0, dados["unidade"])
        entry_validade.insert(0, dados["validade"])
        if dados["categoria"] == "Produto":
            entry_preco.insert(0, dados["preco_venda"] or "")
        else:
            entry_preco.insert(0, dados["preco_compra"] or "")

    btn_salvar = tk.Button(frame_cadastro, text="Salvar", command=salvar)
    btn_salvar.pack(pady=10)

    if modo == "atualizar":
        btn_voltar = tk.Button(frame_cadastro, text="Voltar", command=lambda: (
            frame_cadastro.pack_forget(),
            criar_tela_consulta()
        ))
        btn_voltar.pack(pady=5)

    # Botão "Sair" sempre volta à tela inicial
    btn_sair = tk.Button(frame_cadastro, text="Sair", command=voltar_inicio)
    btn_sair.pack(pady=5)

    frame_cadastro.pack(fill="both", expand=True)

# === TELA DE CONSULTA === #
def abrir_consulta():
    frame_inicial.pack_forget()
    root.state('zoomed')
    criar_tela_consulta()

def criar_tela_consulta():
    global frame_consulta, alerta_pop, tree
    frame_consulta = tk.Frame(root)
    frame_consulta.pack(fill="both", expand=True)

    tk.Label(frame_consulta, text="📦 Estoque", font=("Arial", 12)).pack(pady=10)

    # Painel filtro (criado primeiro mas escondido)
    frame_filtro = tk.LabelFrame(frame_consulta, text="Filtros", padx=10, pady=10)
    frame_filtro.pack_forget()  # escondido inicialmente

    # Variáveis Filtro
    var_produto = tk.BooleanVar(value=True)
    var_ingrediente = tk.BooleanVar(value=True)

    tk.Checkbutton(frame_filtro, text="Produto", variable=var_produto).grid(row=0, column=0, sticky="w")
    tk.Checkbutton(frame_filtro, text="Ingrediente", variable=var_ingrediente).grid(row=0, column=1, sticky="w")

    # Treeview (criado depois do frame_filtro)
    colunas = ("id", "nome", "categoria", "quantidade", "unidade", "validade", "preço")
    tree = ttk.Treeview(frame_consulta, columns=colunas, show="headings", height=10)
    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # Frame para botão de filtro (criado depois do treeview mas posicionado antes)
    frame_filtro_btn = tk.Frame(frame_consulta)
    frame_filtro_btn.pack(fill="x", pady=5, before=tree)  # posiciona antes da tabela

    # Função toggle_filtro definida ANTES de ser usada
    def toggle_filtro():
        if frame_filtro.winfo_ismapped():
            frame_filtro.pack_forget()
        else:
            frame_filtro.pack(fill="x", padx=10, pady=5, before=tree)

    # Agora cria o botão que usa a função
    tk.Button(frame_filtro_btn, text="Filtrar 🔽", command=toggle_filtro).pack(side="right", padx=20)

    ordem_colunas = {col: 0 for col in colunas}  # 0: original, 1: crescente, 2: decrescente
    ordem_original = []  # armazenará a ordem inicial

    def carregar_registros(*args):
        nonlocal ordem_original
        from datetime import datetime, date

        categorias = []
        if var_produto.get():
            categorias.append("Produto")
        if var_ingrediente.get():
            categorias.append("Ingrediente")

        tree.delete(*tree.get_children())

        registros = buscar_todos()
        vencendo = {r[0] for r in buscar_validade(7)}      # IDs perto do vencimento
        baixo_estoque = {r[0] for r in buscar_estoque()}   # IDs com pouco estoque

        # Configura as cores das linhas
        tree.tag_configure("vencido", background="#ffcccc")       # vermelho claro
        tree.tag_configure("sem_estoque", background="#ffe0e0")   # rosa claro
        tree.tag_configure("alerta", background="#fff4cc")        # amarelo claro
        tree.tag_configure("ok", background="white")

        hoje = date.today()

        for row in registros:
            validade_str = row[5]
            tag = "ok"
            alerta_val = ""
            alerta_qtd = ""

            # === Trata validade ===
            data_obj = None
            if validade_str:
                try:
                    data_obj = datetime.strptime(validade_str, "%d/%m/%Y").date()
                    if data_obj < hoje:
                        tag = "vencido"
                    elif row[0] in vencendo:
                        alerta_val = "⚠️"
                        tag = "alerta"
                except Exception:
                    pass

            validade_display = f"{validade_str or '-'} {alerta_val}".strip()

            # === Trata estoque ===
            quantidade = float(row[3]) if row[3] else 0
            unidade = (row[4] or "").lower()

            if quantidade <= 0:
                tag = "sem_estoque"
            elif row[0] in baixo_estoque and tag == "ok":
                alerta_qtd = "⚠️"
                tag = "alerta"

            quantidade_display = f"{quantidade} {unidade} {alerta_qtd}".strip()

            # === Preço ===
            preco = "-"
            if row[2] == "Produto" and row[6] is not None:
                preco = f"R$ {row[6]:.2f} (venda)"
            elif row[2] == "Ingrediente" and row[7] is not None:
                preco = f"R$ {row[7]:.2f} (compra)"

            # === Insere na tabela ===
            tree.insert(
                "",
                tk.END,
                values=(row[0], row[1], row[2], quantidade_display, unidade, validade_display, preco),
                tags=(tag,)
            )

        ordem_original = tree.get_children()

    def ordenar_coluna(col):
        children = list(tree.get_children())
        if not children:
            return
            
        valores_originais = [(tree.set(k, col), k) for k in children]

        if ordem_colunas[col] == 0:  # crescente
            if col == "quantidade":
                valores = sorted(valores_originais, key=lambda t: float(t[0]) if t[0] and t[0].replace('.','').isdigit() else 0)
            elif col == "preço":
                # Ordenação especial para preço formatado
                def extrair_preco(valor):
                    if valor == "-":
                        return 0
                    try:
                        # Remove "R$", "(venda)", "(compra)" e converte
                        preco_limpo = valor.split("R$")[1].split("(")[0].strip()
                        return float(preco_limpo.replace(",", "."))
                    except:
                        return 0
                valores = sorted(valores_originais, key=lambda t: extrair_preco(t[0]))
            elif col == "validade":
                def parse_data(v):
                    try:
                        return datetime.strptime(v, "%d/%m/%Y")
                    except:
                        return datetime.max
                valores = sorted(valores_originais, key=lambda t: parse_data(t[0]))
            else:
                valores = sorted(valores_originais, key=lambda t: t[0].lower() if t[0] else "")
            ordem_colunas[col] = 1

        elif ordem_colunas[col] == 1:  # decrescente
            if col == "quantidade":
                valores = sorted(valores_originais, key=lambda t: float(t[0]) if t[0] and t[0].replace('.','').isdigit() else 0, reverse=True)
            elif col == "preço":
                def extrair_preco(valor):
                    if valor == "-":
                        return 0
                    try:
                        preco_limpo = valor.split("R$")[1].split("(")[0].strip()
                        return float(preco_limpo.replace(",", "."))
                    except:
                        return 0
                valores = sorted(valores_originais, key=lambda t: extrair_preco(t[0]), reverse=True)
            elif col == "validade":
                def parse_data(v):
                    try:
                        return datetime.strptime(v, "%d/%m/%Y")
                    except:
                        return datetime.min
                valores = sorted(valores_originais, key=lambda t: parse_data(t[0]), reverse=True)
            else:
                valores = sorted(valores_originais, key=lambda t: t[0].lower() if t[0] else "", reverse=True)
            ordem_colunas[col] = 2

        else:  # volta à ordem original
            for index, k in enumerate(ordem_original):
                tree.move(k, "", index)
            ordem_colunas[col] = 0
            return

        for index, (val, k) in enumerate(valores):
            tree.move(k, "", index)

    # Configurar colunas
    for col in colunas:
        tree.heading(col, text=col.capitalize(), command=lambda c=col: ordenar_coluna(c))
        if col == "id":
            tree.column(col, width=50, anchor="center")
        elif col == "nome":
            tree.column(col, width=150, anchor="w")
        elif col in ("quantidade", "unidade"):
            tree.column(col, width=80, anchor="center")
        elif col == "validade":
            tree.column(col, width=100, anchor="center")
        elif col == "preço":
            tree.column(col, width=120, anchor="center")
        else:
            tree.column(col, width=100, anchor="center")

    # Atualiza automaticamente quando filtros mudam
    var_produto.trace_add("write", carregar_registros)
    var_ingrediente.trace_add("write", carregar_registros)

    # Carrega tudo inicialmente
    carregar_registros()

    # Botões
    frame_botoes = tk.Frame(frame_consulta)
    frame_botoes.pack(pady=10)

    tk.Button(frame_botoes, text="Atualizar", width=15, command=atualizar_selecionado).pack(side="left", padx=10)
    tk.Button(frame_botoes, text="Deletar", width=15, command=deletar_selecionado).pack(side="left", padx=10)
    tk.Button(frame_botoes, text="Voltar", width=15, command=voltar_inicio).pack(side="left", padx=10)

    # ALERTAS  
    mostrar_alertas(root)

    frame_consulta.pack(fill="both", expand=True)
    
# === ATUALIZAR E DELETAR === #
def atualizar_selecionado():
    global item_atualizando
    item = tree.selection()
    if not item:
        messagebox.showerror("Erro", "Selecione um item para atualizar.")
        return
    
    # Pega os valores do item selecionado
    valores = tree.item(item[0], "values")
    item_atualizando = valores[0]  # ID do item
    
    # Busca os dados completos do banco de dados
    registros = buscar_todos()
    dados_completos = None
    
    for registro in registros:
        if str(registro[0]) == str(item_atualizando):
            dados_completos = {
                "id": registro[0],
                "nome": registro[1],
                "categoria": registro[2],
                "quantidade": registro[3],
                "unidade": registro[4],
                "validade": registro[5] if registro[5] else "",
                "preco_venda": registro[6],
                "preco_compra": registro[7]
            }
            break
    
    if dados_completos:
        abrir_cadastro("atualizar", dados_completos)
    else:
        messagebox.showerror("Erro", "Não foi possível carregar os dados do item.")

def deletar_selecionado():
    item = tree.selection()
    if not item:
        messagebox.showerror("Erro", "Selecione um item para deletar.")
        return

    valores = tree.item(item, "values")
    item_id = valores[0]
    deletar_item(item_id)
    messagebox.showinfo("Sucesso", f"Item ID {item_id} deletado com sucesso!")
    tree.delete(item)

# === JANELA PRINCIPAL === #
root = tk.Tk()
root.title("FoodTRACK")
centralizar_janela(root, 300, 250)

frame_inicial = tk.Frame(root)

tk.Label(frame_inicial, text="Qual a função desejada ?", font=("Arial", 12)).pack(pady=20)

btn_novo = tk.Button(frame_inicial, text="Registrar Novo", width=20, command=lambda: abrir_cadastro("novo"))
btn_novo.pack(pady=5)

btn_atualizar = tk.Button(frame_inicial, text="Consultar Estoque", width=20, command=abrir_consulta)
btn_atualizar.pack(pady=5)

btn_sair = tk.Button(frame_inicial, text="Sair", width=5, command=root.destroy)
btn_sair.pack(pady=5)

abrir_login()

root.mainloop()
