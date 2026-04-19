import json
import os
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips

def ensamblar_video_tdah(json_path, output_name="video_final_tdah.mp4"):
    # 1. Cargar la configuración del storyboard
    if not os.path.exists(json_path):
        print(f"Error: No se encuentra el archivo {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    pista_narrativa = datos.get("fase_4_pista_narrativa", [])
    pista_visual = datos.get("fase_4_pista_visual", [])

    print(f"--- Iniciando ensamblaje de {len(pista_visual)} clips ---")

    clips_finales = []

    # 2. Procesar las 3 fases psicológicas (Thanatos, Neutro, Eros)
    # Relacionamos los 7 clips de 2s con las 3 fases (2+2+3)
    mapeo_fases = {
        "Thanatos": [1, 2],
        "Neutro": [3, 4],
        "Eros": [5, 6, 7]
    }

    for bloque in pista_narrativa:
        fase = bloque["fase"]
        texto = bloque["texto_bimodal"]
        indices_clips = mapeo_fases.get(fase, [])
        
        # Cargar los videos de esta fase
        clips_fase = []
        for i in indices_clips:
            clip_path = f"outputs/clip_{i}.mp4"
            if os.path.exists(clip_path):
                clips_fase.append(VideoFileClip(clip_path))
            else:
                print(f" Advertencia: Falta el archivo {clip_path}")

        if not clips_fase:
            continue

        # Unir los videos de la fase (ej: clip 1 + clip 2)
        video_fase = concatenate_videoclips(clips_fase)

        # Cargar el audio generado por Edge-TTS para esta fase
        audio_path = f"outputs/audio_{fase.lower()}.mp3"
        if os.path.exists(audio_path):
            audio = AudioFileClip(audio_path)
            # Ajustamos el audio al tiempo del video o viceversa si es necesario
            video_fase = video_fase.set_audio(audio)

        # Crear el texto en pantalla (Redundancia Bimodal)
        # Ajustamos el tamaño y estilo para TDAH: Grande, centrado, alto contraste
        txt_clip = TextClip(
            text=texto.upper(), 
            font_size=75, 
            color=estilo["color"], 
            font="assets/fonts/Lexend-VariableFont_wght.ttf",
            stroke_color=estilo["stroke"],
            stroke_width=3,
            method='caption',
            text_align='center',
            size=(video_fase.w * 0.9, None)
        ).with_duration(video_fase.duration).with_position('center')

        # Componer video + texto
        video_con_texto = CompositeVideoClip([video_fase, txt_clip])
        clips_finales.append(video_con_texto)

    # 3. Concatenar las 3 fases en el video final de 14 segundos
    if clips_finales:
        video_final = concatenate_videoclips(clips_finales)
        print(f"Renderizando video final: {output_name}...")
        video_final.write_videofile(output_name, fps=24, codec="libx264")
        print("¡Video ensamblado con éxito!")
    else:
        print("Error: No se pudo generar ningún clip.")

if __name__ == "__main__":
    # Asegurate de que los nombres de los archivos coincidan
    ensamblar_video_tdah("outputs/evidencia_fases_3_4_storyboard.json")