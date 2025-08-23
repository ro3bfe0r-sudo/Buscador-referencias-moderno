import streamlit as st
import pandas as pd
import os

# -----------------------------
# Configuración de la página
# -----------------------------
st.set_page_config(
    page_title="Buscador de Referencias",
    layout="wide",
    page_icon="Logo-Omron-500x283 - Copy.jpg"
)

# -----------------------------
# Autenticación básica segura
# -----------------------------
USERNAME = os.getenv("ST_USERNAME")
PASSWORD = os.getenv("ST_PASSWORD")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("### Inicia sesión")
    username_input = st.text_input("Usuario")
    password_input = st.text_input("Contraseña", type="password")
    if st.button("Acceder"):
        if username_input == USERNAME and password_input == PASSWORD:
            st.session_state.logged_in = True
            st.experimental_rerun = lambda: None
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
else:
    # -----------------------------
    # Logo y título
    # -----------------------------
    st.image("Logo-Omron-500x283 - Copy.jpg", width=250)
    st.markdown("<h2 style='text-align:center;'>Buscador de Referencias</h2>", unsafe_allow_html=True)

    # -----------------------------
    # Cargar CSV
    # -----------------------------
    @st.cache_data
    def load_data():
        df = pd.read_csv("referencias.csv", dtype=str)
        df.columns = df.columns.str.strip()
        return df

    df = load_data()

    # -----------------------------
    # Panel lateral con filtros
    # -----------------------------
    with st.sidebar:
        st.header("Filtros de búsqueda")
        search_term = st.text_input("Escribe código o descripción")
        stocking_filter = st.multiselect(
            "Filtrar por Stocking Type",
            options=sorted(df["Stocking Type"].dropna().unique())
        )

    # -----------------------------
    # Filtrado rápido insensible a mayúsculas
    # -----------------------------
    results = df.copy()
    if search_term:
        term_upper = search_term.upper()
        results = results[
            results["OEE Second Item Number"].str.upper().str.startswith(term_upper, na=False) |
            results["Catalog Description"].str.upper().str.startswith(term_upper, na=False)
        ]

    if stocking_filter:
        results = results[results["Stocking Type"].isin(stocking_filter)]

    # Mostrar total de resultados
    st.markdown(f"**Resultados encontrados: {len(results)}**")

    # -----------------------------
    # Seleccionar producto y mostrar ficha
    # -----------------------------
    if not results.empty:
        options = results["Catalog Description"].tolist()
        selected = st.selectbox("Selecciona un producto para ver ficha completa:", options)
        
        product_row = results[results["Catalog Description"] == selected].iloc[0]

        item_code = product_row.get("OEE Second Item Number", "")
        catalog = product_row.get("Catalog Description", "")
        long_desc = product_row.get("Item Long Description", "")
        price = product_row.get("List Price ES", "")
        stocking = product_row.get("Stocking Type", "")
        image_url = product_row.get("<Primary Image.|Node|.Deep Link - 160px>", "")

        # Convertir precio correctamente
        price_display = ""
        if price and pd.notna(price):
            try:
                price_clean = str(price).replace("€", "").replace(" ", "").strip()
                price_num = float(price_clean)
                price_display = f"{price_num:,.2f} €"
            except:
                price_display = f"{price}"

        st.markdown("---")
        st.write(f"**Item code:** {item_code}")
        st.write(f"**Catalog Description:** {catalog}")
        st.write(f"**Item Long Description:** {long_desc}")
        st.write(f"**List Price:** {price_display}")
        st.write(f"**Stocking Type:** {stocking}")
        if image_url and pd.notna(image_url):
            st.image(image_url, width=200)
    else:
        st.info("⚠️ No se encontraron coincidencias. Ajusta los filtros o el término de búsqueda.")

    # -----------------------------
    # Footer
    # -----------------------------
    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; color:gray; font-size:0.9em;'>Hecho con ❤️ por <b>R. Fernandez | Sales Support</b></p>",
        unsafe_allow_html=True
    )
