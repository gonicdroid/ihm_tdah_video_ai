import os
import json
from typing import Dict, Any
import re
from groq import Groq
import subprocess
from dotenv import load_dotenv
from ingesta import ExtractorDocumental

# Cargar variables de entorno
load_dotenv()

class CerebroPsicologico:
    """Implementa el Pipeline de IA dividido en fases según la rúbrica académica."""
    def __init__(self):
        self.cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.modelo = os.getenv("LLM_MODEL")

    def _limpiar_json(self, texto_respuesta: str) -> Dict[str, Any]:
        """Sanitiza la respuesta del LLM quitando bloques de markdown antes de parsear."""
        texto_limpio = texto_respuesta.strip()
        # Usamos expresiones regulares para extraer solo lo que esté entre la primera llave { y la última }
        match = re.search(r'\{.*\}', texto_limpio, re.DOTALL)
        if match:
            texto_limpio = match.group(0)
            
        try:
            return json.loads(texto_limpio)
        except json.JSONDecodeError as e:
            print(f"\n[!] ERROR CRÍTICO AL PARSEAR JSON: {e}")
            print(f"--- RESPUESTA CRUDA DE LA IA ---\n{texto_respuesta}\n--------------------------------")
            raise

    def ejecutar_fase1_y_2(self, texto_fuente: str) -> Dict[str, Any]:
        """Fase 1 (Síntesis) y Fase 2 (Generación de Hooks)."""
        prompt_sistema = """
            Eres un analista experto en procesamiento de información y psicología de la atención (Interfaz Hombre Máquina).
            Tu objetivo es extraer y estructurar la información crítica del texto fuente provisto, el cual será utilizado para crear un video corto dirigido a ciudadanos, contemplando las necesidades de usuarios con déficit de atención (TDAH).
            1. Thanatos (0-4s): El gancho de pérdida que genera una reacción inmediata de alerta, urgencia o miedo para que el espectador reaccione instantáneamente. Mostrando un escenario catastrófico o la posibilidad de perder algo, siendo agresivo. 
            2. Neutro (4-8s): Transición institucional que transmite seguridad y reduce la carga cognitiva.
            3. Pulsión de Vida (8-14s): Recompensa inmediata y solución al problema planteado.
            INSTRUCCIONES: Analiza el texto fuente y extrae ÚNICAMENTE los siguientes elementos pensando en cómo alimentar esta arquitectura psicológica:
            1. Tema central del PDF: Resumen objetivo en una oración.
            2. Tres ideas importantes: Los tres datos duros o beneficios más críticos del documento. 
            3. Idea principal para el video: Un concepto accionable que sirva para generar el "gancho" de pérdida (Pulsión de muerte) y la "solución" (Pulsión de vida).
            4. Palabras clave: 4 a 6 términos esenciales.
            5. Tono deseado: Cómo debe comunicarse el mensaje.
            6. Para los "hooks_propuestos": redacta 3 ganchos que utilicen obligatoriamente la pulsión de muerte. Longitud máxima de 10 palabras, estrictamente afirmaciones. No debes dar la solución al problema.

            FORMATO DE SALIDA: Debes devolver ÚNICAMENTE un objeto JSON válido SIN MARKDOWN con la siguiente estructura exacta:
            {
              "fase_1_sintesis": {
                "tema_central": "",
                "tres_ideas_importantes": ["", "", ""],
                "idea_principal_video": "",
                "palabras_clave": ["", "", "", ""],
                "tono_deseado": ""
              },
              "fase_2_mensaje": {
                "hooks_propuestos": ["", "", ""] 
              }
            }
        """
        print("Ejecutando Fases 1 y 2: Síntesis y Generación de Opciones...")
        respuesta = self.cliente.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Texto fuente: {texto_fuente}"}
            ],
            model=self.modelo,
            temperature=0.4, # Un poco más de temperatura para mayor creatividad en los hooks
        )
        return self._limpiar_json(respuesta.choices[0].message.content)

    def ejecutar_fase3_y_4(self, datos_sintesis: Dict[str, Any]) -> Dict[str, Any]:
        """Fase 3 (Traducción Psicológica) y Fase 4 (Storyboard de 8 escenas)."""
        prompt_sistema = """
        # Eres un experto en psicología Interfaz Hombre Máquina y TDAH. 
        * El TDAH es un trastorno que implica diferencias reales en la regulación de la atención, el control conductual y la relación con la recompensa inmediata. Diseñar para este público obliga a minimizar la carga cognitiva, reducir la fricción visual y ofrecer refuerzos inmediatos y salientes. 
        * La Arquitectura Psicológica: Thanatos, Neutro y Eros: tres fases psicológicas secuenciales que manipulan los niveles de dopamina del usuario.

        # REGLAS DEL STORYBOARD VISUAL:
        - Usa el JSON de síntesis provisto para crear el guion del video.
        - DEBES utilizar obligatoriamente el "hook_elegido_por_humano" como texto inicial de la primera escena.
        - 7 escenas exactas de 2 segundos cada una (14s totales). En redes sociales se tiene apenas 10 a 14 segundos para captar al usuario, si no se logra, simplemente saltean.
        - Escenas 1-2 (0-4s): Pulsión de muerte, fase 1: "Thanatos"
            * El cerebro reacciona instantáneamente a la alerta, la pérdida o la urgencia. Al mostrar un escenario catastrófico o la posibilidad de perder algo, el cerebro inyecta dopamina y fuerza al usuario a prestar atención.
            * Ejecución: ser agresivo visual o auditivamente (ej. frecuencias altas, colores rojos, imágenes de desesperación).
            * Ejemplo: "Las nuevas cepas avanzan y estás perdiendo tu oportunidad de inmunizarte. Podrías quedarte sin tu dosis."
        - Escenas 3-4 (4-8s): Fase 2: Neutro.
            * Pasar al usuario del "modo pánico" a una transición para tranquilizarlo. El neutro baja o mantiene esa dopamina "negativa" para prepararlo para el mensaje que se quiere dar.
            * Ejecución: Cortás la saturación. Mostrás un elemento que transmita seguridad o institucionalidad.
            * Ejemplo: Corte abrupto a una placa minimalista, aparecen los logos nacionales, el audio baja de frecuencia. "Plan Estratégico de Salud Pública".
        - Escenas 5-8 (8-14s): Fase 3: Pulsión de vida. "Eros" La Recompensa.
            * Es la entrega de la buena noticia. Esta fase debe restaurar la situación de estrés que generaste en la Pulsión de Muerte. Vuelve a subir la dopamina, pero esta vez con una connotación positiva.
            * Ejecución: Mensajes simples, soluciones directas y refuerzos inmediatos. El usuario nunca debe irse amargado.
            * Ejemplo: "Acá te vacunamos gratis, sin turnos y cerca de tu casa. Protegé a los tuyos hoy mismo."
        - "prompt_visual_ia": Debes describir la escena de forma ultra-descriptivo sobre cámara, movimientos, objetos, adjetivos, colores, y filtros. Longitud de al menos 40 palabras. DEBES mantener continuidad visual entre escenas.
        - El guión debe apoyarse en al menos 3 de estos recursos: atención selectiva, saliencia visual, novedad, contraste, carga cognitiva, memoria de trabajo, motivación, recompensa inmediata, emoción, legibilidad, jerarquía visual, reducción de fricción.

        1. REGLAS DE PISTA NARRATIVA (AUDIO Y TEXTO):
        - Solo habrá 3 textos en todo el video (uno por cada fase psicológica).
        - Fase 1 (Thanatos - 0s a 4s): Usa OBLIGATORIAMENTE el "hook_elegido_por_humano" y genera máximo 9 palabras. 
        - Fase 2 (Neutro - 4s a 8s): Transición institucional que transmite seguridad. genera máximo 6 palabras.
        - Fase 3 (Eros - 8s a 14s): Solución y recompensa inmediata. Genera máximo 12 palabras

        Devuelve ÚNICAMENTE un JSON PURO con esta estructura exacta:
        {
          "fase_3_psicologia": {
              "recursos_utilizados": [
                  {"recurso": "Redundancia bimodal", "justificacion": "..."},
                  {"recurso": "Contraste visual", "justificacion": "..."}
              ]
          },
          "fase_4_pista_narrativa": [
              {
                  "fase": "Thanatos",
                  "tiempo": "0s - 4s",
                  "texto_bimodal": "TEXTO CORTO QUE SE LEERÁ Y ESCUCHARÁ",
                  "sonido_de_fondo": "SFX sugerido"
              },
              {
                  "fase": "Neutro",
                  "tiempo": "4s - 8s",
                  "texto_bimodal": "TEXTO CORTO",
                  "sonido_de_fondo": "SFX sugerido"
              },
              {
                  "fase": "Eros",
                  "tiempo": "8s - 14s",
                  "texto_bimodal": "TEXTO DE CIERRE",
                  "sonido_de_fondo": "SFX sugerido"
              }
          ],
          "fase_4_pista_visual": [
              {
                  "escena_numero": 1,
                  "tiempo": "0s - 2s",
                  "prompt_visual_ia": "Cinematic close up..."
              }
              // ... Continúa hasta la escena 7
          ]
        }
        """
        print("Ejecutando Fases 3 y 4: Traducción Psicológica y Storyboard...")
        texto_contexto = json.dumps(datos_sintesis, ensure_ascii=False)
        
        respuesta = self.cliente.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Datos de síntesis con elección del usuario: {texto_contexto}"}
            ],
            model=self.modelo,
            temperature=0.2,
        )
        return self._limpiar_json(respuesta.choices[0].message.content)


class PipelineAcademicoTDAH:
    """Orquestador maestro de todas las fases del TP."""
    def __init__(self):
        self.cerebro = CerebroPsicologico()
        
    def generar_audios(self, resultados_f3_f4: Dict[str, Any]):
        """Fase 7: Generación de Voz HD usando Edge-TTS (Desacoplado)."""
        print("\n[EDGE-TTS] Iniciando generación de locución bimodal (Fase 7)...")
        # AHORA LEEMOS LA PISTA NARRATIVA, NO LA VISUAL
        narrativas = resultados_f3_f4.get("fase_4_pista_narrativa", [])
        
        for i, bloque in enumerate(narrativas):
            fase_nombre = bloque.get("fase", f"bloque_{i}")
            texto = bloque.get("texto_bimodal", "")
            
            if not texto:
                continue
                
            archivo_salida = f"outputs/audio_{fase_nombre.lower()}.mp3"
            print(f"  -> Generando audio para {fase_nombre}: '{texto}'")
            
            comando = [
                "edge-tts",
                "--rate", "+20%",
                "--voice", "es-AR-ElenaNeural",
                "--text", f"'{texto}'",
                "--write-media", archivo_salida
            ]
            
            try:
                subprocess.run(comando, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"     [!] Error al generar audio {fase_nombre}: {e}")
                
        print("  -> Todos los audios (Thanatos, Neutro, Eros) fueron generados en outputs/")

    def exportar_prompts_keyframes(self, resultados_f3_f4: Dict[str, Any]):
        """Fase 5 (Preparación): Extrae los prompts clave inyectando paletas de color por fase."""
        print("\n[KEYFRAMES] Extrayendo prompts visuales y aplicando psicología del color (Fase 5)...")
        escenas = resultados_f3_f4.get("fase_4_pista_visual", [])
        
        # Paletas predefinidas basadas en modulación de atención para TDAH
        config_fases = {
            1: {
                "nombre": "THANATOS (Pulsión de muerte - Alerta/Urgencia)",
                "paleta": "Rojo Carmesí (#D90429), Gris Antracita (#2B2D42), Amarillo Alerta (#FFC300)",
                "instruccion_color": "Aplica una iluminación dramática y de alto contraste predominando estos tonos para generar urgencia y saliencia visual."
            },
            3: {
                "nombre": "NEUTRO (Transición - Descanso Cognitivo)",
                "paleta": "Gris Azulado (#8D99AE), Blanco Roto (#EDF2F4), Cian Suave (#A8DADC)",
                "instruccion_color": "Aplica una paleta desaturada, limpia y de iluminación suave para reducir la carga cognitiva."
            },
            5: {
                "nombre": "EROS (Pulsión de vida - Recompensa/Dopamina)",
                "paleta": "Verde Esmeralda (#06D6A0), Azul Brillante (#118AB2), Amarillo Sol (#FFD166)",
                "instruccion_color": "Aplica una iluminación brillante, vibrante y acogedora predominando estos tonos para transmitir resolución y recompensa visual."
            }
        }
        
        # Prompt maestro más directo, sin pedir texto de retorno
        prompts_exportar = [
            "Eres un director de arte experto en accesibilidad cognitiva.\n",
            "Genera exactamente 3 imágenes utilizando los prompts detallados abajo.\n",
            "REGLA VITAL: Respeta estrictamente la paleta de colores (HEX) y las instrucciones de iluminación exigidas para cada escena. Estas paletas están diseñadas matemáticamente para guiar la respuesta neurológica del espectador.\n",
            "--------------------------------------------------\n\n"
        ]
        
        for escena in escenas:
            num = escena.get("escena_numero")
            if num in config_fases:
                fase = config_fases[num]
                prompt_base = escena.get("prompt_visual_ia", "")
                
                # Ensamblamos el prompt inyectando el color
                bloque_prompt = (
                    f"▶ ESCENA {num} - FASE: {fase['nombre']}\n"
                    f"PALETA OBLIGATORIA: {fase['paleta']}\n"
                    f"ESTILO DE COLOR: {fase['instruccion_color']}\n"
                    f"PROMPT VISUAL: \"{prompt_base}\"\n\n"
                )
                prompts_exportar.append(bloque_prompt)
                
        if len(prompts_exportar) > 4: # Validación simple
            ruta_archivo = "outputs/prompts_keyframes.txt"
            os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.writelines(prompts_exportar)
                
            print(f"  -> Archivo de prompts (con paletas inyectadas) creado exitosamente en: {ruta_archivo}")
            print("  -> PASO MANUAL: Copia el texto y genera las imágenes. Luego, usa esas imágenes como referencia en el modelo Veo.")

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
            
            # --- GENERACIÓN DE AUDIO ---
            self.generar_audios(resultados_f3_f4)
            # --- FASE 5 GENERACION DE KEYFRAMES ---
            self.exportar_prompts_keyframes(resultados_f3_f4)
            
        except Exception as e:
            print(f"Error en Fases 3, 4 o 5: {e}")
            return

            
        print("\n--- PIPELINE ESTRATÉGICO COMPLETADO ---")
        print("Revisa la carpeta 'outputs/' para ver el Storyboard final y los audios .mp3.")

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