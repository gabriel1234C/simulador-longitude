import streamlit as str_app
from google import genai
import pandas as pd
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
str_app.set_page_config(
    page_title="Simulador - Construtora Longitude",
    page_icon="🏢",
    layout="wide"
)

# --- CONFIGURAÇÃO DO GEMINI AI ---
gemini_key = str_app.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in str_app.secrets else None
client = genai.Client(api_key=gemini_key) if gemini_key else None

# Inicializa o estado de sessão
if "user" not in str_app.session_state:
    str_app.session_state["user"] = None

# --- FUNÇÕES DE AUTENTICAÇÃO VIA FIREBASE REST API ---
def firebase_login(email, password):
    try:
        api_key = str_app.secrets["firebase"]["apiKey"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(url, json=payload)
        data = response.json()
        if "idToken" in data:
            return data
        else:
            return None
    except Exception:
        return None

def firebase_signup(email, password):
    try:
        api_key = str_app.secrets["firebase"]["apiKey"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(url, json=payload)
        data = response.json()
        if "idToken" in data:
            return True, "Conta criada com sucesso!"
        else:
            message = data.get("error", {}).get("message", "Erro desconhecido")
            return False, message
    except Exception as e:
        return False, str(e)

def firebase_reset_password(email):
    try:
        api_key = str_app.secrets["firebase"]["apiKey"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        payload = {"requestType": "PASSWORD_RESET", "email": email}
        response = requests.post(url, json=payload)
        data = response.json()
        if "email" in data:
            return True
        else:
            return False
    except Exception:
        return False

# --- FUNÇÕES DE MATEMÁTICA FINANCEIRA ---
def calcular_sac(valor_financiado, taxa_juros_anual, prazo_meses):
    taxa_mensal = (taxa_juros_anual / 100) / 12
    amortizacao = valor_financiado / prazo_meses
    saldo_devedor = valor_financiado
    cronograma = []
    
    for mes in range(1, prazo_meses + 1):
        juros = saldo_devedor * taxa_mensal
        prestacao = amortizacao + juros
        saldo_devedor -= amortizacao
        cronograma.append({
            "Mês": mes,
            "Prestação": prestacao,
            "Amortização": amortizacao,
            "Juros": juros,
            "Saldo Devedor": max(0, saldo_devedor),
            "Sistema": "SAC"
        })
    return cronograma

def calcular_price(valor_financiado, taxa_juros_anual, prazo_meses):
    taxa_mensal = (taxa_juros_anual / 100) / 12
    if taxa_mensal == 0:
        prestacao_fixa = valor_financiado / prazo_meses
    else:
        prestacao_fixa = valor_financiado * (taxa_mensal * (1 + taxa_mensal)**prazo_meses) / ((1 + taxa_mensal)**prazo_meses - 1)
    
    saldo_devedor = valor_financiado
    cronograma = []
    
    for mes in range(1, prazo_meses + 1):
        juros = saldo_devedor * taxa_mensal
        amortizacao = prestacao_fixa - juros
        saldo_devedor -= amortizacao
        cronograma.append({
            "Mês": mes,
            "Prestação": prestacao_fixa,
            "Amortização": amortizacao,
            "Juros": juros,
            "Saldo Devedor": max(0, saldo_devedor),
            "Sistema": "PRICE"
        })
    return cronograma

# --- TELA DE AUTENTICAÇÃO ---
def show_login_screen():
    col1, col2, col3 = str_app.columns([1, 2, 1])
    with col2:
        str_app.markdown("<h2 style='text-align: center;'>🏢 Construtora Longitude</h2>", unsafe_allow_html=True)
        str_app.markdown("<h4 style='text-align: center;'>Simulador Comercial & Crédito</h4>", unsafe_allow_html=True)
        str_app.write("")

        tab1, tab2, tab3 = str_app.tabs(["🔑 Entrar", "📝 Criar Conta", "✉️ Recuperar"])

        with tab1:
            email = str_app.text_input("E-mail corporativo", key="login_email")
            password = str_app.text_input("Senha", type="password", key="login_password")
            
            if str_app.button("Entrar no Sistema", use_container_width=True):
                if not email or not password:
                    str_app.warning("Preencha o e-mail e a senha.")
                else:
                    user_data = firebase_login(email, password)
                    if user_data:
                        str_app.session_state["user"] = user_data
                        str_app.success("Autenticado com sucesso! Entrando...")
                        str_app.rerun()
                    else:
                        str_app.error("E-mail ou senha inválidos. Tente novamente.")

        with tab2:
            novo_email = str_app.text_input("Novo e-mail", key="signup_email")
            nova_senha = str_app.text_input("Criar senha (mín. 6 caracteres)", type="password", key="signup_password")
            
            if str_app.button("Cadastrar Nova Conta", use_container_width=True):
                if not novo_email or not nova_senha:
                    str_app.warning("Preencha todos os campos.")
                else:
                    success, msg = firebase_signup(novo_email, nova_senha)
                    if success:
                        str_app.success("Conta criada com sucesso! Vá para a aba 'Entrar'.")
                    else:
                        str_app.error(f"Erro ao criar conta: {msg}")

        with tab3:
            reset_email = str_app.text_input("E-mail cadastrado", key="reset_email")
            if str_app.button("Enviar link de redefinição", use_container_width=True):
                if not reset_email:
                    str_app.warning("Informe o seu e-mail.")
                else:
                    if firebase_reset_password(reset_email):
                        str_app.success("E-mail de recuperação enviado com sucesso!")
                    else:
                        str_app.error("Erro ao enviar e-mail. Verifique o endereço.")

# --- TELA PRINCIPAL ---
def show_main_app():
    user_info = str_app.session_state["user"]
    
    str_app.sidebar.title("Painel Comercial")
    str_app.sidebar.write(f"Usuário: **{user_info.get('email', 'Corretor')}**")
    
    if str_app.sidebar.button("🚪 Sair do Sistema", use_container_width=True):
        str_app.session_state["user"] = None
        str_app.rerun()

    str_app.title("📊 Simulador de Financiamento Imobiliário")
    str_app.markdown("Ferramenta oficial de simulação de crédito e propostas da **Construtora Longitude**.")
    str_app.divider()

    col_a, col_b, col_c = str_app.columns(3)
    
    with col_a:
        valor_imovel = str_app.number_input("Valor do Imóvel (R$)", value=350000.0, step=10000.0)
        fgts = str_app.number_input("Valor do FGTS (R$)", value=30000.0, step=5000.0)
    
    with col_b:
        entrada_recursos = str_app.number_input("Entrada / Recursos Próprios (R$)", value=40000.0, step=5000.0)
        prazo_anos = str_app.number_input("Prazo do Financiamento (Anos)", value=30, min_value=1, max_value=35)
    
    with col_c:
        taxa_juros = str_app.number_input("Taxa de Juros Anual (% a.a.)", value=9.5, step=0.1)
        modo_exibicao = str_app.selectbox("Visualização de Comparativo", ["Ambos (SAC vs PRICE)", "Somente SAC", "Somente PRICE"])

    valor_financiado = max(0.0, valor_imovel - fgts - entrada_recursos)
    prazo_meses = int(prazo_anos * 12)

    str_app.write("")
    str_app.info(f"💰 **Valor Efetivo a Financiar:** R$ {valor_financiado:,.2f} ({prazo_meses} meses)")

    if str_app.button("🚀 Calcular Simulação Completa", type="primary", use_container_width=True):
        dados_sac = calcular_sac(valor_financiado, taxa_juros, prazo_meses)
        dados_price = calcular_price(valor_financiado, taxa_juros, prazo_meses)
        
        df_sac = pd.DataFrame(dados_sac)
        df_price = pd.DataFrame(dados_price)
        df_total = pd.concat([df_sac, df_price])

        c1, c2, c3, c4 = str_app.columns(4)
        c1.metric("1ª Parcela SAC", f"R$ {df_sac.iloc[0]['Prestação']:,.2f}")
        c2.metric("Última Parcela SAC", f"R$ {df_sac.iloc[-1]['Prestação']:,.2f}")
        c3.metric("Parcela Fixa PRICE", f"R$ {df_price.iloc[0]['Prestação']:,.2f}")
        c4.metric("Juros Totais (SAC vs Price)", f"R$ {df_sac['Juros'].sum():,.2f} / R$ {df_price['Juros'].sum():,.2f}")

        str_app.divider()
        str_app.subheader("📈 Gráficos Interativos de Evolução")

        str_app.line_chart(df_total, x="Mês", y="Prestação", color="Sistema")
        str_app.line_chart(df_total, x="Mês", y="Saldo Devedor", color="Sistema")

        str_app.divider()
        if modo_exibicao.startswith("Ambos"):
            tab_s1, tab_s2 = str_app.tabs(["📋 Tabela SAC", "📋 Tabela PRICE"])
            with tab_s1:
                str_app.dataframe(df_sac, use_container_width=True)
            with tab_s2:
                str_app.dataframe(df_price, use_container_width=True)
        elif modo_exibicao.startswith("Somente SAC"):
            str_app.dataframe(df_sac, use_container_width=True)
        else:
            str_app.dataframe(df_price, use_container_width=True)

        str_app.divider()
        str_app.subheader("🤖 Assistente Comercial (Gemini IA)")
        
        if client:
            if str_app.button("✨ Gerar Proposta Comercial Inteligente"):
                prompt = f"""
                Atue como um gerente comercial sênior da Construtora Longitude. 
                Gere uma mensagem comercial persuasiva para WhatsApp detalhando a simulação:
                - Imóvel: R$ {valor_imovel:,.2f}
                - Financiado: R$ {valor_financiado:,.2f}
                - Prazo: {prazo_anos} anos ({prazo_meses} meses)
                - 1ª Parcela SAC: R$ {df_sac.iloc[0]['Prestação']:,.2f}
                - Parcela PRICE: R$ {df_price.iloc[0]['Prestação']:,.2f}
                """
                try:
                    with str_app.spinner("Gerando proposta..."):
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    str_app.success("Proposta gerada com sucesso:")
                    str_app.write(response.text)
                except Exception as e:
                    str_app.error(f"Erro na IA: {e}")
        else:
            str_app.warning("Chave do Gemini não configurada.")

# --- ROTEADOR ---
if str_app.session_state["user"] is None:
    show_login_screen()
else:
    show_main_app()
