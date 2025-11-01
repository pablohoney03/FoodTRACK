import tkinter as tk
import re
from datetime import datetime, date
from db import buscar_validade, buscar_estoque

alerta_pop = False  # controla exibição de pop-ups apenas 1 vez

def centralizar_janela(root, largura=None, altura=None):
    root.update_idletasks()
    if largura and altura:
        root.geometry(f"{largura}x{altura}")
    largura_atual = root.winfo_width()
    altura_atual = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (largura_atual // 2)
    y = (root.winfo_screenheight() // 2) - (altura_atual // 2)
    root.geometry(f"+{x}+{y}")

def destacar_item(tree, root, item_id, tempo=1500):
    if not tree.get_children():
        return
    for item in tree.get_children():
        valores = tree.item(item, "values")
        if valores and str(valores[0]) == str(item_id):
            tree.tag_configure("destaque", background="lightyellow")
            tree.item(item, tags=("destaque",))
            root.after(tempo, lambda i=item: tree.item(i, tags=()))
            tree.see(item)
            break

def mostrar_alertas(root):
    global alerta_pop
    if alerta_pop:
        return
    alerta_pop = True
    try:
        produtos_vencendo = buscar_validade(7)
        produtos_baixoe = buscar_estoque()
        if not produtos_vencendo and not produtos_baixoe:
            return

        alertas = []
        if produtos_vencendo:
            alertas.append("🔴 Próximos da validade (7 dias):")
            alertas += [f" • {p[1]} — validade {p[5]}" for p in produtos_vencendo]
            alertas.append("")
        if produtos_baixoe:
            alertas.append("🟠 Estoque baixo:")
            alertas += [f" • {p[1]} — {p[3]} {p[4]}" for p in produtos_baixoe]

        texto_alerta = "\n".join(alertas)

        popup = tk.Toplevel(root)
        popup.title("Avisos de Estoque")
        popup.geometry("400x280")
        x = root.winfo_x() + (root.winfo_width() // 2) - 200
        y = root.winfo_y() + (root.winfo_height() // 2) - 140
        popup.geometry(f"+{x}+{y}")
        popup.transient(root)

        tk.Label(popup, text="⚠️ Avisos", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        txt = tk.Text(popup, wrap="word", height=12, padx=10, pady=5)
        txt.insert("1.0", texto_alerta)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, padx=10)
        tk.Button(popup, text="Fechar", command=popup.destroy, width=12).pack(pady=10)
    except Exception as e:
        print("Erro ao verificar alertas:", e)

def formatar_quantidade(qtd, unidade):
    if qtd is None:
        qtd = 0
    return f"{qtd} {unidade or ''}".strip()

def formatar_validade(validade_str):
    if not validade_str:
        return "/"
    try:
        data_obj = datetime.strptime(validade_str, "%d/%m/%Y").date()
        return data_obj.strftime("%d/%m/%Y")
    except:
        return validade_str

def formatar_preco(valor, tipo=None):
    """Formata preço e adiciona '(venda)' ou '(compra)' se necessário."""
    if valor is None:
        return "-"
    # Garante que o valor seja float antes de formatar para evitar erros
    try:
        valor = float(valor)
    except (ValueError, TypeError):
        return "-" # Retorna algo padrão se a conversão falhar
    s = f"R$ {valor:.2f}"
    if tipo:
        s += f" ({tipo})"
    return s

def normalizar_data(data_str):
    if not data_str:
        return ""
    # Remove tudo que não for número
    numeros = re.sub(r'\D', '', data_str)
    if len(numeros) == 8:
        # ddmmaaaa
        try:
            return datetime.strptime(numeros, "%d%m%Y").strftime("%d/%m/%Y")
        except Exception:
            pass
    # Tenta outros formatos comuns
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(data_str, fmt).strftime("%d/%m/%Y")
        except Exception:
            continue
    # Se não conseguir, retorna como está
    return data_str
