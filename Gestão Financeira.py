import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import webbrowser
import threading
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AppControleFinanceiro:
    def __init__(self, root):
        self.root = root
        self.root.title("Consultoria e Gestão Financeira - Painel Corporativo")
        self.root.geometry("1200x750")
        
        self.inicializar_banco_dados()
        self.criar_tela_login()

    # =========================================================================
    # CONFIGURAÇÃO DO BANCO DE DADOS
    # =========================================================================
    def inicializar_banco_dados(self):
        self.conexao = sqlite3.connect("sistema_gestao.db")
        self.cursor = self.conexao.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS entidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                nome TEXT NOT NULL,
                cnpj TEXT,
                telefone TEXT,
                localidade TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                part_number TEXT NOT NULL,
                fornecedor TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contas_pagar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                forma TEXT NOT NULL,
                parcelas TEXT NOT NULL,
                vencimento TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contas_receber (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                vencimento TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        self.conexao.commit()

    # =========================================================================
    # TELA DE LOGIN E CADASTRO
    # =========================================================================
    def criar_tela_login(self):
        self.frame_login = tk.Frame(self.root, bg="#f4f6f9")
        self.frame_login.place(relx=0.5, rely=0.5, anchor="center", width=450, height=500)
        
        card = tk.Frame(self.frame_login, bg="white", highlightbackground="#e2e8f0", highlightthickness=1, padx=30, pady=30)
        card.pack(fill="both", expand=True)
        
        self.lbl_titulo_auth = tk.Label(card, text="Acesso ao Sistema", font=("Arial", 18, "bold"), fg="#1a365d", bg="white")
        self.lbl_titulo_auth.pack(pady=(10, 20))
        
        tk.Label(card, text="E-mail Corporativo / Usuário:", font=("Arial", 10, "bold"), fg="#4a5568", bg="white").pack(anchor="w", pady=(10, 2))
        self.entry_login_email = ttk.Entry(card, font=("Arial", 11), width=35)
        self.entry_login_email.pack(fill="x", ipady=4, pady=(0, 15))
        
        tk.Label(card, text="Senha de Acesso:", font=("Arial", 10, "bold"), fg="#4a5568", bg="white").pack(anchor="w", pady=(5, 2))
        self.entry_login_senha = ttk.Entry(card, font=("Arial", 11), width=35, show="*")
        self.entry_login_senha.pack(fill="x", ipady=4, pady=(0, 25))
        
        self.btn_acao_auth = ttk.Button(card, text="Acessar Sistema", command=self.processar_autenticacao)
        self.btn_acao_auth.pack(fill="x", ipady=5, pady=(0, 15))
        
        self.modo_cadastro = False
        self.lbl_alternar_modo = tk.Label(card, text="Não tem uma conta? Quero me cadastrar", font=("Arial", 10, "underline"), fg="#2b6cb0", bg="white", cursor="hand2")
        self.lbl_alternar_modo.pack(pady=5)
        self.lbl_alternar_modo.bind("<Button-1>", self.alternar_modo_auth)

    def alternar_modo_auth(self, event):
        self.modo_cadastro = not self.modo_cadastro
        if self.modo_cadastro:
            self.lbl_titulo_auth.config(text="Criar Nova Conta")
            self.btn_acao_auth.config(text="Cadastrar e Salvar")
            self.lbl_alternar_modo.config(text="Já tenho conta? Fazer Login")
        else:
            self.lbl_titulo_auth.config(text="Acesso ao Sistema")
            self.btn_acao_auth.config(text="Acessar Sistema")
            self.lbl_alternar_modo.config(text="Não tem uma conta? Quero me cadastrar")

    def processar_autenticacao(self):
        email = self.entry_login_email.get().strip().lower()
        senha = self.entry_login_senha.get().strip()
        
        if not email or not senha:
            messagebox.showerror("Aviso", "Preencha todos os campos para prosseguir.")
            return
            
        if self.modo_cadastro:
            self.cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
            if self.cursor.fetchone():
                messagebox.showerror("Erro de Cadastro", "Este e-mail já está cadastrado.")
                return
            self.cursor.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)", (email, senha))
            self.conexao.commit()
            messagebox.showinfo("Sucesso", "Conta criada! Faça login para acessar.")
            self.alternar_modo_auth(None)
        else:
            self.cursor.execute("SELECT id FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
            usuario = self.cursor.fetchone()
            if usuario:
                self.usuario_logado_id = usuario[0]
                self.frame_login.destroy()
                self.construir_painel_principal()
            else:
                messagebox.showerror("Erro de Acesso", "E-mail ou senha incorretos.")

    # =========================================================================
    # CONSTRUÇÃO DO PAINEL PRINCIPAL
    # =========================================================================
    def construir_painel_principal(self):
        self.container_main = tk.Frame(self.root, bg="#f4f6f9")
        self.container_main.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(self.container_main)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=(15, 5))
        
        self.aba_dashboard = ttk.Frame(self.notebook)
        self.aba_entidades = ttk.Frame(self.notebook)
        self.aba_estoque = ttk.Frame(self.notebook)
        self.aba_pagar = ttk.Frame(self.notebook)
        self.aba_receber = ttk.Frame(self.notebook)
        self.aba_inadimplencia = ttk.Frame(self.notebook)
        
        self.notebook.add(self.aba_dashboard, text="Dashboard Executivo")
        self.notebook.add(self.aba_entidades, text="Cadastro de Entidades")
        self.notebook.add(self.aba_estoque, text="Gerenciamento de Estoque")
        self.notebook.add(self.aba_pagar, text="Contas a Pagar")
        self.notebook.add(self.aba_receber, text="Contas a Receber")
        self.notebook.add(self.aba_inadimplencia, text="Gestão de Inadimplência")
        
        self.notebook.bind("<<NotebookTabChanged>>", self.ao_alternar_aba)
        
        self.criar_layout_entidades()
        self.criar_layout_estoque()
        self.criar_layout_contas_pagar()
        self.criar_layout_contas_receber()
        
        self.atualizar_combos_vinculo_entidades()
        
        self.criar_barra_botoes_atalho()
        self.renderizar_dashboard_executivo()

    def ao_alternar_aba(self, event):
        aba_atual = self.notebook.index(self.notebook.select())
        self.atualizar_combos_vinculo_entidades()
        if aba_atual == 0: self.renderizar_dashboard_executivo()
        elif aba_atual == 2: self.atualizar_tabela_estoque_visual()
        elif aba_atual == 3: self.atualizar_tabela_pagar()  
        elif aba_atual == 4: self.atualizar_tabela_receber() 
        elif aba_atual == 5: self.renderizar_inadimplencia()

    def criar_barra_botoes_atalho(self):
        frame_atalhos = tk.LabelFrame(self.container_main, text=" Painel Integrado de Atalhos (Acesso Rápido) ", font=("Arial", 10, "bold"), fg="#2b6cb0", bg="white", padx=10, pady=8)
        frame_atalhos.pack(fill="x", padx=15, pady=(5, 15), side="bottom")
        
        botoes_config = [
            ("📊 Dashboard", 0),
            ("👥 Entidades", 1),
            ("📦 Estoque Geral", 2),
            ("💸 Contas a Pagar", 3),
            ("💰 Contas a Receber", 4),
            ("⚠️ Inadimplências", 5)
        ]
        
        for idx, (texto, aba_id) in enumerate(botoes_config):
            btn = tk.Button(frame_atalhos, text=texto, font=("Arial", 10, "bold"), fg="#1a365d", bg="#e2e8f0", activebackground="#cbd5e0", relief="groove", bd=2, cursor="hand2", padx=10, pady=4,
                            command=lambda a_id=aba_id: self.notebook.select(a_id))
            btn.grid(row=0, column=idx, padx=10, pady=2, sticky="nsew")
            frame_atalhos.grid_columnconfigure(idx, weight=1)

    # =========================================================================
    # SEÇÃO DE CADASTRO DE ENTIDADES (REPARADA)
    # =========================================================================
    def criar_layout_entidades(self):
        frame_form = tk.LabelFrame(self.aba_entidades, text=" Cadastrar Cliente ou Fornecedor ", font=("Arial", 11, "bold"), fg="#1a365d", bg="white", padx=15, pady=15)
        frame_form.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_form, text="Tipo:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_tipo_entidade = ttk.Combobox(frame_form, values=["Cliente", "Fornecedor"], width=15, state="readonly")
        self.combo_tipo_entidade.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.combo_tipo_entidade.set("Cliente")
        
        tk.Label(frame_form, text="Perfil:", bg="white").grid(row=0, column=2, sticky="w", padx=15)
        self.combo_perfil_entidade = ttk.Combobox(frame_form, values=["Pessoa Jurídica", "Pessoa Física"], width=18, state="readonly")
        self.combo_perfil_entidade.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.combo_perfil_entidade.set("Pessoa Jurídica")
        self.combo_perfil_entidade.bind("<<ComboboxSelected>>", self.alternar_perfil_entidade)
        
        self.lbl_documento = tk.Label(frame_form, text="CNPJ:", bg="white")
        self.lbl_documento.grid(row=1, column=0, sticky="w", pady=5)
        self.entry_documento = ttk.Entry(frame_form, width=22)
        self.entry_documento.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        self.btn_buscar_cnpj = ttk.Button(frame_form, text="Buscar Dados", command=self.disparar_busca_cnpj)
        self.btn_buscar_cnpj.grid(row=1, column=2, padx=15, pady=5, sticky="w")
        
        tk.Label(frame_form, text="Nome / Razão Social:", bg="white").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_nome_entidade = ttk.Entry(frame_form, width=35)
        self.entry_nome_entidade.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_form, text="Telefone:", bg="white").grid(row=2, column=3, sticky="w", padx=15)
        self.entry_tel_entidade = ttk.Entry(frame_form, width=18)
        self.entry_tel_entidade.grid(row=2, column=4, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_form, text="Cidade/UF:", bg="white").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_cidade_entidade = ttk.Entry(frame_form, width=25)
        self.entry_cidade_entidade.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Button(frame_form, text="Salvar Entidade", command=self.adicionar_entity).grid(row=4, column=0, columnspan=5, pady=10)
        
        frame_tabela = tk.LabelFrame(self.aba_entidades, text=" Entidades Cadastradas ", font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
        frame_tabela.pack(fill="both", expand=True, padx=10, pady=10)
        
        colunas = ("id", "tipo", "nome", "documento", "telefone", "localidade")
        self.tree_entidades = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
        self.tree_entidades.heading("id", text="ID")
        self.tree_entidades.heading("tipo", text="Tipo")
        self.tree_entidades.heading("nome", text="Nome / Razão Social")
        self.tree_entidades.heading("documento", text="CPF / CNPJ")
        self.tree_entidades.heading("telefone", text="Telefone")
        self.tree_entidades.heading("localidade", text="Cidade/UF")
        
        self.tree_entidades.column("id", width=50, anchor="center")
        self.tree_entidades.column("tipo", width=100, anchor="center")
        self.tree_entidades.column("nome", width=320, anchor="w")
        self.tree_entidades.column("documento", width=160, anchor="center")
        self.tree_entidades.column("telefone", width=120, anchor="center")
        self.tree_entidades.column("localidade", width=150, anchor="w")
        
        self.tree_entidades.pack(fill="both", expand=True)
        self.atualizar_tabela_entidades()

    def alternar_perfil_entidade(self, event):
        perfil = self.combo_perfil_entidade.get()
        if perfil == "Pessoa Física":
            self.lbl_documento.config(text="CPF:")
            self.btn_buscar_cnpj.config(state="disabled")
        else:
            self.lbl_documento.config(text="CNPJ:")
            self.btn_buscar_cnpj.config(state="normal")

    def disparar_busca_cnpj(self):
        cnpj = "".join(filter(str.isdigit, self.entry_documento.get().strip()))
        if len(cnpj) != 14: 
            messagebox.showwarning("Aviso", "Insira um CNPJ com 14 dígitos numéricos para buscar.")
            return
        
        self.btn_buscar_cnpj.config(state="disabled")
        # CORREÇÃO DA CHAMADA DA THREAD (Nome do método corrigido)
        threading.Thread(target=self.executar_busca_api_cnpj, args=(cnpj,), daemon=True).start()

    def executar_busca_api_cnpj(self, cnpj):
        try:
            import requests
            resposta = requests.get(f"https://receitaws.com.br/v1/cnpj/{cnpj}", timeout=5)
            
            if resposta.status_code == 200:
                dados = resposta.json()
                if dados.get("status") == "ERROR":
                    motivo = dados.get("message", "CNPJ inválido ou rejeitado.")
                    self.root.after(0, lambda: messagebox.showerror("Erro na Base", f"A SEFAZ/Receita retornou:\n{motivo}"))
                else:
                    nome_retornado = dados.get("nome", "")
                    local_retornado = f"{dados.get('municipio', '')}/{dados.get('uf', '')}"
                    tel_retornado = dados.get("telefone", "")
                    
                    self.root.after(0, lambda: self.preencher_campos_cnpj(nome_retornado, local_retornado, tel_retornado))
            elif resposta.status_code == 429:
                self.root.after(0, lambda: messagebox.showwarning("Limite Atingido", "Limite de consultas públicas atingido.\nAguarde 1 minuto antes de tentar novamente."))
            else:
                self.root.after(0, lambda: messagebox.showerror("Erro de Resposta", f"O servidor retornou o status: {resposta.status_code}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Falha de Conexão", f"Não foi possível contactar o servidor:\n{str(e)}"))
        finally:
            # Garante que o botão volte ao estado normal em qualquer cenário (sucesso ou falha)
            self.root.after(0, lambda: self.btn_buscar_cnpj.config(state="normal"))

    def preencher_campos_cnpj(self, nome, city, tel):
        self.entry_nome_entidade.delete(0, tk.END); self.entry_nome_entidade.insert(0, nome)
        self.entry_cidade_entidade.delete(0, tk.END); self.entry_cidade_entidade.insert(0, city)
        self.entry_tel_entidade.delete(0, tk.END); self.entry_tel_entidade.insert(0, tel)

    def adicionar_entity(self):
        tipo = self.combo_tipo_entidade.get()
        perfil = self.combo_perfil_entidade.get()
        nome = self.entry_nome_entidade.get().strip()
        doc = self.entry_documento.get().strip()
        tel = self.entry_tel_entidade.get().strip()
        cidade = self.entry_cidade_entidade.get().strip()
        
        if not nome:
            messagebox.showerror("Erro", "O preenchimento do Nome ou Razão Social é obrigatório.")
            return
            
        self.cursor.execute("INSERT INTO entidades (usuario_id, tipo, nome, cnpj, telefone, localidade) VALUES (?, ?, ?, ?, ?, ?)",
                            (self.usuario_logado_id, tipo, nome, doc if doc else "N/I", tel, cidade))
        self.conexao.commit()
        self.atualizar_tabela_entidades()
        self.atualizar_combos_vinculo_entidades()
        
        self.entry_documento.delete(0, tk.END); self.entry_nome_entidade.delete(0, tk.END)
        self.entry_tel_entidade.delete(0, tk.END); self.entry_cidade_entidade.delete(0, tk.END)
        messagebox.showinfo("Sucesso", f"{tipo} ({perfil}) adicionado com sucesso!")

    def atualizar_tabela_entidades(self):
        for item in self.tree_entidades.get_children(): self.tree_entidades.delete(item)
        self.cursor.execute("SELECT id, tipo, nome, cnpj, telefone, localidade FROM entidades WHERE usuario_id = ?", (self.usuario_logado_id,))
        for row in self.cursor.fetchall(): self.tree_entidades.insert("", "end", values=row)

    def atualizar_combos_vinculo_entidades(self):
        if not hasattr(self, 'usuario_logado_id'): return
        
        self.cursor.execute("SELECT nome FROM entidades WHERE usuario_id = ? AND tipo = 'Cliente'", (self.usuario_logado_id,))
        clientes = [r[0] for r in self.cursor.fetchall()]
        
        self.cursor.execute("SELECT nome FROM entidades WHERE usuario_id = ? AND tipo = 'Fornecedor'", (self.usuario_logado_id,))
        fornecedores = [r[0] for r in self.cursor.fetchall()]
        
        if hasattr(self, 'combo_fornecedor_pagar'): self.combo_fornecedor_pagar.config(values=fornecedores)
        if hasattr(self, 'combo_cliente_receber'): self.combo_cliente_receber.config(values=clientes)
        if hasattr(self, 'combo_fornecedor_produto'): self.combo_fornecedor_produto.config(values=fornecedores)

    # =========================================================================
    # CONTAS A PAGAR
    # =========================================================================
    def criar_layout_contas_pagar(self):
        sub_frame_topo = tk.Frame(self.aba_pagar)
        sub_frame_topo.pack(fill="x", padx=10, pady=5)

        frame_form = tk.LabelFrame(sub_frame_topo, text=" Novo Lançamento de Despesa ", font=("Arial", 11, "bold"), fg="#1a365d", bg="white", padx=15, pady=15)
        frame_form.pack(fill="x")
        
        tk.Label(frame_form, text="Descrição:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_descricao = ttk.Entry(frame_form, width=25)
        self.entry_descricao.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_form, text="Valor (R$):", bg="white").grid(row=0, column=2, sticky="w", padx=10)
        self.entry_valor = ttk.Entry(frame_form, width=12)
        self.entry_valor.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(frame_form, text="Vencimento:", bg="white").grid(row=0, column=4, sticky="w", padx=10)
        self.entry_data_pagar = ttk.Entry(frame_form, width=14)
        self.entry_data_pagar.grid(row=0, column=5, padx=5, pady=5)
        self.entry_data_pagar.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        tk.Label(frame_form, text="Fornecedor:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_fornecedor_pagar = ttk.Combobox(frame_form, values=[], width=22, state="readonly")
        self.combo_fornecedor_pagar.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_form, text="Forma:", bg="white").grid(row=1, column=2, sticky="w", padx=10)
        self.combo_forma_pagto = ttk.Combobox(frame_form, values=["Dinheiro", "Pix", "Boleto Fixo", "Cartão de Crédito"], width=15, state="readonly")
        self.combo_forma_pagto.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.combo_forma_pagto.set("Pix")
        self.combo_forma_pagto.bind("<<ComboboxSelected>>", self.toggle_campo_parcelas)
        
        self.lbl_parcelas = tk.Label(frame_form, text="Parcelas:", bg="white")
        self.combo_parcelas = ttk.Combobox(frame_form, values=[f"{i}x" for i in range(1, 24)], width=8, state="readonly")
        
        btn_salvar = ttk.Button(frame_form, text="Adicionar Despesa", command=self.adicionar_conta_pagar)
        btn_salvar.grid(row=2, column=0, columnspan=6, pady=12)
        
        sub_frame_baixo = tk.Frame(self.aba_pagar)
        sub_frame_baixo.pack(fill="both", expand=True, padx=10, pady=5)

        frame_tabela = tk.LabelFrame(sub_frame_baixo, text=" Painel de Exibição de Contas a Pagar ", font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
        frame_tabela.pack(fill="both", expand=True)
        
        colunas = ("id", "desc", "val", "forma", "parc", "venc")
        self.tree_pagar = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
        self.tree_pagar.heading("id", text="ID")
        self.tree_pagar.heading("desc", text="Descrição / Fornecedor")
        self.tree_pagar.heading("val", text="Valor")
        self.tree_pagar.heading("forma", text="Forma")
        self.tree_pagar.heading("parc", text="Parcelas")
        self.tree_pagar.heading("venc", text="Vencimento")
        
        self.tree_pagar.column("id", width=50, anchor="center")
        self.tree_pagar.column("desc", width=380, anchor="w")
        self.tree_pagar.column("val", width=140, anchor="center")
        self.tree_pagar.column("forma", width=140, anchor="center")
        self.tree_pagar.column("parc", width=100, anchor="center")
        self.tree_pagar.column("venc", width=140, anchor="center")
        
        self.tree_pagar.pack(fill="both", expand=True)
        self.atualizar_tabela_pagar()

    def toggle_campo_parcelas(self, event):
        if self.combo_forma_pagto.get() == "Cartão de Crédito":
            self.lbl_parcelas.grid(row=1, column=4, sticky="w", padx=10)
            self.combo_parcelas.grid(row=1, column=5, padx=5, pady=5, sticky="w")
            self.combo_parcelas.set("1x")
        else:
            self.lbl_parcelas.grid_forget(); self.combo_parcelas.grid_forget()

    def adicionar_conta_pagar(self):
        try:
            desc = self.entry_descricao.get().strip()
            forn = self.combo_fornecedor_pagar.get()
            valor = float(self.entry_valor.get().replace(",", "."))
            venc = self.entry_data_pagar.get().strip()
            forma = self.combo_forma_pagto.get()
            datetime.strptime(venc, "%d/%m/%Y")
            parcelas = self.combo_parcelas.get() if forma == "Cartão de Crédito" else "À Vista"
            
            exibicao_desc = f"{desc} [{forn}]" if forn else desc
            
            self.cursor.execute("INSERT INTO contas_pagar (usuario_id, descricao, valor, forma, parcelas, vencimento) VALUES (?, ?, ?, ?, ?, ?)",
                                (self.usuario_logado_id, exibicao_desc, valor, forma, parcelas, venc))
            self.conexao.commit()
            
            self.atualizar_tabela_pagar()
            self.entry_descricao.delete(0, tk.END); self.entry_valor.delete(0, tk.END)
            messagebox.showinfo("Sucesso", "Despesa adicionada com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", "Valide os campos de entrada.")

    def atualizar_tabela_pagar(self):
        for item in self.tree_pagar.get_children(): self.tree_pagar.delete(item)
        self.cursor.execute("SELECT id, descricao, valor, forma, parcelas, vencimento FROM contas_pagar WHERE usuario_id = ?", (self.usuario_logado_id,))
        for row in self.cursor.fetchall():
            self.tree_pagar.insert("", "end", values=(row[0], row[1], f"R$ {row[2]:,.2f}", row[3], row[4], row[5]))

    # =========================================================================
    # CONTAS A RECEBER
    # =========================================================================
    def criar_layout_contas_receber(self):
        sub_frame_topo = tk.Frame(self.aba_receber)
        sub_frame_topo.pack(fill="x", padx=10, pady=5)

        frame_form_receber = tk.LabelFrame(sub_frame_topo, text=" Novo Lançamento de Receita ", font=("Arial", 11, "bold"), fg="#1a365d", bg="white", padx=15, pady=15)
        frame_form_receber.pack(fill="x")
        
        tk.Label(frame_form_receber, text="Descrição Serviço:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_desc_receber = ttk.Entry(frame_form_receber, width=30)
        self.entry_desc_receber.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_form_receber, text="Valor (R$):", bg="white").grid(row=0, column=2, sticky="w", padx=10)
        self.entry_val_receber = ttk.Entry(frame_form_receber, width=15)
        self.entry_val_receber.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(frame_form_receber, text="Cliente Vinculado:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_cliente_receber = ttk.Combobox(frame_form_receber, values=[], width=27, state="readonly")
        self.combo_cliente_receber.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_form_receber, text="Data Vencimento:", bg="white").grid(row=1, column=2, sticky="w", padx=10)
        self.entry_data_receber = ttk.Entry(frame_form_receber, width=16)
        self.entry_data_receber.grid(row=1, column=3, padx=5, pady=5)
        self.entry_data_receber.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        ttk.Button(frame_form_receber, text="Adicionar Receita", command=self.adicionar_conta_receber).grid(row=2, column=0, columnspan=4, pady=12)
        
        sub_frame_baixo = tk.Frame(self.aba_receber)
        sub_frame_baixo.pack(fill="both", expand=True, padx=10, pady=5)

        frame_tabela_receber = tk.LabelFrame(sub_frame_baixo, text=" Painel de Exibição de Contas a Receber ", font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
        frame_tabela_receber.pack(fill="both", expand=True)
        
        colunas = ("id", "desc", "val", "venc")
        self.tree_receber = ttk.Treeview(frame_tabela_receber, columns=colunas, show="headings")
        self.tree_receber.heading("id", text="ID")
        self.tree_receber.heading("desc", text="Descrição / Cliente Vinculado")
        self.tree_receber.heading("val", text="Valor")
        self.tree_receber.heading("venc", text="Vencimento")
        
        self.tree_receber.column("id", width=50, anchor="center")
        self.tree_receber.column("desc", width=450, anchor="w")
        self.tree_receber.column("val", width=150, anchor="center")
        self.tree_receber.column("venc", width=150, anchor="center")
        
        self.tree_receber.pack(fill="both", expand=True)
        self.atualizar_tabela_receber()

    def adicionar_conta_receber(self):
        try:
            desc = self.entry_desc_receber.get().strip()
            cli = self.combo_cliente_receber.get()
            valor = float(self.entry_val_receber.get().replace(",", "."))
            venc = self.entry_data_receber.get().strip()
            datetime.strptime(venc, "%d/%m/%Y")
            
            exibicao_nome = f"{desc} [{cli}]" if cli else desc
            
            self.cursor.execute("INSERT INTO contas_receber (usuario_id, descricao, valor, vencimento) VALUES (?, ?, ?, ?)",
                                (self.usuario_logado_id, exibicao_nome, valor, venc))
            self.conexao.commit()
            self.atualizar_tabela_receber()
            self.entry_desc_receber.delete(0, tk.END); self.entry_val_receber.delete(0, tk.END)
            messagebox.showinfo("Sucesso", "Receita inserida com sucesso.")
        except: messagebox.showerror("Erro", "Valide as informações inseridas.")

    def atualizar_tabela_receber(self):
        for item in self.tree_receber.get_children(): self.tree_receber.delete(item)
        self.cursor.execute("SELECT id, descricao, valor, vencimento FROM contas_receber WHERE usuario_id = ?", (self.usuario_logado_id,))
        for row in self.cursor.fetchall():
            self.tree_receber.insert("", "end", values=(row[0], row[1], f"R$ {row[2]:,.2f}", row[3]))

    # =========================================================================
    # GESTÃO DE ESTOQUE
    # =========================================================================
    def criar_layout_estoque(self):
        frame_form = tk.LabelFrame(self.aba_estoque, text=" Cadastrar Novo Produto no Estoque ", font=("Arial", 11, "bold"), fg="#1a365d", bg="white", padx=15, pady=15)
        frame_form.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_form, text="Descrição Produto:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_desc_produto = ttk.Entry(frame_form, width=30)
        self.entry_desc_produto.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_form, text="Part Number:", bg="white").grid(row=0, column=2, sticky="w", padx=15)
        self.entry_part_number = ttk.Entry(frame_form, width=20)
        self.entry_part_number.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_form, text="Fornecedor Vinculado:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_fornecedor_produto = ttk.Combobox(frame_form, values=[], width=27, state="readonly")
        self.combo_fornecedor_produto.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_form, text="Qtd. Inicial:", bg="white").grid(row=1, column=2, sticky="w", padx=15)
        self.entry_qtd_inicial = ttk.Entry(frame_form, width=10)
        self.entry_qtd_inicial.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.entry_qtd_inicial.insert(0, "0")
        
        btn_salvar_prod = ttk.Button(frame_form, text="Salvar Produto", command=self.adicionar_produto_estoque)
        btn_salvar_prod.grid(row=2, column=0, columnspan=4, pady=12)
        
        frame_tabela = tk.LabelFrame(self.aba_estoque, text=" Painel do Estoque Atual e Movimentação ", font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
        frame_tabela.pack(fill="both", expand=True, padx=10, pady=10)
        
        colunas = ("id", "desc", "pn", "forn", "qtd")
        self.tree_estoque = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
        self.tree_estoque.heading("id", text="ID"); self.tree_estoque.heading("desc", text="Descrição / Item"); self.tree_estoque.heading("pn", text="Part Number"); self.tree_estoque.heading("forn", text="Fornecedor"); self.tree_estoque.heading("qtd", text="Quantidade em Estoque")
        
        self.tree_estoque.column("id", width=50, anchor="center")
        self.tree_estoque.column("desc", width=350, anchor="w")
        self.tree_estoque.column("pn", width=150, anchor="center")
        self.tree_estoque.column("forn", width=200, anchor="w")
        self.tree_estoque.column("qtd", width=120, anchor="center")
        self.tree_estoque.pack(fill="both", expand=True, side="top")
        
        frame_botoes_estoque = ttk.Frame(frame_tabela)
        frame_botoes_estoque.pack(pady=10, fill="x")
        
        ttk.Button(frame_botoes_estoque, text="➕ Dar Entrada no Estoque", command=lambda: self.alterar_quantidade_estoque("entrada")).pack(side="left", padx=20, expand=True)
        ttk.Button(frame_botoes_estoque, text="➖ Dar Saída no Estoque", command=lambda: self.alterar_quantidade_estoque("saida")).pack(side="right", padx=20, expand=True)
        
        self.atualizar_tabela_estoque_visual()

    def adicionar_produto_estoque(self):
        desc = self.entry_desc_produto.get().strip()
        pn = self.entry_part_number.get().strip()
        forn = self.combo_fornecedor_produto.get()
        qtd_str = self.entry_qtd_inicial.get().strip()
        
        if not desc or not pn or not forn:
            messagebox.showerror("Erro", "Preencha todos os dados obrigatórios, incluindo o Fornecedor.")
            return
        try:
            qtd = int(qtd_str)
            if qtd < 0: raise ValueError
        except:
            messagebox.showerror("Erro", "Quantidade inicial inválida.")
            return
            
        self.cursor.execute("INSERT INTO estoque (usuario_id, descricao, part_number, fornecedor, quantidade) VALUES (?, ?, ?, ?, ?)",
                            (self.usuario_logado_id, desc, pn, forn, qtd))
        self.conexao.commit()
        self.atualizar_tabela_estoque_visual()
        self.entry_desc_produto.delete(0, tk.END); self.entry_part_number.delete(0, tk.END)
        self.combo_fornecedor_produto.set("")

    def atualizar_tabela_estoque_visual(self):
        for item in self.tree_estoque.get_children(): self.tree_estoque.delete(item)
        self.cursor.execute("SELECT id, descricao, part_number, fornecedor, quantidade FROM estoque WHERE usuario_id = ?", (self.usuario_logado_id,))
        for row in self.cursor.fetchall(): self.tree_estoque.insert("", "end", values=row)

    def alterar_quantidade_estoque(self, operacao):
        selecionado = self.tree_estoque.selection()
        if not selecionado: return
        valores = self.tree_estoque.item(selecionado, "values")
        id_prod, desc_prod, _, _, qtd_atual = valores[0], valores[1], valores[2], valores[3], int(valores[4])
        
        qtd_movimento = simpledialog.askinteger("Movimentação", f"Quantidade para '{desc_prod}':", minvalue=1)
        if qtd_movimento:
            nova_qtd = qtd_atual + qtd_movimento if operacao == "entrada" else qtd_atual - qtd_movimento
            if nova_qtd < 0:
                messagebox.showerror("Erro", "Saldo de estoque insuficiente.")
                return
            self.cursor.execute("UPDATE estoque SET quantidade = ? WHERE id = ? AND usuario_id = ?", (nova_qtd, id_prod, self.usuario_logado_id))
            self.conexao.commit()
            self.atualizar_tabela_estoque_visual()

    # =========================================================================
    # VISUALIZAÇÃO DE DASHBOARDS E RELATÓRIOS
    # =========================================================================
    def renderizar_dashboard_executivo(self):
        for widget in self.aba_dashboard.winfo_children(): widget.destroy()
        
        self.cursor.execute("SELECT SUM(valor) FROM contas_receber WHERE usuario_id = ?", (self.usuario_logado_id,))
        faturamento = self.cursor.fetchone()[0] or 0.0
        self.cursor.execute("SELECT SUM(valor) FROM contas_pagar WHERE usuario_id = ?", (self.usuario_logado_id,))
        total_despesas = self.cursor.fetchone()[0] or 0.0
        lucro_liquido = faturamento - total_despesas
        
        frame_cards = ttk.Frame(self.aba_dashboard); frame_cards.pack(fill="x", padx=10, pady=5)
        kpis = [
            ("Faturamento Consolidado", f"R$ {faturamento:,.2f}", "#2f855a"),
            ("Resultado Líquido", f"R$ {lucro_liquido:,.2f}", "#2b6cb0" if lucro_liquido >= 0 else "#c53030"),
            ("Total de Despesas", f"R$ {total_despesas:,.2f}", "#c53030")
        ]
        for i, (titulo, valor, cor) in enumerate(kpis):
            card = tk.Frame(frame_cards, bg="white", highlightbackground="#e2e8f0", highlightthickness=1, padx=12, pady=12)
            card.grid(row=0, column=i, padx=8, pady=6, sticky="nsew")
            tk.Label(card, text=titulo, font=("Arial", 9, "bold"), fg="#718096", bg="white").pack(anchor="w")
            tk.Label(card, text=valor, font=("Arial", 15, "bold"), fg=cor, bg="white", pady=3).pack(anchor="w")
            frame_cards.grid_columnconfigure(i, weight=1)

        frame_graficos = ttk.Frame(self.aba_dashboard); frame_graficos.pack(fill="both", expand=True, padx=10, pady=5)
        fig, ax1 = plt.subplots(figsize=(10, 3))
        fig.patch.set_facecolor('#f4f6f9')
        ax1.bar(['Faturamento', 'Despesas'], [faturamento, total_despesas], color=['#2f855a', '#c53030'], width=0.4)
        ax1.set_title("Balanço Geral", fontsize=9, fontweight='bold')
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame_graficos)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    def renderizar_inadimplencia(self):
        for widget in self.aba_inadimplencia.winfo_children(): widget.destroy()
        frame_lista = tk.LabelFrame(self.aba_inadimplencia, text=" Clientes com Títulos em Atraso ", font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree_inad = ttk.Treeview(frame_lista, columns=("id", "cliente", "valor", "vencimento"), show="headings")
        self.tree_inad.heading("id", text="ID"); self.tree_inad.heading("cliente", text="Cliente"); self.tree_inad.heading("valor", text="Valor"); self.tree_inad.heading("vencimento", text="Vencimento")
        self.tree_inad.pack(side="left", fill="both", expand=True)
        
        self.cursor.execute("SELECT id, descricao, valor, vencimento FROM contas_receber WHERE usuario_id = ?", (self.usuario_logado_id,))
        for r in self.cursor.fetchall():
            try:
                if datetime.strptime(r[3], "%d/%m/%Y") < datetime.now():
                    self.tree_inad.insert("", "end", values=(r[0], r[1], f"R$ {r[2]:,.2f}", r[3]))
            except: pass
        ttk.Button(self.aba_inadimplencia, text="Disparar Cobrança via WhatsApp", command=self.disparar_cobranca_real).pack(pady=10)

    def disparar_cobranca_real(self):
        selecionado = self.tree_inad.selection()
        def renderizar_inadimplencia(self):
         for widget in self.aba_inadimplencia.winfo_children(): widget.destroy()
        frame_lista = tk.LabelFrame(self.aba_inadimplencia, text=" Clientes com Títulos em Atraso ", font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree_inad = ttk.Treeview(frame_lista, columns=("id", "cliente", "valor", "vencimento"), show="headings")
        self.tree_inad.heading("id", text="ID"); self.tree_inad.heading("cliente", text="Cliente"); self.tree_inad.heading("valor", text="Valor"); self.tree_inad.heading("vencimento", text="Vencimento")
        self.tree_inad.pack(side="left", fill="both", expand=True)
        
        self.cursor.execute("SELECT id, descricao, valor, vencimento FROM contas_receber WHERE usuario_id = ?", (self.usuario_logado_id,))
        for r in self.cursor.fetchall():
            try:
                if datetime.strptime(r[3], "%d/%m/%Y") < datetime.now():
                    self.tree_inad.insert("", "end", values=(r[0], r[1], f"R$ {r[2]:,.2f}", r[3]))
            except: pass
        ttk.Button(self.aba_inadimplencia, text="Disparar Cobrança via WhatsApp", command=self.disparar_cobranca_real).pack(pady=10)

    # COLE AQUI POR CIMA DA ANTIGA:
    def disparar_cobranca_real(self):
        selecionado = self.tree_inad.selection()
        
        if selecionado: 
            valores = self.tree_inad.item(selecionado, "values")
            _, cliente, valor_devido, data_venc = valores
            num_whatsapp = simpledialog.askstring("Contato", f"Informe o WhatsApp de '{cliente}':")
            if num_whatsapp:
                num_limpo = "".join(filter(str.isdigit, num_whatsapp))
                msg = f"Olá {cliente}, identificamos uma pendência no valor de {valor_devido} vencida em {data_venc}."
                webbrowser.open(f"https://web.whatsapp.com/send?phone=55{num_limpo}&text={msg.replace(' ', '%20')}")

# FINAL DO ARQUIVO (Sem espaços no início destas linhas abaixo):
if __name__ == "__main__":
    root = tk.Tk()
    app = AppControleFinanceiro(root)
    root.mainloop()