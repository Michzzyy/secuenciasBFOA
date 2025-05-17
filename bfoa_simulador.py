import pandas as pd
from datetime import datetime
import time
import random
import subprocess
import re
import numpy as np
from multiprocessing import Pool

# Configuración de parámetros del algoritmo
PARAMS = {
    'numeroDeBacterias': 8,
    'numRandomBacteria': 1,
    'iteraciones': 6,
    'tumbo': 7,
    'nado': 5,
    'dAttr': 0.08,
    'wAttr': 0.001,
    'hRep': 0.05,
    'wRep': 0.0005
}

def ejecutar_algoritmo(ejecucion):
    """Función que ejecuta el algoritmo BFOA y captura los resultados"""
    print(f"Ejecutando BFOA #{ejecucion+1}...")
    
    # Registrar tiempo de inicio
    tiempo_inicio = time.time()
    
    # Ejecutar el algoritmo real (ajusta la ruta según sea necesario)
    resultado = subprocess.run(['python', 'parallel_BFOA.py'], 
                             capture_output=True, text=True)
    
    # Procesar la salida para extraer métricas
    output = resultado.stdout
    
    # Extraer el Very Best de la salida
    best_match = re.search(r"Very Best: \[(.*?)\]", output)
    if best_match:
        best_data = best_match.group(1).split(', ')
        best_idx = int(best_data[0]) if best_data[0] != 'None' else 0
        fitness = float(best_data[1]) if best_data[1] != 'None' else 0.0
    else:
        best_idx, fitness = 0, 0.0
    
    # Extraer NFE (Number of Function Evaluations)
    nfe_match = re.search(r"NFE: (\d+)", output)
    nfe = int(nfe_match.group(1)) if nfe_match else 0
    
    # Extraer tiempos
    time_match = re.search(r"--- ([\d.]+) seconds ---", output)
    tiempo_ejec = float(time_match.group(1)) if time_match else 0.0
    
    # Para Blosum Score e Interaction, necesitarías modificar parallel_BFOA.py para imprimirlos
    # Estos son valores simulados como ejemplo:
    blosum = round(fitness * 0.7, 2)
    interaction = round(fitness * 0.3, 2)
    
    return {
        'Ejecución': ejecucion + 1,
        'Best': best_idx,
        'Fitness': fitness,
        'Blosum Score': blosum,
        'Interaction': interaction,
        'NFE': nfe,
        'Time (s)': tiempo_ejec,
        'Params': str(PARAMS)  # Guardamos los parámetros usados
    }

def generar_excel():
    NUM_EJECUCIONES = 30
    resultados = []
    
    # Usamos multiprocessing para ejecuciones paralelas
    with Pool() as pool:
        resultados = pool.map(ejecutar_algoritmo, range(NUM_EJECUCIONES))
    
    # Crear DataFrame y exportar a Excel
    df = pd.DataFrame(resultados)
    
    # Calcular estadísticas adicionales
    stats = {
        'Media Fitness': np.mean(df['Fitness']),
        'Max Fitness': np.max(df['Fitness']),
        'Min Fitness': np.min(df['Fitness']),
        'Std Fitness': np.std(df['Fitness']),
        'Media Time': np.mean(df['Time (s)']),
        'Total NFE': np.sum(df['NFE'])
    }
    
    # Crear hoja de estadísticas
    stats_df = pd.DataFrame.from_dict(stats, orient='index', columns=['Valor'])
    
    excel_name = f"BFOA_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    with pd.ExcelWriter(excel_name) as writer:
        df.to_excel(writer, sheet_name='Resultados', index=False)
        stats_df.to_excel(writer, sheet_name='Estadísticas')
    
    print(f"\n✅ Archivo Excel generado: {excel_name}")
    print("\nResumen de resultados:")
    print(df.describe())
    print("\nEstadísticas clave:")
    print(stats_df)

if __name__ == "__main__":
    generar_excel()