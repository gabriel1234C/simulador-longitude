import streamlit as str_app
import pyrebase

def init_firebase():
    """Inicializa e retorna a autenticação do Firebase usando os segredos do Streamlit."""
    try:
        firebase_config = {
            "apiKey": str_app.secrets["firebase"]["apiKey"],
            "authDomain": str_app.secrets["firebase"]["authDomain"],
            "projectId": str_app.secrets["firebase"]["projectId"],
            "storageBucket": str_app.secrets["firebase"]["storageBucket"],
            "messagingSenderId": str_app.secrets["firebase"]["messagingSenderId"],
            "appId": str_app.secrets["firebase"]["appId"],
            "databaseURL": ""
        }
        firebase = pyrebase.initialize_app(firebase_config)
        return firebase.auth()
    except Exception as e:
        str_app.error(f"Erro ao carregar credenciais do Firebase: {e}")
        return None

def show_login_screen(auth):
    """Exibe as abas de login corporativo e recuperação de senha."""
    col1, col2, col3 = str_app.columns([1, 2, 1])
    with col2:
        str_app.markdown("<h2 style='text-align: center;'>🏢 Construtora Longitude</h2>", unsafe_allow_html=True)
        str_app.markdown("<h4 style='text-align: center;'>Simulador Comercial & Crédito</h4>", unsafe_allow_html=True)
        str_app.write("")

        tab1, tab2 = str_app.tabs(["🔑 Acesso Corporativo", "✉️ Recuperar Senha"])

        with tab1:
            email = str_app.text_input("E-mail corporativo", key="login_email")
            password = str_app.text_input("Senha", type="password", key="login_password")
            
            if str_app.button("Entrar no Sistema", use_container_width=True):
                if not email or not password:
                    str_app.warning("Preencha o e-mail e a senha.")
                else:
                    try:
                        user = auth.sign_in_with_email_and_password(email, password)
                        str_app.session_state["user"] = user
                        str_app.success("Autenticado com sucesso! Entrando...")
                        str_app.rerun()
                    except Exception:
                        str_app.error("E-mail ou senha inválidos. Tente novamente.")

        with tab2:
            reset_email = str_app.text_input("E-mail cadastrado", key="reset_email")
            if str_app.button("Enviar link de redefinição", use_container_width=True):
                if not reset_email:
                    str_app.warning("Informe o seu e-mail.")
                else:
                    try:
                        auth.send_password_reset_email(reset_email)
                        str_app.success("E-mail de recuperação enviado com sucesso!")
                    except Exception:
                        str_app.error("Erro ao enviar e-mail. Verifique o endereço digitado.")
