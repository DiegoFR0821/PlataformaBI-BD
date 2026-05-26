import pandas as pd
import random
from datetime import datetime, timedelta

distritos = ['Los Olivos', 'Comas', 'San Martin de Porres', 'Independencia', 'Carabayllo', 'Puente Piedra', 'Ancon', 'Santa Rosa']
delitos = ['Robo a mano armada', 'Hurto simple', 'Extorsion', 'Robo de vehiculo', 'Vandalismo', 'Arrebato']
horarios = ['Madrugada', 'Manana', 'Tarde', 'Noche']

registros = []
fecha_base = datetime(2026, 1, 1)

for i in range(1000):
    distrito = random.choice(distritos)
    delito = random.choice(delitos)
    fecha = fecha_base + timedelta(days=random.randint(0, 120))
    
    horario_elegido = random.choice(horarios)
    if horario_elegido == 'Madrugada': h_base = random.randint(0, 5)
    elif horario_elegido == 'Manana': h_base = random.randint(6, 11)
    elif horario_elegido == 'Tarde': h_base = random.randint(12, 17)
    else: h_base = random.randint(18, 23)
    hora = f"{h_base:02d}:{random.randint(0,59):02d}"
    
    lat = round(-11.9 + random.uniform(-0.1, 0.1), 4)
    lon = round(-77.0 + random.uniform(-0.1, 0.1), 4)
    tiempo_resp = round(random.uniform(5.0, 30.0), 1)
    
    # === AQUÍ ESTÁ LA MAGIA PARA QUE TUS KPIs SE MUEVAN ===
    uso_arma = 'TRUE' if (delito == 'Robo a mano armada' or random.random() > 0.6) else 'FALSE'
    captura = 'TRUE' if random.random() > 0.65 else 'FALSE'
    
    registros.append([fecha.strftime('%Y-%m-%d'), hora, distrito, delito, lat, lon, tiempo_resp, uso_arma, captura, horario_elegido])

columnas = ['Fecha_Reporte', 'Hora_Reporte', 'Distrito', 'Tipo_Delito', 'Latitud', 'Longitud', 'Tiempo_Respuesta_Min', 'Uso_Arma', 'Captura', 'Rango_Horario']
df = pd.DataFrame(registros, columns=columnas)
df.to_csv('Reportes_Final_1000.csv', index=False)
print("¡Archivo generado! Listo para subir.")
