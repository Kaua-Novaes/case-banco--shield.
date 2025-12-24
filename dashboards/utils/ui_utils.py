"""
Funções auxiliares de UI para o dashboard SHIELD.
Centraliza componentes visuais reutilizáveis.
"""

import streamlit as st

COLOR_SHIELD = "#00F0FF"  # Cyan Neon


def card_metric(label:str, value:str, delta=None, color=COLOR_SHIELD):
    """
    Cria um card de métrica estilizado para o dashboard.
    :param label: rótulo do card
    :param value: valor principal do card
    :param delta: variação percentual (ex: "+5.2%")
    :param color: cor da borda esquerda do card
    """
    delta_html = ""
    if delta:
        #defini se delta é positivo ou negativo
        delta_color = "#00FF7F" if "+" in str(delta) or float(str(delta).strip('%').replace('+','')) > 0 else "#FF4B4B"
        delta_html = f"<span class='metric-delta' style='color: {delta_color};'> {delta}</span>"
    
    html = f"""
    <div class="metric-container" style="border-left-color: {color};">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def plot_bg_transparent(fig):
    """
    Remove e personaliza os fundos do gráfico Plotly para integração com tema escuro.

    Remove os fundos padrão do papel e da área de plotagem, configurando cores 
    transparentes. Define a cor da fonte como cinza claro e ajusta as margens.
    Adiciona grade visível nos eixos X e Y com cor discreta (#30363D) para melhor
    legibilidade em tema escuro.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        Objeto de figura Plotly a ser estilizado.

    Returns
    -------
    plotly.graph_objects.Figure
        Figura Plotly com fundos transparentes e tema escuro aplicado.

    Examples
    --------
    >>> import plotly.graph_objects as go
    >>> fig = go.Figure()
    >>> fig = plot_bg_transparent(fig)
    """
    """Remove fundos do Plotly para integrar ao tema"""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#E0E0E0",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(showgrid=True, gridcolor='#30363D'),
        yaxis=dict(showgrid=True, gridcolor='#30363D'),
    )
    return fig
