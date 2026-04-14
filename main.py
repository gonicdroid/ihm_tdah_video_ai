import os
import json
import subprocess
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from groq import Groq
from dotenv import load_dotenv

# Cargar variables de entorno (tu GROQ_API_KEY)
load_dotenv()

class VideoGeneratorStrategy(ABC):
    """Interfaz para la generación de video."""
    @abstractmethod
    def generar_clip(self, prompt_visual: str, texto_pantalla: str, duracion: int, output_filename: str) -> str:
        pass

class MockVideoGenerator(VideoGeneratorStrategy):
    """Generador de prueba local que no consume créditos. Usa FFmpeg."""
    def generar_clip(self, prompt_visual: str, texto_pantalla: str, duracion: int, output_filename: str) -> str:
        print(f"[MOCK] Generando video para: '{prompt_visual}'...")
        # Genera un video negro de 'duracion' segundos con el texto centrado usando FFmpeg
        comando = [
            'ffmpeg', '-y', '-f', 'lavfi', '-i', f'color=c=black:s=1080x1920:d={duracion}',
            '-vf', f"drawtext=text='{texto_pantalla}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
            output_filename
        ]
        # Ejecutamos de forma silenciosa
        subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[MOCK] Clip guardado: {output_filename}")
        return output_filename

class APIRepareVideoGenerator(VideoGeneratorStrategy):
    """Implementación futura para Replicate, Kling, etc."""
    def generar_clip(self, prompt_visual: str, texto_pantalla: str, duracion: int, output_filename: str) -> str:
        # TODO: Implementar la llamada HTTP a la API real.
        raise NotImplementedError("La API real de video aún no está conectada.")

class CerebroPsicologico:
    """Se encarga de comunicarse con Groq para estructurar el guion TDAH."""
    def __init__(self):
        self.cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
    def generar_guion(self, texto_fuente: str) -> Dict[str, Any]:
        prompt_sistema = """
        Eres un experto en psicología del consumidor y TDAH. 
        Tu objetivo es tomar el texto conceptual provisto y devolver ÚNICAMENTE un objeto JSON.
        El guion debe durar máximo 6 segundos, dividido en bloques de 2 segundos.
        Aplica estrictamente: Bloque 1 (Pulsión de muerte/Pérdida) -> Bloque 2 (Neutro/Transición) -> Bloque 3 (Pulsión de vida/Recompensa).
        
        Formato JSON requerido:
        {
          "escenas": [
            {
              "bloque": 1,
              "prompt_visual_ia": "Descripción visual detallada",
              "texto_en_pantalla": "TEXTO CORTO",
              "texto_para_locucion": "Locución persuasiva"
            }
          ]
        }
        NO devuelvas markdown, solo el JSON puro.
        """
        
        print("[GROQ] Solicitando estructuración del guion...")
        respuesta = self.cliente.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Texto fuente: {texto_fuente}"}
            ],
            model=os.getenv("LLM_MODEL"), # Modelo muy rápido y gratuito
            temperature=0.3, # Baja temperatura para evitar alucinaciones en el JSON
        )
        
        contenido = respuesta.choices[0].message.content
        try:
            return json.loads(contenido)
        except json.JSONDecodeError:
            print("ERROR: Groq no devolvió un JSON válido. Revisa el prompt.")
            return {"escenas": []}

class PipelineTDAH:
    """Orquestador principal."""
    def __init__(self, video_strategy: VideoGeneratorStrategy):
        self.cerebro = CerebroPsicologico()
        self.video_gen = video_strategy
        
    def ejecutar(self, texto_pdf: str):
        # 1. Generar JSON
        guion = self.cerebro.generar_guion(texto_pdf)
        escenas = guion.get("escenas", [])
        
        if not escenas:
            print("Abortando pipeline por error en guion.")
            return

        archivos_generados = []
        
        # 2. Iterar y generar clips
        for i, escena in enumerate(escenas):
            nombre_archivo = f"clip_{i+1}.mp4"
            # Asumimos bloques de 2 segundos según las notas de clase
            self.video_gen.generar_clip(
                prompt_visual=escena["prompt_visual_ia"],
                texto_pantalla=escena["texto_en_pantalla"],
                duracion=2, 
                output_filename=nombre_archivo
            )
            archivos_generados.append(nombre_archivo)
            
        print("\n--- FASE DE VIDEO COMPLETADA ---")
        print("Archivos listos para ensamblar:", archivos_generados)
        print("Próximo paso a desarrollar: Integrar Edge-TTS para el audio y concatenar todo con FFmpeg.")

if __name__ == "__main__":
    # Inyectamos la estrategia Mock para no gastar plata mientras desarrollamos
    generador_video = MockVideoGenerator()
    pipeline = PipelineTDAH(generador_video)
    
    texto_prueba = "El sedentarismo está destruyendo tu metabolismo lentamente. Si caminas 30 minutos al día, reactivas tu sistema cardiovascular y extiendes tu expectativa de vida."
    
    pipeline.ejecutar(texto_prueba)
