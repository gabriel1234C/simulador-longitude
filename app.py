import streamlit as st

st.set_page_config(
    page_title="Simulador | Construtora Longitude", page_icon="🏢"
)

st.title("🏢 Construtora Longitude")
st.subheader("Simulador de Financiamento Imobiliário")

valor_imovel = st.number_input(
    "Valor do Imóvel (R$)", min_value=50000.0, value=350000.0, step=10000.0
)
entrada = st.number_input(
    "Valor da Entrada (R$)", min_value=0.0, value=70000.0, step=5000.0
)
prazo_anos = st.slider(
    "Prazo de Financiamento (Anos)", min_value=1, max_value=35, value=30
)
taxa_juros_anual = st.number_input(
    "Taxa de Juros Anual (%)", min_value=1.0, value=9.5, step=0.1
)

valor_financiado = valor_imovel - entrada
meses = prazo_anos * 12
taxa_mensal = (1 + taxa_juros_anual / 100) ** (1 / 12) - 1

if entrada >= valor_imovel:
  st.error(
      "⚠️ O valor da entrada não pode ser maior ou igual ao valor do"
      " imóvel."
  )
else:
  prestacao = (
      valor_financiado
      * (taxa_mensal * (1 + taxa_mensal) ** meses)
      / ((1 + taxa_mensal) ** meses - 1)
  )
  st.success(
      f"### Estimativa da Parcela Mensal (Price): R$ {prestacao:,.2f}"
  )
