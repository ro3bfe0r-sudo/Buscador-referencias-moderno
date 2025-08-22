import streamlit as st
import pandas as pd

# -----------------------------
# Configuración de la página
# -----------------------------
st.set_page_config(
    page_title="Buscador de Referencias OMRON",
    page_icon="🔎",
    layout="wide"
)

# -----------------------------
# Estilo CSS moderno
# -----------------------------
OMRON_BLUE = "#005EB8"
st.markdown(f"""
<style>
body {{
    background-color: #f4f7fa;
}}
.card {{
    border: 1px solid #ddd;
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
    background-color: #ffffff;
    text-align: center;
    transition: all 0.3s ease-in-out;
}}
.card:hover {{
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    transform: translateY(-5px);
}}
.card img {{
    border-radius: 10px;
    margin-bottom: 10px;
    max-width: 100%;
    height: auto;
}}
h2, h4 {{
    color: {OMRON_BLUE};
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Logo OMRON
# -----------------------------
st.markdown(
    """
    <div style="display:flex; justify-content:center; margin-bottom:25px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/OMRON_Logo.svg" width="200">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(f"<h2 style='text-align: center;'>Buscador de Referencias OMRON</h2>", unsafe_allow_html=True)

# -----------------------------
# Cargar Excel
# -----------------------------
@st.cache_data
def load_data():
    file_path = "BBDD REFERENCIAS 2025 AGOSTO.xlsx"
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()  # limpiar espacios
    return df

df = load_data()

# -----------------------------
# Panel lateral: filtros y búsqueda
# -----------------------------
with st.sidebar:
    st.header("Filtros de búsqueda")
    search_term = st.text_input("🔎 Buscar referencia o descripción")
    
    stocking_filter = st.multiselect(
        "Stocking Type",
        options=sorted(df["Stocking Type"].dropna().unique())
    )
    
    order_by = st.selectbox(
        "Ordenar por",
        ["Relevancia", "List Price Ascendente", "List Price Descendente", "Alfabético A-Z", "Alfabético Z-A"]
    )

# -----------------------------
# Filtrado de datos
# -----------------------------
results = df.copy()

if search_term:
    results = results[
        results.apply(
            lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(),
            axis=1
        )
    ]

if stocking_filter:
    results = results[results["Stocking Type"].isin(stocking_filter)]

# Ordenar según selección
if order_by == "List Price Ascendente":
    results["List Price ES"] = pd.to_numeric(results["List Price ES"], errors='coerce')
    results = results.sort_values("List Price ES")
elif order_by == "List Price Descendente":
    results["List Price ES"] = pd.to_numeric(results["List Price ES"], errors='coerce')
    results = results.sort_values("List Price ES", ascending=False)
elif order_by == "Alfabético A-Z":
    results = results.sort_values("Catalog Description")
elif order_by == "Alfabético Z-A":
    results = results.sort_values("Catalog Description", ascending=False)

# -----------------------------
# Limitar resultados para velocidad
# -----------------------------
MAX_ROWS = 100
display_results = results.head(MAX_ROWS)

# -----------------------------
# Mostrar tarjetas expandibles
# -----------------------------
if not display_results.empty:
    st.markdown(f"<h4>Resultados encontrados: {len(results)}</h4>", unsafe_allow_html=True)
    
    for idx, row in display_results.iterrows():
        with st.expander(f"{row['OEE Second Item Number']} - {row['Catalog Description']}", expanded=False):
            image_url = row.get("<Primary Image.|Node|.Deep Link - 160px>", None)
            price = row.get("List Price ES", None)
            price_display = f"€ {float(price):,.2f}" if pd.notna(price) else "N/A"
            
            st.markdown(
                f"""
                <div class="card">
                    {'<img src="'+image_url+'">' if image_url and pd.notna(image_url) else ''}
                    <h4>{row['OEE Second Item Number']}</h4>
                    <p>{row['Catalog Description']}</p>
                    <p><b>List Price:</b> {price_display}</p>
                    <p><b>Stocking Type:</b> {row.get('Stocking Type','N/A')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
else:
    st.info("⚠️ No se encontraron coincidencias. Ajusta los filtros o el término de búsqueda.")

# -----------------------------
# Footer elegante con autoría
# -----------------------------
st.markdown("---")
st.markdown(
    f"""
    <p style='text-align:center; color:gray; font-size:0.9em;'>
    Hecho con ❤️ por <b>R. Fernandez | Sales Support</b> | Rápido, fácil y profesional
    </p>
    """,
    unsafe_allow_html=True
)
