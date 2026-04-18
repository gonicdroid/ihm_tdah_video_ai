import os
import json
from typing import Dict, Any
from groq import Groq
from dotenv import load_dotenv
from ingesta import ExtractorDocumental

# Cargar variables de entorno
load_dotenv()

class CerebroPsicologico:
    """Implementa el Pipeline de IA dividido en fases según la rúbrica académica."""
    def __init__(self):
        self.cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.modelo = os.getenv("LLM_MODEL")

    def ejecutar_fase1_y_2(self, texto_fuente: str) -> Dict[str, Any]:
        """Fase 1 (Síntesis) y Fase 2 (Generación de Hooks)."""
        prompt_sistema = """
        Eres un analista experto en marketing digital y psicología de la atención. 
        Tu tarea es procesar el texto fuente y extraer la información clave.
        
        REGLA VITAL PARA LOS HOOKS: Deben aplicar el concepto de "Pulsión de muerte" (Pérdida, urgencia, alerta). 
        No hagas preguntas amables. Apela al miedo a perder una oportunidad o dinero.
        
        Devuelve ÚNICAMENTE un JSON con esta estructura exacta:
        {
          "fase_1_sintesis": {
            "tema_central": "...",
            "tres_ideas_importantes": ["...", "...", "..."],
            "idea_principal_video": "...",
            "palabras_clave": ["...", "..."],
            "tono_deseado": "Urgente y resolutivo"
          },
          "fase_2_mensaje": {
            "hooks_propuestos": ["Hook 1 (Agresivo)...", "Hook 2 (Urgencia)...", "Hook 3 (Pérdida)..."]
          }
        }
        NO devuelvas markdown, solo el JSON puro.
        """
        print("[GROQ] Ejecutando Fases 1 y 2: Síntesis y Generación de Opciones...")
        respuesta = self.cliente.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Texto fuente: {texto_fuente}"}
            ],
            model=self.modelo,
            temperature=0.4, # Un poco más de temperatura para mayor creatividad en los hooks
        )
        return json.loads(respuesta.choices[0].message.content)

    def ejecutar_fase3_y_4(self, datos_sintesis: Dict[str, Any]) -> Dict[str, Any]:
        """Fase 3 (Traducción Psicológica) y Fase 4 (Storyboard de 8 escenas)."""
        prompt_sistema = """
        Eres un experto en psicología IHM y TDAH. Usa el JSON de síntesis provisto para crear el guion del video.
        DEBES utilizar obligatoriamente el "hook_elegido_por_humano" como texto inicial de la primera escena.
        
        REGLAS DEL STORYBOARD:
        - 8 escenas exactas de 2 segundos cada una (16s totales).
        - Escenas 1-2 (0-4s): Pulsión de muerte (Alerta, pérdida, uso del Hook elegido).
        - Escenas 3-4 (4-8s): Neutro (Transición).
        - Escenas 5-8 (8-16s): Pulsión de vida (Recompensa).
        - "prompt_visual_ia": Debe ser en INGLÉS, ultra-descriptivo, y mantener continuidad visual entre escenas.
        
        Devuelve ÚNICAMENTE un JSON con esta estructura:
        {
          "fase_3_psicologia": {
            "recursos_utilizados": [
              {"recurso": "Contraste visual", "justificacion": "..."},
              {"recurso": "Recompensa inmediata", "justificacion": "..."}
            ]
          },
          "fase_4_storyboard": [
             {
              "escena_numero": 1,
              "tiempo": "0s - 2s",
              "fase_psicologica": "Pulsión de muerte",
              "prompt_visual_ia": "Cinematic close up of...",
              "texto_en_pantalla": "TEXTO CORTO Y GRANDE",
              "texto_para_locucion": "Locución"
            }
          ]
        }
        NO devuelvas markdown, solo el JSON puro.
        """
        print("[GROQ] Ejecutando Fases 3 y 4: Traducción Psicológica y Storyboard...")
        texto_contexto = json.dumps(datos_sintesis, ensure_ascii=False)
        
        respuesta = self.cliente.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Datos de síntesis con elección del usuario: {texto_contexto}"}
            ],
            model=self.modelo,
            temperature=0.2,
        )
        return json.loads(respuesta.choices[0].message.content)


class PipelineAcademicoTDAH:
    """Orquestador maestro de todas las fases del TP."""
    def __init__(self):
        self.cerebro = CerebroPsicologico()
        
    def ejecutar(self, texto_crudo: str):
        os.makedirs("outputs", exist_ok=True)
        
        # 1. Fases 1 y 2
        try:
            resultados_f1_f2 = self.cerebro.ejecutar_fase1_y_2(texto_crudo)
        except Exception as e:
            print(f"Error en Fases 1 y 2: {e}")
            return
            
        # --- INTERVENCIÓN DEL USUARIO (HUMAN IN THE LOOP) ---
        hooks = resultados_f1_f2.get("fase_2_mensaje", {}).get("hooks_propuestos", [])
        
        if not hooks:
            print("Error: La IA no generó hooks válidos.")
            return

        print("\n" + "="*50)
        print(" INTERVENCIÓN HUMANA REQUERIDA (Fase 2)")
        print("="*50)
        print("La IA generó los siguientes ganchos atencionales. Selecciona el más adecuado:")
        
        for i, hook in enumerate(hooks):
            print(f"\n[{i+1}] {hook}")
            
        seleccion = 0
        while seleccion not in [1, 2, 3]:
            try:
                entrada = input("\nIngresa el número de tu elección (1, 2 o 3): ")
                seleccion = int(entrada)
            except ValueError:
                print("Por favor, ingresa un número válido.")
                
        hook_elegido = hooks[seleccion - 1]
        print(f"\n[+] Excelente elección. Hook configurado: '{hook_elegido}'\n")
        
        # Inyectamos la decisión en el diccionario
        resultados_f1_f2["fase_2_mensaje"]["hook_elegido_por_humano"] = hook_elegido
        
        # Guardamos la evidencia de Fases 1 y 2
        with open("outputs/evidencia_fases_1_2.json", 'w', encoding='utf-8') as f:
            json.dump(resultados_f1_f2, f, indent=4, ensure_ascii=False)
        print("  -> Fases 1 y 2 guardadas.")

        # 2. Fases 3 y 4 (Le pasamos el JSON que ahora incluye la decisión del usuario)
        try:
            resultados_f3_f4 = self.cerebro.ejecutar_fase3_y_4(resultados_f1_f2)
            with open("outputs/evidencia_fases_3_4_storyboard.json", 'w', encoding='utf-8') as f:
                json.dump(resultados_f3_f4, f, indent=4, ensure_ascii=False)
            print("  -> Fases 3 y 4 completadas y guardadas.")
        except Exception as e:
            print(f"Error en Fases 3 y 4: {e}")
            return
            
        print("\n--- PIPELINE ESTRATÉGICO COMPLETADO ---")
        print("Revisa la carpeta 'outputs/' para ver el Storyboard final.")

if __name__ == "__main__":
    pipeline = PipelineAcademicoTDAH()
    extractor = ExtractorDocumental()
    
    carpeta_entrada = "assets"
    
    print("Iniciando Extracción documental...")
    texto_crudo = extractor.procesar_directorio(carpeta_entrada)
    
    if not texto_crudo.strip():
        print("No se encontró texto para procesar. Abortando.")
    else:
        max_caracteres = 15000 
        if len(texto_crudo) > max_caracteres:
            texto_crudo = texto_crudo[:max_caracteres]
            
        pipeline.ejecutar(texto_crudo)