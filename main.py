from PIL import Image
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os

# Definir la variable ventana globalmente
ventana = None

def seleccionar_plantilla(index, texto1, texto2):
    global plantilla
    global ancho_predeterminado
    global altura_predeterminada

    ruta_script = os.path.abspath(__file__)

    if index == 0:
        plantilla = os.path.join(os.path.dirname(ruta_script), "plantillas", "plantilla0.png")
    elif index == 1:
        plantilla = os.path.join(os.path.dirname(ruta_script), "plantillas", "plantilla1.png")
    elif index == 2:
        plantilla = os.path.join(os.path.dirname(ruta_script), "plantillas", "plantilla2.png")

    texto = entry.get()  # Obtiene el texto del campo de entrada
    if texto:  # Verifica que no esté vacío
        try:
            numero = int(texto1)  # Intenta convertir el texto a un entero
            ancho_predeterminado = numero
        except ValueError:
            messagebox.showerror("Error", "No ingresó un número válido. Se asignará 1000px de ancho.")
    
    texto = entry2.get()  # Obtiene el texto del campo de entrada
    if texto:  # Verifica que no esté vacío
        try:
            numero = int(texto2)  # Intenta convertir el texto a un entero
            altura_predeterminada = numero
        except ValueError:
            messagebox.showerror("Error", "No ingresó un número válido. Se centrará la imagen.")

def recortar_y_redimensionar_imagen(imagen_path, transparentar=True, ancho=1000, umbral=254):
    imagen = Image.open(imagen_path).convert("RGBA")
    bbox = imagen.getbbox()
    imagen = imagen.crop(bbox)
    left, upper, right, lower = imagen.size[0], imagen.size[1], 0, 0

    for y in range(imagen.size[1]):
        for x in range(imagen.size[0]):
            r, g, b, a = imagen.getpixel((x, y))
            if r < umbral or g < umbral or b < umbral:
                left = min(left, x)
                upper = min(upper, y)
                right = max(right, x)
                lower = max(lower, y)

    if left < right and upper < lower:
        bbox = (left, upper, right + 1, lower + 1)
        imagen = imagen.crop(bbox)

    if transparentar:
        data = imagen.getdata()
        nueva_data = [(255, 255, 255, 0) if all(channel >= umbral for channel in item[:3]) else item for item in data]
        imagen.putdata(nueva_data)

    ancho_original, alto_original = imagen.size
    nuevo_ancho = ancho
    nuevo_alto = int((nuevo_ancho / ancho_original) * alto_original)

    if nuevo_alto > 800:
        nuevo_alto = 800
        nuevo_ancho = int((nuevo_alto / alto_original) * ancho_original)

    return imagen.resize((nuevo_ancho, nuevo_alto))


def seleccionar_archivos():
    root = tk.Tk()
    root.withdraw()
    archivos = filedialog.askopenfilenames(title="Seleccionar imágenes a transparentar")
    return list(archivos)

def procesar_imagenes(altura=0):
    archivos_seleccionados = seleccionar_archivos()
    for archivo in archivos_seleccionados:
        moto = recortar_y_redimensionar_imagen(archivo, var.get(), ancho_predeterminado)

        # Cargar la plantilla
        imagen_fondo = Image.open(plantilla)

        # Obtener dimensiones
        ancho_fondo, alto_fondo = imagen_fondo.size
        ancho_superior, alto_superior = moto.size

        # Calcular la posición para centrar la imagen superior
        x = (ancho_fondo - ancho_superior) // 2
        y = (alto_fondo - alto_superior) // 2 + int(altura)

        # Pegar la imagen superior en la imagen de fondo
        imagen_fondo.paste(moto, (x, y), moto)

        # Guardar la imagen resultante
        carpeta_guardado = os.path.dirname(archivo)
        ruta_guardado = os.path.join(carpeta_guardado, "modified_" + os.path.basename(archivo))

        if imagen_fondo.mode == 'RGBA':
            imagen_fondo = imagen_fondo.convert('RGB')

        imagen_fondo.save(ruta_guardado, format='JPEG')
        os.startfile(carpeta_guardado)

    # Reiniciar la ventana
    reiniciar_ventana()

def reiniciar_ventana():
    global ventana, var, entry, entry2, plantilla, ancho_predeterminado, altura_predeterminada

    # Cerrar la ventana actual si existe
    if ventana is not None:
        ventana.destroy()

    # Crear una nueva ventana
    ventana = tk.Tk()
    ventana.title("Seleccione la plantilla")
    ventana.geometry("300x400")

    frame = tk.Frame(ventana)
    frame.pack(expand=True)

    var = tk.BooleanVar(value=1)
    checkbutton = tk.Checkbutton(frame, text="Transparentar", variable=var)
    checkbutton.pack(pady=20)


    ancho_predeterminado = 1000
    # Crear un Label
    label = tk.Label(frame, text="Cambiar ancho (1000px por defecto)")
    label.pack(pady=5)

    # Crear un campo de entrada
    entry = tk.Entry(frame)
    entry.pack(pady=5)

    altura_predeterminada = 0

    # Crear un Label
    label2 = tk.Label(frame, text="Cambiar altura (centro por defecto)")
    label2.pack(pady=5)

    # Crear un campo de entrada
    entry2 = tk.Entry(frame)
    entry2.pack(pady=5)

    # Botones para seleccionar plantilla
    nombres_botones = ['Sin Bonificación', 'Casco de regalo', 'Casco + Linga de regalo']
    for index, nombre in enumerate(nombres_botones):
        boton = tk.Button(frame, text=nombre, command=lambda i=index: seleccionar_plantilla(i, entry.get(), entry2.get()))
        boton.pack(pady=5)

    # Botón para procesar imágenes
    boton_procesar = tk.Button(frame, text="Procesar Imágenes", command= lambda: procesar_imagenes(altura_predeterminada))
    boton_procesar.pack(pady=20)

    ventana.mainloop()

# Inicializar la ventana
reiniciar_ventana()