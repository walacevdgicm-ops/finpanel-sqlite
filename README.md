# 💰 FinPanel SQLite — Gestão Financeira com Banco de Dados

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-informational)

Aplicativo desktop de **controle financeiro para pequenas empresas**, com contas a pagar e a receber, estoque, cadastro de clientes e fornecedores, inadimplência e **cobrança automática via WhatsApp**, tudo salvo em **SQLite** com login por usuário.

## ✨ Funcionalidades

- 🔐 **Cadastro e login de usuários** com senha protegida por hash **PBKDF2-SHA256**
- 👥 Clientes e fornecedores com **preenchimento automático por CNPJ**
- 💸 **Contas a pagar** (com parcelamento) e **contas a receber**
- 📦 **Estoque** com entrada e saída de produtos
- 📊 **Dashboard** com gráfico de faturamento x despesas (Matplotlib)
- ⏰ **Inadimplência**: lista títulos vencidos automaticamente
- 📲 **Cobrança no WhatsApp** com mensagem pronta para o cliente
- 🗂️ Cada usuário enxerga apenas os próprios dados

## 🚀 Como executar

```bash
pip install -r requirements.txt
python finpanel_sqlite.py
```

Na primeira tela, clique em **"Quero me cadastrar"** para criar seu usuário. O banco `sistema_gestao.db` é criado sozinho.

## 🧭 Evolução do projeto

`FinPanel` → **`FinPanel SQLite`** → [`Nexus ERP v1`](https://github.com/walacevdgicm-ops/nexus-erp-v1) → [`Nexus ERP`](https://github.com/walacevdgicm-ops/nexus-erp)

## 👨‍💻 Autor

**Walace Soares Vidigal Junior** · [GitHub](https://github.com/walacevdgicm-ops)

Licença [MIT](LICENSE)
