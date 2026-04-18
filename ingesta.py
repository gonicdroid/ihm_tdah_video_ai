import os
import base64
from bs4 import BeautifulSoup
import PyPDF2
import docx
from groq import Groq
from dotenv import load_dotenv

# Cargar variables de entorno (necesitamos la API KEY para el OCR en la nube)
load_dotenv()

class ExtractorDocumental:
    """Módulo responsable de extraer texto plano 100% en Python, compatible con Windows/Linux/Mac."""
    
    def __init__(self):
        # Mapeo de extensiones a sus funciones de extracción
        self.estrategias = {
            '.txt': self._extraer_txt,
            '.html': self._extraer_html,
            '.pdf': self._extraer_pdf,
            '.docx': self._extraer_docx,
            '.png': self._extraer_imagen,
            '.jpg': self._extraer_imagen,
            '.jpeg': self._extraer_imagen
        }
        # Cliente Groq para usar el modelo de visión como OCR
        self.cliente_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def procesar_directorio(self, ruta_directorio: str) -> str:
        """Lee todos los archivos soportados en un directorio y consolida el texto."""
        texto_consolidado = ""
        
        if not os.path.exists(ruta_directorio):
            print(f"Error: El directorio '{ruta_directorio}' no existe.")
            return ""

        for archivo in sorted(os.listdir(ruta_directorio)):
            ruta_completa = os.path.join(ruta_directorio, archivo)
            if os.path.isfile(ruta_completa):
                extension = os.path.splitext(archivo)[1].lower()
                if extension in self.estrategias:
                    print(f"[INGESTA] Extrayendo datos de: {archivo}...")
                    try:
                        texto_extraido = self.estrategias[extension](ruta_completa)
                        texto_consolidado += f"\n\n--- INICIO DE {archivo} ---\n"
                        texto_consolidado += texto_extraido.strip()
                        texto_consolidado += f"\n--- FIN DE {archivo} ---\n"
                    except Exception as e:
                        print(f"  [!] Error al leer {archivo}: {e}")
                else:
                    print(f"[INGESTA] Saltando {archivo} (Formato no soportado)")
                    
        return texto_consolidado

    # --- ESTRATEGIAS DE EXTRACCIÓN (Puro Python) ---

    def _extraer_txt(self, ruta: str) -> str:
        with open(ruta, 'r', encoding='utf-8') as f:
            return f.read()

    def _extraer_html(self, ruta: str) -> str:
        """Limpia etiquetas HTML usando BeautifulSoup para ahorrar tokens."""
        with open(ruta, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            # Eliminar scripts y estilos ocultos
            for script in soup(["script", "style"]):
                script.extract()
            return soup.get_text(separator=' ', strip=True)

    def _extraer_pdf(self, ruta: str) -> str:
        """Lee PDFs usando PyPDF2."""
        texto = ""
        with open(ruta, 'rb') as f:
            lector = PyPDF2.PdfReader(f)
            for pagina in lector.pages:
                extraido = pagina.extract_text()
                if extraido:
                    texto += extraido + " "
        return texto

    def _extraer_docx(self, ruta: str) -> str:
        """Lee archivos DOCX usando python-docx."""
        doc = docx.Document(ruta)
        return "\n".join([parrafo.text for parrafo in doc.paragraphs])

    def _extraer_imagen(self, ruta: str) -> str:
        """Usa el modelo Llama 3.2 Vision de Groq como motor OCR en la nube."""
        print("  -> Aplicando OCR en la nube (Groq Vision)...")
        with open(ruta, "rb") as image_file:
            imagen_b64 = base64.b64encode(image_file.read()).decode('utf-8')
            
        respuesta = self.cliente_groq.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extrae todo el texto legible de esta imagen. Devuelve SOLO el texto plano, sin comentarios ni explicaciones adicionales."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{imagen_b64}",
                            }
                        }
                    ]
                }
            ],
            temperature=0.0, # Temperatura 0 para evitar que la IA invente cosas en la imagen
        )
        return respuesta.choices[0].message.content

# Prueba independiente del módulo
if __name__ == "__main__":
    extractor = ExtractorDocumental()
    texto = extractor.procesar_directorio("assets")
    print(f"\nResumen: Se extrajeron {len(texto)} caracteres en total.")