# Trabajo Práctico Interfaz Hombre Máquina
## Generación de contenido audiovisual para personas con TDAH

El proyecto implementa una arquitectura híbrida en la cual lee el contenido dispuesto por el usuario en la carpeta Assets para recolectar la información más importante de esta. En base a lo obtenido, genera "ganchos" para retener al espectador y darle el mensaje deseado.

### Archivos ya generados
Este proyecto cuenta con los archivos ya generados de la ejecución en la que se hace entrega.
* [Acceder a el vídeo final generado](./video_final_tdah.mp4)
* [Acceder al documento teórico con las consideraciones y la ejecución](./TP1_IHM_Gotte_Murguia.pdf)
* Los archivos de las distintas fases se pueden acceder en la carpeta [outputs](./outputs)

### Pasos para ejecutar el proyecto
1. Activar entorno virtual
    ```bash
    source venv/bin/activate
    ```
2. Instalar librerias
    ```bash
    pip install PyPDF2 beautifulsoup4 python-docx groq python-dotenv edge-tts moviepy numpy scipy
    ```

3. Ejecutar
    ```bash
    python3 main.py
    ```

4. El resultado se obtiene en la carpeta "outputs", donde se obtienen:
    * Los **datos crudos** generados por el modelo en **JSON** (archivos "evidencia_fases_1_2.JSON" y "evidencia_fases_3_4_storyboard.JSON"). 
    * Los **archivos de texto** ("prompts_keyframes.txt" y "prompts_video.txt") que contienen los **prompts** para que el usuario haga uso de herramientas externas como ElevenLabs o Google Flow para la generación de las imágenes "keyframes" de referencia y luego el vídeo.

5. Colocar el vídeo obtenido resultante de la plataforma con el nombre "video_unico.mp4" en la carpeta "outputs". 

6. Ejecutar el comando para insertar los audios de voz generados, colocar el texto en pantalla y obtener el resultado final. El resultado queda guardado en la raíz del proyecto con el nombre "video_final_tdah.mp4"
    ```bash
    python3 ensamblador.py
    ```
