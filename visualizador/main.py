# app.py (Main Entry Point)
import threading
import time
import pandas as pd
import streamlit as st
import requests
import plotly.express as px
import folium
from streamlit_folium import st_folium
from flask import Flask, request, jsonify
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Examen 2 IoT", layout="wide")
st.title("🌡️ Examen 2: Internet de las Cosas: TEMA - End Devices")
app = Flask(__name__)
data_lock = threading.Lock()
data_path = "data.xlsx"

# Initialize data
initial_data = pd.read_excel("./datainicial.xlsx")
#initial_data.to_excel(data_path, index=False)

@app.route("/data", methods=["POST"])
def update_data():
    global data_path
    try:
        new_data = request.get_json()
        print(new_data["CODIGO"])
        print(new_data["LONGITUD"])
        print(new_data["LATITUD"])
        print(new_data["TEMPERATURA"])
        dfcambiar = pd.read_excel(data_path)
        dfcambiar.loc[dfcambiar["CODIGO"] == int(new_data["CODIGO"]), ["LATITUD", "LONGITUD", "TEMPERATURA"]] = [new_data["LATITUD"], new_data["LONGITUD"], new_data["TEMPERATURA"]]
        #dfcambiar.loc[dfcambiar["CODIGO"] == 1025, ["LATITUD", "LONGITUD", "TEMPERATURA"]] = [6.243157, -75.59148, 10.2]
        dfcambiar.to_excel(data_path, index=False)
        print(dfcambiar)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def run_flask():
    app.run(host='0.0.0.0',port=80)

def run_streamlit():
    # ✅ Refrescar automáticamente cada 5 segundos
    st_autorefresh(interval=5000, key="autorefresh")
    tabs = st.tabs(["Inicio", "Mapa", "Gráficas y Tabla"])
    

    # Tab 1: Inicio
    with tabs[0]:
        st.header("Bienvenido a su Examen de Internet de las Cosas")
        st.write("Vaya a la pagina del TEAMS para descargar los archivos de apoyo que son:")
        st.write("1. Código Base para el Proyecto")
        st.write("2. Enunciado del examen")
        st.write("3. Código fuente del servidor")
        st.write("Las condiciones del proyecto son:")
        st.write("1. Nota 5.0 (100%): Elabora un bundling con un END DEVICE usando WiFi mediante una conexión http al servidor de forma correcta")
        st.write("2. Respeta el formato JSON del paquete así: {\"CODIGO\":\"1015\",\"TEMPERATURA\":19.7,\"LONGITUD\":-75.59048,\"LATITUD\":6.244157}")
        st.write("Bonificación de 1 unidad para el examen anterior: (Si hace las dos suma dos unidades, ninguna no hay, solo una una unidad)")
        st.write("Opcipon 1. Si hace la opcion de efectuar la comunicación con LoRA")
        st.write("Opcion 2. Si desarrolla cifrado de la comunicación: (ud debe modificar el codigo fuente del software)")
    # Tab 2: Mapa
    with tabs[1]:
        df = pd.read_excel(data_path)
        m = folium.Map(location=[df["LATITUD"].mean(), df["LONGITUD"].mean()], zoom_start=17)
        for _, row in df.iterrows():
            tooltip = f"Codigo: {row['CODIGO']}<br>Nombre: {row['NOMBRE']}<br>Temp: {row['TEMPERATURA']}°C"
            folium.Marker(
                location=[row["LATITUD"], row["LONGITUD"]],
                tooltip=tooltip,
                icon=folium.Icon(color=row['COLOR'].lower())
            ).add_to(m)
        st_folium(m, width=1200, height=500)

    # Tab 3: Gráfica y Tabla
    with tabs[2]:
        df = pd.read_excel(data_path)
        fig = px.bar(df, x="CODIGO", y="TEMPERATURA", color="COLOR", title="Temperatura por Código")
        st.plotly_chart(fig)
        st.dataframe(df, height=1000, use_container_width=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_streamlit()
