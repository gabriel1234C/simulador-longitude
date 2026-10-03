import pandas as pd
import plotly.express as px

def calcular_sac(valor_financiado, taxa_juros_anual, prazo_meses):
    """Calcula a Tabela SAC (Amortização Constante, Prestações Decrescentes)."""
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
    """Calcula a Tabela PRICE (Prestações Fixas, Amortização Crescente)."""
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

def criar_grafico_prestacoes(df_total):
    """Gera o gráfico Plotly comparativo das prestações."""
    fig = px.line(
        df_total, 
        x="Mês", 
        y="Prestação", 
        color="Sistema", 
        title="Comparativo do Comportamento das Prestações Mensais (SAC vs PRICE)",
        labels={"Prestação": "Valor da Prestação (R$)", "Mês": "Mês do Contrato"}
    )
    fig.update_layout(template="plotly_white", hovermode="x unified")
    return fig

def criar_grafico_saldo(df_total):
    """Gera o gráfico Plotly da evolução da redução do saldo devedor."""
    fig = px.line(
        df_total, 
        x="Mês", 
        y="Saldo Devedor", 
        color="Sistema", 
        title="Evolução da Redução do Saldo Devedor",
        labels={"Saldo Devedor": "Saldo Devedor (R$)", "Mês": "Mês do Contrato"}
    )
    fig.update_layout(template="plotly_white", hovermode="x unified")
    return fig
