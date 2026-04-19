import json
import os
import textwrap
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip

def ensamblar_video_veo(json_path, video_path="outputs/video_unico.mp4", output_name="video_final_tdah.mp4"):
    if not os.path.exists(json_path) or not os.path.exists(video_path):
        print("Error: No se encontró el video base o el JSON.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    pista_narrativa = datos.get("fase_4_pista_narrativa", [])

    CONFIG = {
        "color_texto": "white",
        "color_caja": "black",
        "opacidad_box": 0.7, 
        "font": "assets/fonts/Lexend-VariableFont_wght.ttf",
        "font_size": 48
    }

    print("--- Parche Anti-Solapamiento: Corte Visual Limpio ---")
    
    video_base = VideoFileClip(video_path).with_volume_scaled(0.15)
    duracion_total = video_base.duration
    
    textos_clips = []
    audios_clips = [video_base.audio]

    # TIEMPOS PARA 14 SEGUNDOS
    tiempos = [
        {"inicio": 0, "dur": 4},
        {"inicio": 4, "dur": 4},
        {"inicio": 8, "dur": duracion_total - 8}
    ]

    pos_y_caja = int(video_base.h * 0.65)

    for i, bloque in enumerate(pista_narrativa[:3]):
        fase = bloque["fase"]
        texto = bloque["texto_bimodal"].upper()
        
        # --- A. PROCESAMIENTO DE VOZ (Audio Libre)
        audio_voz_path = f"outputs/audio_{fase.lower()}.mp3"
        if os.path.exists(audio_voz_path):
            voz = AudioFileClip(audio_voz_path).with_start(tiempos[i]["inicio"])
            audios_clips.append(voz)

        # --- B. CORTE DE TEXT
        duracion_estricta_texto = tiempos[i]["dur"] - 0.1

        # --- C. FORMATEO Y CAJA DE TEXTO
        texto_formateado = textwrap.fill(texto, width=22)

        temp_txt = TextClip(
            text=texto_formateado,
            font_size=CONFIG["font_size"],
            color=CONFIG["color_texto"],
            font=CONFIG["font"],
            method='label',
            text_align='center',
            bg_color=CONFIG["color_caja"]
        )

        nuevo_ancho = int(temp_txt.w * 1.25)
        nuevo_alto = int(temp_txt.h * 1.30)

        txt_clip = TextClip(
            text=texto_formateado,
            font_size=CONFIG["font_size"],
            color=CONFIG["color_texto"],
            font=CONFIG["font"],
            method='label',
            text_align='center',
            bg_color=CONFIG["color_caja"],
            size=(nuevo_ancho, nuevo_alto)
        ).with_start(tiempos[i]["inicio"]).with_duration(duracion_estricta_texto).with_opacity(CONFIG["opacidad_box"])

        txt_clip = txt_clip.with_position(('center', pos_y_caja))
        textos_clips.append(txt_clip)

    # 3. MEZCLA FINAL
    audio_final = CompositeAudioClip(audios_clips)
    video_base = video_base.with_audio(audio_final)

    video_final = CompositeVideoClip([video_base] + textos_clips)
    
    print(f"Renderizando video final...")
    video_final.write_videofile(output_name, fps=24, codec="libx264", audio_codec="aac")
    print(f"¡Éxito! El solapamiento de textos ha sido eliminado.")

if __name__ == "__main__":
    ensamblar_video_veo("outputs/evidencia_fases_3_4_storyboard.json")