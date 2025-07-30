import streamlit as st
import pandas as pd
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
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
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
st.title("💎 Robo-Advisor Premium")
st.subheader("Tu asesor de inversiones inteligente y personalizado")
st.markdown("---")

# Tabs principales
tab1, tab2, tab3 = st.tabs(["📊 Análisis de Perfil", "📈 Simulación Histórica", "📚 Información de ETFs"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 📋 Cuestionario de Perfil de Riesgo")
        
        with st.form("questionnaire"):
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
            
            # Mostrar resultado
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
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Tabla de composición
            st.markdown("### 📊 Composición del Portafolio")
            pf_data = []
            for ticker, weight in portfolio.items():
                info = ETF_INFO[ticker]
                pf_data.append({
                    'ETF': ticker,
                    'Peso %': f"{weight*100:.0f}%",
                    'Tipo': info['tipo']
                })
            
            df_portfolio = pd.DataFrame(pf_data)
            st.table(df_portfolio)
        
        with col2:
            st.markdown("### 📋 Detalle de ETFs")
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
                        "$10,000"
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
                        f"{total_return:.1f}%"
                    )
                
                with col4:
                    st.metric(
                        "Retorno Anualizado",
                        f"{annual_return*100:.1f}%"
                    )
                
                # Mostrar gráfico con Streamlit nativo
                st.line_chart(portfolio_value)
                
                # Análisis adicional
                st.markdown("### 📊 Análisis de Rendimiento")
                
                # Calcular estadísticas
                daily_returns = portfolio_value.pct_change().dropna()
                volatility = daily_returns.std() * np.sqrt(252) * 100
                sharpe = (annual_return * 100 - 2) / volatility
                max_drawdown = ((portfolio_value / portfolio_value.cummax() - 1) * 100).min()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Volatilidad Anual", f"{volatility:.1f}%")
                
                with col2:
                    st.metric("Ratio Sharpe", f"{sharpe:.2f}")
                
                with col3:
                    st.metric("Máxima Caída", f"{max_drawdown:.1f}%")
                
                # Tabla de rendimientos anuales
                yearly_returns = portfolio_value.resample('Y').last().pct_change().dropna() * 100
                yearly_df = pd.DataFrame({
                    'Año': yearly_returns.index.year,
                    'Rendimiento %': yearly_returns.values.round(2)
                })
                
                st.markdown("### 📅 Rendimientos Anuales")
                st.dataframe(yearly_df, use_container_width=True)
                
    else:
        st.info("👆 Primero completa el cuestionario en la pestaña 'Análisis de Perfil'")

with tab3:
    st.markdown("## 📚 Información Detallada de los ETFs")
    
    for ticker, info in ETF_INFO.items():
        with st.expander(f"{info['nombre']} ({ticker})"):
            st.markdown(f"**Descripción:** {info['descripcion']}")
            st.markdown(f"**Tipo de activo:** {info['tipo']}")
            st.markdown(f"**Nivel de riesgo:** {info['riesgo']}")
            st.markdown(f"**Rendimiento esperado:** {info['rendimiento_esperado']}")
            
            # Información adicional específica
            if ticker == "AGG":
                st.markdown(f"**Duración:** {info['duración']}")
                st.markdown(f"**Yield:** {info['yield']}")
            elif ticker == "ACWI":
                st.markdown(f"**Cobertura:** {info['países']}, {info['empresas']}")
            elif ticker == "VNQ":
                st.markdown(f"**Dividend Yield:** {info['dividend_yield']}")
            elif ticker == "GLD":
                st.markdown(f"**Correlación:** {info['correlación']}")

# Footer
st.markdown("---")
st.info("""
**⚠️ Disclaimer Importante**  
Esta herramienta tiene fines **educativos e informativos**. No constituye asesoramiento financiero personalizado.
Los rendimientos pasados no garantizan resultados futuros. Consulta con un asesor financiero profesional antes de tomar decisiones de inversión.
""")
