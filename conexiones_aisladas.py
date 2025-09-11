print("Conexione saisladas")
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
for gap_start, gap_end in islas:
    # Crear 3 conexiones cercanas a los extremos de cada isla
    conexiones_nuevas.append((gap_start, gap_end))
    conexiones_nuevas.append((gap_start - pd.Timedelta(days=1), gap_end))
    conexiones_nuevas.append((gap_start, gap_end + pd.Timedelta(days=1)))
    for conn in conexiones_nuevas[-3:]:
        G.add_edge(*conn)

# Guardar en archivo
with open('interferogramasnoaislados.txt', 'w') as f:
    for conn in conexiones_nuevas:
        start_str = conn[0].strftime('%Y%m%d')
        end_str = conn[1].strftime('%Y%m%d')
        f.write(f"{start_str}_{end_str}\n")

print("Archivo 'interferogramasnoaislados.txt' generado con las conexiones no aisladas.")

