import json
import os
# Asegúrate de importar el nombre correcto de tu clase principal desde main.py
from main import PipelineAcademicoTDAH 

def probar_solo_keyframes():
    ruta_json = "outputs/evidencia_fases_3_4_storyboard.json"
    
    # 1. Verificamos que el "checkpoint" exista
    if not os.path.exists(ruta_json):
        print(f"Error: No se encontró el archivo {ruta_json}. Debes correr el pipeline completo al menos una vez.")
        return

    # 2. Cargamos el estado guardado en memoria
    print(f"Cargando estado guardado desde: {ruta_json}")
    with open(ruta_json, 'r', encoding='utf-8') as f:
        resultados_f3_f4 = json.load(f)
        
    # 3. Instanciamos tu clase principal
    # (Al no llamar a ejecutar_fase1_y_2, la API de Groq no se activa)
    pipeline = PipelineAcademicoTDAH()
    
    # 4. Ejecutamos SOLO la Fase 5
    pipeline.exportar_prompts_keyframes(resultados_f3_f4)
    pipeline.exportar_prompts_video(resultados_f3_f4)
    
    print("\n¡Prueba de Fase 5 Y 6 finalizada sin consumir tokens!")

if __name__ == "__main__":
    probar_solo_keyframes()