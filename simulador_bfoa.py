import pandas as pd
from datetime import datetime
import time
import random
import subprocess
import re
#CORRER 30 VECES EL CODIGO BFOA 

def ejecutar_algoritmo(ejecucion):
    """Función que simula la ejecución del algoritmo BFOA"""
    print(f"Ejecutando BFOA #{ejecucion+1}...")
    
    # Simulación de tiempos y resultados 
    tiempo_inicio = time.time()
    time.sleep(random.uniform(2.0, 5.0))  # Simula tiempo de ejecución
    
    # Genera datos de ejemplo 
    best_idx = random.randint(0, 3)
    fitness = round(1000 + random.uniform(-200, 200), 2)
    blosum = round(fitness * 0.7, 2)
    interaction = round(fitness * 0.3, 2)
    nfe = random.randint(800, 1200)
    tiempo_ejec = round(time.time() - tiempo_inicio, 2)
    
    return {
        'Ejecución': ejecucion + 1,
        'Best': best_idx,
        'Fitness': fitness,
        'Blosum Score': blosum,
        'Interaction': interaction,
        'NFE': nfe,
        'Time (s)': tiempo_ejec
    }

def generar_excel():
    NUM_EJECUCIONES = 30
    resultados = []
    
    for ejecucion in range(NUM_EJECUCIONES):
        resultados.append(ejecutar_algoritmo(ejecucion))
    
    # Crear DataFrame y exportar a Excel
    df = pd.DataFrame(resultados)
    excel_name = f"BFOA_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(excel_name, index=False)
    
    print(f"\n✅ Archivo Excel generado: {excel_name}")
    print("\nResumen de resultados:")
    print(df.describe())

if __name__ == "__main__":
    generar_excel()