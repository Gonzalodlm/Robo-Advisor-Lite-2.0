import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

from scoring import score_user, bucket_to_label
from portfolios import MODEL_PORTFOLIOS
from etf_descriptions import ETF_INFO

# Configuración de la página
st.set_page_config(
    page_title="Robo-Advisor Premium", 
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para mejor diseño
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        height: 50px;
        font-size: 18px;
        font-weight: 500;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .etf-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f2937;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    h2 {
        color: #374151;
        font-size: 2rem;
        font-weight: 600;
    }
    h3 {
        color: #4b5563;
        font-size: 1.5rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Función para obtener datos históricos
@st.cache_data
def get_historical_data(tickers, start_date, end_date):
    """Obtiene datos históricos de Yahoo Finance"""
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            data[ticker] = hist['Close']
        except:
            st.warning(f"No se pudo obtener datos para {ticker}")
    return pd.DataFrame(data)

# Función para simular portafolio histórico
def simulate_portfolio(weights, initial_investment=10000):
    """Simula el rendimiento histórico de un portafolio"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*10)  # 10 años atrás
    
    # Obtener datos históricos
    tickers = list(weights.keys())
    historical_data = get_historical_data(tickers, start_date, end_date)
    
    if historical_data.empty:
        return None
    
    # Calcular retornos diarios
    returns = historical_data.pct_change().fillna(0)
    
    # Calcular retorno del portafolio
    portfolio_returns = (returns * list(weights.values())).sum(axis=1)
    
    # Calcular valor acumulado
    cumulative_returns = (1 + portfolio_returns).cumprod()
    portfolio_value = initial_investment * cumulative_returns
    
    return portfolio_value

# ---------- INTERFAZ PRINCIPAL ----------
st.markdown("# 💎 Robo-Advisor Premium")
st.markdown("### Tu asesor de inversiones inteligente y personalizado")
st.markdown("---")

# Tabs principales
tab1, tab2, tab3 = st.tabs(["📊 Análisis de Perfil", "📈 Simulación Histórica", "📚 Información de ETFs"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 📋 Cuestionario de Perfil de Riesgo")
        st.markdown("Responde estas 10 preguntas para determinar tu perfil de inversión ideal")
        
        with st.form("questionnaire"):
            # Preguntas en un diseño más compacto
            col_q1, col_q2 = st.columns(2)
            
            with col_q1:
                age = st.slider("1️⃣ ¿Cuál es tu edad?", 18, 75, 30)
                horizon = st.selectbox(
                    "2️⃣ Horizonte de inversión",
                    ("< 3 años", "3-5 años", "5-10 años", "> 10 años"),
                )
                income = st.selectbox(
                    "3️⃣ % de ingresos para invertir",
                    ("< 5 %", "5-10 %", "10-20 %", "> 20 %"),
                )
                knowledge = st.selectbox(
                    "4️⃣ Conocimiento financiero",
                    ("Principiante", "Intermedio", "Avanzado"),
                )
                max_drop = st.selectbox(
                    "5️⃣ Caída máxima tolerable",
                    ("5 %", "10 %", "20 %", "30 %", "> 30 %"),
                )
            
            with col_q2:
                reaction = st.selectbox(
                    "6️⃣ Si tu portafolio cae 15%",
                    ("Vendo todo", "Vendo una parte", "No hago nada", "Compro más"),
                )
                liquidity = st.selectbox(
                    "7️⃣ Necesidad de liquidez",
                    ("Alta", "Media", "Baja"),
                )
                goal = st.selectbox(
                    "8️⃣ Objetivo principal",
                    ("Proteger capital", "Ingresos regulares", "Crecimiento balanceado", "Máximo crecimiento"),
                )
                inflation = st.selectbox(
                    "9️⃣ Preocupación por inflación",
                    ("No me preocupa", "Me preocupa moderadamente", "Me preocupa mucho"),
                )
                digital = st.selectbox(
                    "🔟 Confianza en plataformas digitales",
                    ("Baja", "Media", "Alta"),
                )

            submitted = st.form_submit_button("🎯 Calcular mi perfil", use_container_width=True)

    with col2:
        st.markdown("## 🎯 Tu Resultado")
        
        if submitted:
            answers = dict(
                age=age, horizon=horizon, income=income, knowledge=knowledge,
                max_drop=max_drop, reaction=reaction, liquidity=liquidity,
                goal=goal, inflation=inflation, digital=digital
            )
            
            bucket, total_score = score_user(answers)
            label = bucket_to_label[bucket]
            
            # Mostrar resultado con diseño mejorado
            st.markdown(f"""
            <div class="metric-card" style="background-color: {'#e8f5e9' if bucket <= 1 else '#fff3e0' if bucket <= 3 else '#ffebee'};">
                <h2 style="margin: 0;">Perfil: {label}</h2>
                <p style="font-size: 1.2rem; margin: 10px 0;">Puntaje: {total_score}/50</p>
                <p style="margin: 0;">Nivel de riesgo: {bucket + 1}/5</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Guardar en sesión
            st.session_state['profile'] = {
                'bucket': bucket,
                'label': label,
                'portfolio': MODEL_PORTFOLIOS[bucket]
            }

    # Mostrar portafolio recomendado
    if 'profile' in st.session_state:
        st.markdown("---")
        st.markdown("## 💼 Tu Portafolio Recomendado")
        
        portfolio = st.session_state['profile']['portfolio']
        
        # Crear gráfico de dona mejorado
        fig = go.Figure(data=[go.Pie(
            labels=[ETF_INFO[ticker]['nombre'] for ticker in portfolio.keys()],
            values=list(portfolio.values()),
            hole=.3,
            marker_colors=[ETF_INFO[ticker]['color'] for ticker in portfolio.keys()],
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Composición Detallada")
            for ticker, weight in portfolio.items():
                info = ETF_INFO[ticker]
                st.markdown(f"""
                <div class="etf-card">
                    <h4 style="margin: 0; color: {info['color']};">{info['nombre']} ({ticker})</h4>
                    <p style="margin: 5px 0; font-size: 1.2rem; font-weight: bold;">{weight*100:.0f}%</p>
                    <p style="margin: 0; font-size: 0.9rem; color: #666;">{info['tipo']} - Riesgo {info['riesgo']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Descargar CSV
        pf_df = pd.DataFrame([
            {
                'ETF': ticker,
                'Nombre': ETF_INFO[ticker]['nombre'],
                'Peso %': weight * 100,
                'Tipo': ETF_INFO[ticker]['tipo'],
                'Descripción': ETF_INFO[ticker]['descripcion']
            }
            for ticker, weight in portfolio.items()
        ])
        
        csv = pf_df.to_csv(index=False).encode()
        st.download_button(
            "📥 Descargar portafolio en CSV",
            csv,
            f"portfolio_{st.session_state['profile']['label']}.csv",
            "text/csv",
            use_container_width=True
        )

with tab2:
    st.markdown("## 📈 Simulación Histórica del Portafolio")
    
    if 'profile' in st.session_state:
        portfolio = st.session_state['profile']['portfolio']
        
        with st.spinner('Calculando rendimiento histórico...'):
            portfolio_value = simulate_portfolio(portfolio)
            
            if portfolio_value is not None:
                # Calcular métricas
                final_value = portfolio_value.iloc[-1]
                total_return = (final_value / 10000 - 1) * 100
                years = len(portfolio_value) / 252  # Días de trading por año
                annual_return = (final_value / 10000) ** (1/years) - 1
                
                # Mostrar métricas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Inversión Inicial",
                        "$10,000",
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        "Valor Final",
                        f"${final_value:,.0f}",
                        delta=f"+${final_value-10000:,.0f}"
                    )
                
                with col3:
                    st.metric(
                        "Retorno Total",
                        f"{total_return:.1f}%",
                        delta=None
                    )
                
                with col4:
                    st.metric(
                        "Retorno Anualizado",
                        f"{annual_return*100:.1f}%",
                        delta=None
                    )
                
                # Gráfico de evolución
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=portfolio_value.index,
                    y=portfolio_value.values,
                    mode='lines',
                    name='Valor del Portafolio',
                    line=dict(color='#1976D2', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(25, 118, 210, 0.1)'
                ))
                
                fig.update_layout(
                    title="Evolución de $10,000 invertidos hace 10 años",
                    xaxis_title="Fecha",
                    yaxis_title="Valor del Portafolio ($)",
                    hovermode='x unified',
                    showlegend=False,
                    height=500
                )
                
                fig.update_yaxis(tickformat='$,.0f')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Análisis adicional
                st.markdown("### 📊 Análisis de Rendimiento")
                
                # Calcular rendimientos anuales
                yearly_returns = portfolio_value.resample('Y').last().pct_change().dropna() * 100
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico de barras de rendimientos anuales
                    fig_yearly = go.Figure(data=[
                        go.Bar(
                            x=yearly_returns.index.year,
                            y=yearly_returns.values,
                            marker_color=['#388E3C' if r > 0 else '#D32F2F' for r in yearly_returns.values]
                        )
                    ])
                    
                    fig_yearly.update_layout(
                        title="Rendimientos Anuales (%)",
                        xaxis_title="Año",
                        yaxis_title="Rendimiento (%)",
                        showlegend=False,
                        height=350
                    )
                    
                    st.plotly_chart(fig_yearly, use_container_width=True)
                
                with col2:
                    # Estadísticas de riesgo
                    daily_returns = portfolio_value.pct_change().dropna()
                    volatility = daily_returns.std() * np.sqrt(252) * 100
                    sharpe = (annual_return * 100 - 2) / volatility  # Asumiendo tasa libre de riesgo del 2%
                    max_drawdown = ((portfolio_value / portfolio_value.cummax() - 1) * 100).min()
                    
                    st.markdown("#### 📈 Métricas de Riesgo-Retorno")
                    st.metric("Volatilidad Anual", f"{volatility:.1f}%")
                    st.metric("Ratio Sharpe", f"{sharpe:.2f}")
                    st.metric("Máxima Caída", f"{max_drawdown:.1f}%")
                
    else:
        st.info("👆 Primero completa el cuestionario en la pestaña 'Análisis de Perfil' para ver la simulación histórica de tu portafolio personalizado.")

with tab3:
    st.markdown("## 📚 Información Detallada de los ETFs")
    st.markdown("Conoce más sobre cada componente de tu portafolio")
    
    for ticker, info in ETF_INFO.items():
        with st.expander(f"{info['nombre']} ({ticker})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Descripción:** {info['descripcion']}")
                st.markdown(f"**Tipo de activo:** {info['tipo']}")
                st.markdown(f"**Nivel de riesgo:** {info['riesgo']}")
                st.markdown(f"**Rendimiento esperado:** {info['rendimiento_esperado']}")
                
                # Información adicional específica por ETF
                if ticker == "AGG":
                    st.markdown(f"**Duración:** {info['duración']}")
                    st.markdown(f"**Yield:** {info['yield']}")
                elif ticker == "ACWI":
                    st.markdown(f"**Cobertura:** {info['países']}, {info['empresas']}")
                elif ticker == "VNQ":
                    st.markdown(f"**Dividend Yield:** {info['dividend_yield']}")
                elif ticker == "GLD":
                    st.markdown(f"**Correlación:** {info['correlación']}")
            
            with col2:
                # Crear mini gráfico de ejemplo
                fig = go.Figure(data=[go.Pie(
                    values=[1],
                    marker_colors=[info['color']],
                    hole=.7,
                    showlegend=False
                )])
                
                fig.update_layout(
                    height=150,
                    margin=dict(t=0, b=0, l=0, r=0),
                    annotations=[dict(text=ticker, x=0.5, y=0.5, font_size=20, showarrow=False)]
                )
                
                st.plotly_chart(fig, use_container_width=True)

# Footer con disclaimer
st.markdown("---")
st.info("""
**⚠️ Disclaimer Importante**  
Esta herramienta tiene fines **educativos e informativos**. No constituye asesoramiento financiero personalizado.
Los rendimientos pasados no garantizan resultados futuros. Consulta con un asesor financiero profesional antes de tomar decisiones de inversión.
Los ETFs mostrados son ejemplos y no representan recomendaciones de compra o venta.
""")

# Información adicional en el sidebar
with st.sidebar:
    st.markdown("### 💡 Cómo funciona")
    st.markdown("""
    1. **Completa el cuestionario** para determinar tu perfil de riesgo
    2. **Recibe tu portafolio** personalizado basado en ETFs diversificados
    3. **Analiza el rendimiento** histórico de tu estrategia
    4. **Aprende sobre cada ETF** y su rol en tu portafolio
    """)
    
    st.markdown("### 🎯 Perfiles de Inversión")
    st.markdown("""
    - **Conservador**: Preservación de capital
    - **Moderado**: Balance riesgo-retorno
    - **Balanceado**: Crecimiento estable
    - **Crecimiento**: Mayor retorno esperado
    - **Agresivo**: Máximo potencial de crecimiento
    """)
    
    st.markdown("### 📊 ETFs Utilizados")
    st.markdown("""
    - **BIL**: Efectivo/T-Bills (ultra seguro)
    - **AGG**: Bonos diversificados
    - **ACWI**: Acciones globales
    - **VNQ**: Bienes raíces (REITs)
    - **GLD**: Oro (cobertura)
    """)
