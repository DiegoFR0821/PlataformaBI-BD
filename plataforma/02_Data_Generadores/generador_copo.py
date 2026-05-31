import pandas as pd
import random
from datetime import datetime, timedelta

distritos = ['Los Olivos', 'Comas', 'San Martin de Porres', 'Independencia', 'Carabayllo', 'Puente Piedra', 'Ancon', 'Santa Rosa']
delitos = ['Robo a mano armada', 'Hurto simple', 'Extorsion', 'Robo de vehiculo', 'Vandalismo', 'Arrebato']
horarios = ['Madrugada', 'Manana', 'Tarde', 'Noche']

registros = []
fecha_base = datetime(2026, 1, 1)

for i in range(500):
    delito = random.choice(delitos)
    h_elegido = random.choice(horarios)
    
    if h_elegido == 'Madrugada': h_base = random.randint(0, 5)
    elif h_elegido == 'Manana': h_base = random.randint(6, 11)
    elif h_elegido == 'Tarde': h_base = random.randint(12, 17)
    else: h_base = random.randint(18, 23)
    
    uso_arma = 'TRUE' if (delito == 'Robo a mano armada' or random.random() > 0.6) else 'FALSE'
    captura = 'TRUE' if random.random() > 0.65 else 'FALSE'
    
    registros.append([
        (fecha_base + timedelta(days=random.randint(0, 120))).strftime('%Y-%m-%d'),
        f"{h_base:02d}:{random.randint(0,59):02d}",
        random.choice(distritos),
        delito,
        round(-11.9 + random.uniform(-0.1, 0.1), 4),
        round(-77.0 + random.uniform(-0.1, 0.1), 4),
        round(random.uniform(5.0, 30.0), 1),
        uso_arma,
        captura,
        h_elegido
    ])

df = pd.DataFrame(registros, columns=['Fecha_Reporte', 'Hora_Reporte', 'Distrito', 'Tipo_Delito', 'Latitud', 'Longitud', 'Tiempo_Respuesta_Min', 'Uso_Arma', 'Captura', 'Rango_Horario'])
df.to_csv('Data_CopoNieve_500.csv', index=False)
print("¡Archivo 'Data_CopoNieve_1000.csv' generado correctamente!")