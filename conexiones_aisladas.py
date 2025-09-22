print("Conexiones no aisladas")
import os
import pandas as pd
import networkx as nx

# Carpeta GEOC
directorio = "GEOC"
carpetas = [f for f in os.listdir(directorio) 
            if f.startswith('2') and os.path.isdir(os.path.join(directorio, f))]

# Convertir a DataFrame
df = pd.DataFrame([c.split('_') for c in carpetas], columns=['start', 'end'])
df['start'] = pd.to_datetime(df['start'], format='%Y%m%d')
df['end'] = pd.to_datetime(df['end'], format='%Y%m%d')
df = df.sort_values('start').reset_index(drop=True)

# Crear grafo original
G = nx.Graph()
for _, row in df.iterrows():
    G.add_edge(row['start'], row['end'])

# Detectar huecos (islas)
islas = []
for i in range(len(df)-1):
    if df.loc[i, 'end'] < df.loc[i+1, 'start'] - pd.Timedelta(days=1):
        islas.append((df.loc[i, 'end'], df.loc[i+1, 'start']))

# Generar nuevas conexiones para unir islas
conexiones_nuevas = []
fechas = sorted(set(df['start']).union(set(df['end'])))

for gap_start, gap_end in islas:
    # Fechas disponibles posteriores al gap_start
    posteriores = [f for f in fechas if f > gap_start]
    # Fechas disponibles anteriores al gap_end
    anteriores = [f for f in fechas if f < gap_end]

    if posteriores and anteriores:
        cercanas_post = posteriores[:2]   # 2 más próximas después
        cercanas_ant = anteriores[-2:]    # 2 más próximas antes

        lejana_post = [posteriores[-1]]   # la más lejana hacia adelante
        lejana_ant = [anteriores[0]]      # la más lejana hacia atrás

        # Fecha real más cercana ANTERIOR al gap_start
        fecha_inicio_real = max([f for f in fechas if f <= gap_start], default=None)
        # Fecha real más cercana POSTERIOR al gap_end
        fecha_fin_real = min([f for f in fechas if f >= gap_end], default=None)

        if fecha_inicio_real:
            for f in cercanas_post + lejana_post:
                conexiones_nuevas.append((fecha_inicio_real, f))
                G.add_edge(fecha_inicio_real, f)

        if fecha_fin_real:
            for f in cercanas_ant + lejana_ant:
                conexiones_nuevas.append((f, fecha_fin_real))
                G.add_edge(f, fecha_fin_real)

# Guardar en archivo
with open('interferogramasnoaislados.txt', 'w') as f:
    for conn in conexiones_nuevas:
        start_str = conn[0].strftime('%Y%m%d')
        end_str = conn[1].strftime('%Y%m%d')
        f.write(f"{start_str}_{end_str}\n")

print("Archivo 'interferogramasnoaislados.txt' generado con las conexiones no aisladas.")
