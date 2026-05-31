# Back-End/API/main.py
from flask import Flask, jsonify, request
from flask_cors import CORS  # Permite que el HTML se comunique con Python
import sys
import os
from werkzeug.utils import secure_filename
from datetime import datetime 

ruta_backend = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_backend)

from CLASES_BD.conexion_bd import conectar_bd

app = Flask(__name__)
CORS(app) # Habilitamos CORS para toda la API

@app.route('/')
def inicio():
    return jsonify({"mensaje": "API de NightWatch funcionando correctamente."})

@app.route('/test-db')
def probar_base_datos():
    conexion = conectar_bd()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT @@version;")
        version = cursor.fetchone()
        conexion.close()
        return jsonify({"estado": "EXITO", "version_sql": version[0]})
    else:
        return jsonify({"estado": "ERROR"})

# ==========================================
# NUEVA RUTA: SISTEMA DE LOGIN
# ==========================================
@app.route('/login', methods=['POST'])
def autenticar_usuario():
    # Recibimos los datos que envía el HTML
    datos = request.json
    usuario = datos.get('usuario')
    password = datos.get('password')

    # Para este prototipo, validamos un usuario maestro (luego se puede conectar a la BD)
    if usuario == "admin@gmail.com" and password == "seguridad":
        return jsonify({
            "estado": "EXITO", 
            "mensaje": "Credenciales correctas. Bienvenido Analista."
        })
    else:
        return jsonify({
            "estado": "ERROR", 
            "mensaje": "Usuario o contraseña incorrectos."
        }), 401


# ==========================================
# CONFIGURACIÓN PARA SUBIR ARCHIVOS
# ==========================================
# Creamos una carpeta temporal para guardar los CSV antes de mandarlos a SQL
CARPETA_SUBIDAS = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(CARPETA_SUBIDAS, exist_ok=True) # Crea la carpeta si no existe

@app.route('/upload', methods=['POST'])
def subir_archivo():
    # 1. Verificamos que el HTML realmente envió un archivo
    if 'file' not in request.files:
        return jsonify({"estado": "ERROR", "mensaje": "No se detectó ningún archivo."})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"estado": "ERROR", "mensaje": "Nombre de archivo vacío."})
        
    # 2. Verificamos que sea un CSV o Excel
    if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        # secure_filename limpia el nombre (ej. quita espacios raros)
        nombre_seguro = secure_filename(file.filename)
        ruta_guardado = os.path.join(CARPETA_SUBIDAS, nombre_seguro)
        
        # Guardamos el archivo físicamente en el Back-End
        file.save(ruta_guardado)
        
        return jsonify({
            "estado": "EXITO", 
            "mensaje": f"Archivo '{nombre_seguro}' recibido exitosamente por el motor Python."
        })
    else:
        return jsonify({"estado": "ERROR", "mensaje": "Formato inválido. Solo se admiten archivos .csv o .xlsx"})
    
    
# ==========================================
# RUTA: PROVEER ARCHIVOS DE STAGING (Capa 2)
# ==========================================


# ... (tu otro código) ...

@app.route('/staging-files', methods=['GET'])
def listar_archivos_staging():
    try:
        archivos = os.listdir(CARPETA_SUBIDAS)
        lista_resultado = []
        
        for index, nombre in enumerate(archivos):
            ruta_completa = os.path.join(CARPETA_SUBIDAS, nombre)
            
            # Obtener la fecha REAL de cuando se subió/creó el archivo
            tiempo_modificacion = os.path.getmtime(ruta_completa)
            fecha_real = datetime.fromtimestamp(tiempo_modificacion).strftime('%d/%m/%Y %H:%M')
            
            estado = "Esperando Limpieza"
            if "error" in nombre.lower():
                estado = "Con Errores (Nulos)"
                
            lista_resultado.append({
                "id": f"RAW-2026-B{index+1}",
                "nombre": nombre,
                "fecha": fecha_real, # Usamos la fecha real de tu PC
                "estado": estado
            })
            
        return jsonify({"estado": "EXITO", "archivos": lista_resultado})
    except Exception as e:
        return jsonify({"estado": "ERROR", "mensaje": str(e)})
    
import pandas as pd

# ==========================================
# CAPA 3: ETL AUTOMATIZADO (MÉTODO DE CLAVE NATURAL)
# ==========================================
@app.route('/run-etl', methods=['POST'])
def ejecutar_etl():
    try:
        archivos = [f for f in os.listdir(CARPETA_SUBIDAS) if f.endswith('.csv')]
        if not archivos:
            return jsonify({"estado": "ERROR", "mensaje": "No hay archivos CSV en Staging."})
        
        conexion = conectar_bd()
        cursor = conexion.cursor()
        registros_insertados = 0
        
        for nombre_archivo in archivos:
            archivo_procesar = os.path.join(CARPETA_SUBIDAS, nombre_archivo)
            df = pd.read_csv(archivo_procesar).dropna().drop_duplicates()
            
            for index, fila in df.iterrows():
                distrito_txt = str(fila['Distrito']).strip()
                delito_txt = str(fila['Tipo_Delito']).strip()
                fecha_str = str(fila['Fecha_Reporte']).strip()
                hora_str = str(fila['Hora_Reporte']).strip()
                rango_h = str(fila['Rango_Horario']).strip()
                uso_arma = str(fila['Uso_Arma']).upper().strip()
                captura = str(fila['Captura']).upper().strip()
                t_resp = float(fila['Tiempo_Respuesta_Min'])
                lat_val = float(fila['Latitud'])
                lon_val = float(fila['Longitud'])
                
                cat_txt = "Delitos Contra el Patrimonio"
                if "Extorsion" in delito_txt: cat_txt = "Extorsion y Chantaje"
                elif "Vandalismo" in delito_txt: cat_txt = "Delitos Contra la Seguridad Publica"

                # 1. Resolver ID_Distrito (Sub-dimensión)
                cursor.execute("SELECT ID_Distrito FROM Dim_Distrito WHERE Nombre_Distrito = ?", (distrito_txt,))
                res_d = cursor.fetchone()
                if res_d: id_distrito = res_d[0]
                else:
                    cursor.execute("INSERT INTO Dim_Distrito (Nombre_Distrito) VALUES (?)", (distrito_txt,))
                    cursor.execute("SELECT ID_Distrito FROM Dim_Distrito WHERE Nombre_Distrito = ?", (distrito_txt,))
                    id_distrito = cursor.fetchone()[0]

                # 2. Resolver ID_Categoria (Sub-dimensión)
                cursor.execute("SELECT ID_Categoria FROM Dim_Categoria_Delito WHERE Nombre_Categoria = ?", (cat_txt,))
                res_c = cursor.fetchone()
                if res_c: id_categoria = res_c[0]
                else:
                    cursor.execute("INSERT INTO Dim_Categoria_Delito (Nombre_Categoria, Severidad_Base) VALUES (?, ?)", (cat_txt, "ALTA"))
                    cursor.execute("SELECT ID_Categoria FROM Dim_Categoria_Delito WHERE Nombre_Categoria = ?", (cat_txt,))
                    id_categoria = cursor.fetchone()[0]

                # 3. Insertar e Inferencia de ID_Ubicacion (Dimensión)
                cursor.execute("INSERT INTO Dim_Ubicacion (Latitud, Longitud, ID_Distrito) VALUES (?, ?, ?)", (lat_val, lon_val, id_distrito))
                cursor.execute("SELECT MAX(ID_Ubicacion) FROM Dim_Ubicacion")
                id_ubicacion = cursor.fetchone()[0]

                # 4. Resolver ID_Delito (Dimensión)
                cursor.execute("SELECT ID_Delito FROM Dim_Delito WHERE Nombre_Delito = ? AND ID_Categoria = ?", (delito_txt, id_categoria))
                res_del = cursor.fetchone()
                if res_del: id_delito = res_del[0]
                else:
                    cursor.execute("INSERT INTO Dim_Delito (Nombre_Delito, ID_Categoria) VALUES (?, ?)", (delito_txt, id_categoria))
                    cursor.execute("SELECT ID_Delito FROM Dim_Delito WHERE Nombre_Delito = ? AND ID_Categoria = ?", (delito_txt, id_categoria))
                    id_delito = cursor.fetchone()[0]

                # 5. Insertar e Inferencia de ID_Tiempo (Dimensión)
                f_obj = pd.to_datetime(fecha_str)
                cursor.execute("INSERT INTO Dim_Tiempo (Fecha, Anio, Mes, Dia, Hora_Completa, Rango_Horario) VALUES (?, ?, ?, ?, ?, ?)", (fecha_str, int(f_obj.year), int(f_obj.month), int(f_obj.day), hora_str, rango_h))
                cursor.execute("SELECT MAX(ID_Tiempo) FROM Dim_Tiempo")
                id_tiempo = cursor.fetchone()[0]

                # 6. Inyección final a Tabla de Hechos Central
                cursor.execute("""
                    INSERT INTO Fact_Incidentes (ID_Tiempo, ID_Ubicacion, ID_Delito, Tiempo_Respuesta_Min, Uso_Arma, Captura)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (id_tiempo, id_ubicacion, id_delito, t_resp, uso_arma, captura))
                
                # Inyección espejo a Staging para alimentar gráficos y KPIs remotos
                cursor.execute("""
                    INSERT INTO Staging_Reportes_Policiales (Fecha_Reporte, Hora_Reporte, Distrito, Tipo_Delito, Latitud, Longitud, Tiempo_Respuesta_Min, Uso_Arma, Captura, Rango_Horario, Estado_Limpieza)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Procesado')
                """, (fecha_str, hora_str, distrito_txt, delito_txt, lat_val, lon_val, t_resp, uso_arma, captura, rango_h))
                
                registros_insertados += 1
            
        conexion.commit()
        conexion.close()
        return jsonify({"estado": "EXITO", "mensaje": f"ETL Copo de Nieve Completado: {registros_insertados} registros procesados."})
    except Exception as e:
        return jsonify({"estado": "ERROR", "mensaje": f"Error crítico en Pipeline ETL: {str(e)}"})


# ==========================================
# RUTA: MÉTRICAS DEL DATA WAREHOUSE (Capa 4)
# ==========================================
@app.route('/dw-stats', methods=['GET'])
def metricas_dw():
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        # Contamos cuántos registros hay en nuestra tabla de BD
        cursor.execute("SELECT COUNT(*) FROM Staging_Reportes_Policiales WHERE Estado_Limpieza = 'Procesado'")
        total = cursor.fetchone()[0]
        conexion.close()
        
        return jsonify({"estado": "EXITO", "total_registros": total})
    except Exception as e:
        return jsonify({"estado": "ERROR", "mensaje": str(e)})
    
    # Back-End/API/main.py (Actualización de la ruta de IA)

# ... (Tus otras importaciones de arriba se mantienen igual) ...

# IMPORTAMOS LA CLASE DE ML DESDE SU CARPETA CORRESPONDIENTE
from CLASE_ML.modelo_arbol import MotorPredictivoSeguridad

# ... (Tus rutas de /login, /upload, /staging-files, /run-etl y /dw-stats continúan igual) ...


# ==========================================
# RUTA ARQUITECTÓNICA: LLAMA A LA CLASE_ML (Capa 5)
# ==========================================
@app.route('/run-predictions', methods=['GET'])
def ejecutar_ia():
    # Instanciamos la clase dedicada que creamos en CLASE_ML
    motor_ia = MotorPredictivoSeguridad()
    resultados = motor_ia.ejecutar_predicciones_delictivas()
    
    if resultados is None:
        return jsonify({"estado": "ERROR", "mensaje": "Error en el servidor al conectar con la base de datos para la IA."}), 500
        
    if len(resultados) == 0:
        return jsonify({"estado": "ERROR", "mensaje": "No hay datos consolidados en el Data Warehouse para entrenar el árbol de decisión."})

    # Respondemos al Front-End delegando los parámetros del objeto de IA
    return jsonify({
        "estado": "EXITO", 
        "mensaje": "Modelo de Árbol de Decisión (Módulo CLASE_ML) ejecutado correctamente.",
        "precision_modelo": motor_ia.precision,
        "datos": resultados
    })

# ==========================================
# CAPA 6: CÓMPUTO DE KPIs BLINDADO
# ==========================================
@app.route('/kpi-metrics', methods=['GET'])
def obtener_kpis():
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("SELECT Tipo_Delito, Tiempo_Respuesta_Min, Uso_Arma, Captura FROM Staging_Reportes_Policiales WHERE Estado_Limpieza = 'Procesado'")
        filas = cursor.fetchall()
        conexion.close()
        
        total = len(filas)
        if total == 0:
            return jsonify({"estado": "EXITO", "kpis": {"total_incidentes": 0, "tiempo_respuesta": "0 min", "porcentaje_extorsion": "0%", "tasa_captura": "0%", "indice_uso_armas": "0%"}})
            
        extorsiones = 0
        capturas = 0
        armas = 0
        sum_tiempo = 0.0
        
        for f in filas:
            if f[0] and 'Extorsion' in str(f[0]): extorsiones += 1
            if f[1]: sum_tiempo += float(f[1])
            # Validación blindada sin importar mayúsculas/minúsculas
            if f[2] and str(f[2]).upper().strip() == 'TRUE': armas += 1
            if f[3] and str(f[3]).upper().strip() == 'TRUE': capturas += 1
            
        return jsonify({
            "estado": "EXITO",
            "kpis": {
                "total_incidentes": total,
                "tiempo_respuesta": f"{round(sum_tiempo / total, 1)} min",
                "porcentaje_extorsion": f"{round((extorsiones / total) * 100, 1)}%",
                "tasa_captura": f"{round((capturas / total) * 100, 1)}%",
                "indice_uso_armas": f"{round((armas / total) * 100, 1)}%"
            }
        })
    except Exception as e:
        return jsonify({"estado": "ERROR", "mensaje": str(e)})

# ==========================================
# CAPA 7: MOTOR DEL DASHBOARD BLINDADO
# ==========================================
@app.route('/dashboard-analytics', methods=['POST'])
def procesar_filtros_dashboard():
    try:
        datos_filtros = request.json or {}
        distrito = datos_filtros.get('distrito', 'TODOS')
        delito = datos_filtros.get('delito', 'TODOS')
        horario = datos_filtros.get('horario', 'TODOS')

        conexion = conectar_bd()
        cursor = conexion.cursor()
        query_base = "SELECT Distrito, Tipo_Delito, Rango_Horario, Tiempo_Respuesta_Min, Uso_Arma, Captura FROM Staging_Reportes_Policiales WHERE Estado_Limpieza='Procesado'"
        parametros = []
        if distrito != 'TODOS': query_base += " AND Distrito = ?"; parametros.append(distrito)
        if delito != 'TODOS': query_base += " AND Tipo_Delito = ?"; parametros.append(delito)
        if horario != 'TODOS': query_base += " AND Rango_Horario = ?"; parametros.append(horario)
            
        cursor.execute(query_base, parametros)
        filas = cursor.fetchall()
        conexion.close()
        
        distritos_count = {'Los Olivos':0, 'Comas':0, 'San Martin de Porres':0, 'Independencia':0, 'Carabayllo':0, 'Puente Piedra':0, 'Ancon':0, 'Santa Rosa':0}
        delitos_count = {'Robo a mano armada':0, 'Hurto simple':0, 'Extorsion':0, 'Robo de vehiculo':0, 'Vandalismo':0, 'Arrebato':0}
        horarios_count = {'Madrugada':0, 'Manana':0, 'Tarde':0, 'Noche':0}
        tabla_dinamica = []
        
        sum_tiempo = 0.0
        extorsiones = 0
        capturas = 0
        armas = 0
        
        for f in filas:
            dis, delit, hor = str(f[0]), str(f[1]), str(f[2])
            tie = float(f[3]) if f[3] else 0.0
            arm, cap = str(f[4]).upper().strip(), str(f[5]).upper().strip()
            
            if dis in distritos_count: distritos_count[dis] += 1
            if delit in delitos_count: delitos_count[delit] += 1
            if hor in horarios_count: horarios_count[hor] += 1
            
            sum_tiempo += tie
            if 'Extorsion' in delit: extorsiones += 1
            if arm == 'TRUE': armas += 1
            if cap == 'TRUE': capturas += 1
            
            if len(tabla_dinamica) < 8:
                tabla_dinamica.append({"cuadrante": f"{dis} - Sector Alpha", "delito": delit, "efectivos": "3 Unidades" if tie > 15 else "1 Unidad", "estado": "Crítico" if arm == 'TRUE' else "Controlado"})

        total_f = len(filas)
        return jsonify({
            "estado": "EXITO", "total": total_f,
            "avg_tiempo": f"{round(sum_tiempo / total_f, 1)} min" if total_f > 0 else "0 min",
            "pct_extorsion": f"{round((extorsiones / total_f) * 100, 1)}%" if total_f > 0 else "0%",
            "pct_captura": f"{round((capturas / total_f) * 100, 1)}%" if total_f > 0 else "0%",
            "pct_armas": f"{round((armas / total_f) * 100, 1)}%" if total_f > 0 else "0%",
            "distritos": distritos_count, "delitos": delitos_count, "horarios": horarios_count, "tabla": tabla_dinamica
        })
    except Exception as e:
        return jsonify({"estado": "ERROR", "mensaje": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)