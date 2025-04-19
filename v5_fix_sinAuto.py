#!/usr/bin/env python3
import os
import subprocess
import markdown2
import pdfkit
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
from threading import Thread
from PIL import Image, ImageTk
import getpass
import shutil
import re

# Variables globales
txt_file = md_file = html_file = pdf_file = timestamp = output_dir = ""
modo_oscuro = False
imagen_label = None
imagen_actual = None
ruta_personalizada = None
entry_ruta = None
ultima_ruta_guardada = None
entry_nombre = None
var_lynis = None

# Funciones auxiliares
def ejecutar_comando(comando):
    try:
        return subprocess.check_output(comando, shell=True, stderr=subprocess.STDOUT, universal_newlines=True).strip()
    except subprocess.CalledProcessError as e:
        return f"[ERROR]: {e.output.strip()}"

#* Para limpiar la salida de la aplicacion de LYNIS
def limpiar_ansi(texto):
    ansi_escape = re.compile(r'(\x1B\[[0-9;]*[mK])')
    return ansi_escape.sub('', texto)

def formatear_lista(salida_raw):
    return '\n'.join([f"\u2022 {linea.strip()}" for linea in salida_raw.splitlines() if linea.strip()])

def obtener_ruta_escritorio(usuario):
    user_home = os.path.expanduser(f"~{usuario}")
    xdg_file = os.path.join(user_home, ".config/user-dirs.dirs")
    if os.path.exists(xdg_file):
        try:
            with open(xdg_file, "r") as f:
                for line in f:
                    if line.startswith("XDG_DESKTOP_DIR"):
                        ruta = line.split("=")[1].strip().strip('"').replace("$HOME", user_home)
                        if os.path.exists(ruta):
                            return ruta
        except:
            pass
    posibles = [os.path.join(user_home, carpeta) for carpeta in ["Escritorio", "Desktop"]]
    for ruta in posibles:
        if os.path.exists(ruta):
            return ruta
    return user_home

def comprobar_o_instalar_lynis():
    if shutil.which("lynis") is None:
        respuesta = messagebox.askyesno("Lynis no encontrado", "Lynis no está instalado. ¿Deseas instalarlo automáticamente?")
        if respuesta:
            instalar = ejecutar_comando("sudo apt update && sudo apt install -y lynis")
            ventana.lift()
            ventana.attributes('-topmost', True)
            messagebox.showinfo("Instalación completa", "Lynis ha sido instalado correctamente. Pulse OK para ejecutar el comando y insertarlo en el informe")
            ventana.attributes('-topmost', False)
        else:
            ventana.lift()
            ventana.attributes('-topmost', True)
            messagebox.showwarning("Lynis requerido", "No se incluirá el análisis Lynis.")
            ventana.attributes('-topmost', False)

def generar_contenido_txt():
    contenido = []
    def log(seccion, comando, como_lista=False, limpiar=False):
        resultado = ejecutar_comando(comando)
        if limpiar:
            resultado = limpiar_ansi(resultado)
        bloque = f"\n==================== {seccion} ====================\n"
        bloque += formatear_lista(resultado) + "\n" if como_lista else resultado + "\n"
        contenido.append(bloque)

    log("INFORMACION DEL SISTEMA", "uname -a")
    log("DISTRIBUCION", "cat /etc/os-release")
    log("UPTIME", "uptime")
    log("FECHA Y HORA", "date")
    log("VARIABLES DE ENTORNO", "printenv", como_lista=True)
    log("CONFIGURACION DE CIFRADO DE DISCO", "sudo cat /etc/crypttab", como_lista=True)

    log("CPU", "lscpu")
    log("MEMORIA RAM", "free -h")
    log("DISCOS", "lsblk -o NAME,SIZE,TYPE,MOUNTPOINT", como_lista=True)
    log("ESPACIO EN DISCO", "df -h")

    log("INTERFACES DE RED", "ip -brief address", como_lista=True)
    log("INTERFACES EN PROMISCUO", "ip link | grep PROMISC", como_lista=True)
    log("RUTA POR DEFECTO", "ip route show")
    log("RUTAS DE RED", "ip route show table all")
    log("SERVIDORES DNS", "cat /etc/resolv.conf")
    log("PUERTOS ESCUCHANDO", "ss -tulnp")
    log("PROCESOS CON CONEXION", "ss -plntu")

    log("USUARIOS DEL SISTEMA", "cut -d: -f1 /etc/passwd", como_lista=True)
    log("USUARIOS CON SHELL ACTIVA", "grep -v '/usr/sbin/nologin' /etc/passwd | cut -d: -f1", como_lista=True)
    log("USUARIOS EN GRUPO SUDO", "getent group sudo")
    log("GRUPOS DEL SISTEMA", "cut -d: -f1 /etc/group", como_lista=True)
    log("CONFIGURACION DE SUDO", "sudo -l -U $(whoami)")

    log("LOG DE AUTENTICACION", "grep -i 'authentication' /var/log/auth.log | tail -n 20", como_lista=True)
    log("FALLOS DE LOGIN", "grep 'Failed password' /var/log/auth.log | tail -n 10")
    log("ULTIMOS INICIOS DE SESION", "last -n 10", como_lista=True)

    log("HISTORIAL DE COMANDOS DEL USUARIO", "tail -n 20 ~/.bash_history")
    log("HISTORIAL DE COMANDOS EJECUTADOS POR ROOT", "sudo tail -n 20 /root/.bash_history")

    log("PROCESOS EN EJECUCION (TOP 15)", "ps aux --sort=-%mem | head -n 15", como_lista=True)
    log("SERVICIOS ACTIVOS", "systemctl list-units --type=service --state=running | grep '.service'", como_lista=True)

    for archivo in ["/etc/passwd", "/etc/shadow", "/etc/sudoers"]:
        if os.path.exists(archivo):
            permisos = ejecutar_comando(f"ls -l {archivo}")
            contenido.append(f"\n==================== PERMISOS DE {archivo} ====================\n{permisos}\n")

    if var_lynis.get():
        comprobar_o_instalar_lynis()
        contenido.append("\n==================== RESULTADO DE LYNIS ====================\n")
        resultado_lynis = ejecutar_comando("sudo lynis audit system")
        resultado_limpio = limpiar_ansi(resultado_lynis)
        contenido.append(resultado_limpio + "\n")

    return "".join(contenido)

# ========== PREPARACIÓN SIN CREAR CARPETA ==========
def preparar_exportacion():
    messagebox.showinfo("Auditoría preparada", "Datos listos. Ahora selecciona los formatos.")
    mostrar_opciones_exportacion()

# ========== INICIAR PROCESO ==========
def iniciar_proceso():
    Thread(target=preparar_exportacion).start()

# ========== APLICAR TEMA ==========
def aplicar_tema(widget):
    colores = {
        "fondo": "#2E2E2E" if modo_oscuro else "#FFFFFF",
        "texto": "#FFFFFF" if modo_oscuro else "#000000",
        "boton": "#4CAF50" if not modo_oscuro else "#3E8E41"
    }
    widget.configure(bg=colores["fondo"])
    for child in widget.winfo_children():
        try:
            if isinstance(child, tk.Checkbutton):
                child.configure(bg=colores["fondo"], fg=colores["texto"], selectcolor=colores["fondo"])
            else:
                child.configure(bg=colores["fondo"], fg=colores["texto"])
        except:
            pass
    actualizar_imagen()

# ========== ACTUALIZAR IMAGEN ==========
def actualizar_imagen():
    global imagen_actual
    ruta = "img/white.png" if modo_oscuro else "img/black.png"
    if os.path.exists(ruta):
        imagen = Image.open(ruta)
        imagen = imagen.resize((240, 240))
        imagen_actual = ImageTk.PhotoImage(imagen)
        imagen_label.config(image=imagen_actual)

# ========== MOSTRAR OPCIONES ==========
def mostrar_opciones_exportacion():
    global ventana_opciones, var_txt, var_md, var_html, var_pdf, entry_ruta, entry_nombre, var_lynis

    ventana_opciones = tk.Toplevel(ventana)
    ventana_opciones.title("Exportar informe")
    centrar_ventana(ventana_opciones, 600, 700)

    var_txt = tk.BooleanVar()
    var_md = tk.BooleanVar()
    var_html = tk.BooleanVar()
    var_pdf = tk.BooleanVar()
    var_lynis = tk.BooleanVar()

    tk.Label(ventana_opciones, text="Selecciona los formatos para exportar:").pack(pady=10)
    tk.Checkbutton(ventana_opciones, text="TXT", variable=var_txt).pack(anchor='w', padx=40)
    tk.Checkbutton(ventana_opciones, text="Markdown (.md)", variable=var_md).pack(anchor='w', padx=40)
    tk.Checkbutton(ventana_opciones, text="HTML (.html)", variable=var_html).pack(anchor='w', padx=40)
    tk.Checkbutton(ventana_opciones, text="PDF (.pdf)", variable=var_pdf).pack(anchor='w', padx=40)

    frame_lynis = tk.Frame(ventana_opciones)
    tk.Checkbutton(frame_lynis, text="Incluir auditoría Lynis", variable=var_lynis).pack(side="left", padx=(40, 5))
    label_info = tk.Label(frame_lynis, text="(?)", fg="blue", cursor="question_arrow")
    label_info.pack(side="left")

    def mostrar_tooltip(event):
        messagebox.showinfo("Lynis", "Lynis es una herramienta de auditoría de seguridad para sistemas Unix.\nSe ejecuta con privilegios y revisa configuraciones del sistema, debilidades y medidas de seguridad.")

    label_info.bind("<Button-1>", mostrar_tooltip)
    frame_lynis.pack(pady=10)

    tk.Label(ventana_opciones, text="Nombre y Apellidos:").pack(pady=(20, 5))
    entry_nombre = tk.Entry(ventana_opciones, width=50)
    entry_nombre.pack(pady=5)

    tk.Label(ventana_opciones, text="Ruta para guardar el informe:").pack(pady=(20, 5))
    frame_ruta = tk.Frame(ventana_opciones)
    entry_ruta = tk.Entry(frame_ruta, width=45)
    usuario_real = os.environ.get("SUDO_USER") or getpass.getuser()
    ruta_escritorio = obtener_ruta_escritorio(usuario_real)
    ruta_inicial = ultima_ruta_guardada if ultima_ruta_guardada else ruta_escritorio
    entry_ruta.insert(0, ruta_inicial)
    entry_ruta.pack(side="left", padx=(0, 5))

    def seleccionar_directorio():
        ruta = filedialog.askdirectory()
        if ruta:
            entry_ruta.delete(0, tk.END)
            entry_ruta.insert(0, ruta)

    boton_explorar = tk.Button(frame_ruta, text="📁", command=seleccionar_directorio)
    boton_explorar.pack(side="right")

    frame_ruta.pack(pady=5)
    tk.Button(ventana_opciones, text="Exportar", command=exportar_formatos).pack(pady=20)
    aplicar_tema(ventana_opciones)

# ========== CENTRAR VENTANA ==========
def centrar_ventana(ventana, ancho, alto):
    ventana.update_idletasks()
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

# ========== CAMBIAR TEMA ==========
def cambiar_tema():
    global modo_oscuro
    modo_oscuro = not modo_oscuro
    aplicar_tema(ventana)

    # ========== EXPORTAR FORMATOS ==========
def exportar_formatos():
    global txt_file, md_file, html_file, pdf_file, output_dir, ultima_ruta_guardada, timestamp

    if not any([var_txt.get(), var_md.get(), var_html.get(), var_pdf.get()]):
        messagebox.showwarning("Nada seleccionado", "Debes seleccionar al menos un formato.")
        return

    if var_pdf.get() and not var_html.get():
        messagebox.showwarning("Dependencia HTML", "Para generar un PDF primero debes generar también el HTML.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_ruta = entry_ruta.get().strip()
    nombre = entry_nombre.get().strip()
    if not nombre:
        nombre = "No especificado"

    if not base_ruta:
        messagebox.showwarning("Ruta no válida", "Debes indicar una ruta de destino.")
        return

    base_ruta = os.path.expanduser(base_ruta)
    output_dir = os.path.join(base_ruta, f"auditoria_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    ultima_ruta_guardada = base_ruta

    txt_file = os.path.join(output_dir, "reporte.txt")
    md_file = os.path.join(output_dir, "reporte.md")
    html_file = os.path.join(output_dir, "reporte.html")
    pdf_file = os.path.join(output_dir, "reporte.pdf")

    seleccionados = []
    contenido_txt = None

    for ruta, variable in [(txt_file, var_txt), (md_file, var_md), (html_file, var_html), (pdf_file, var_pdf)]:
        if not variable.get() and os.path.exists(ruta):
            try:
                os.remove(ruta)
            except:
                pass

    if var_txt.get():
        contenido_txt = generar_contenido_txt()
        with open(txt_file, "w") as f:
            f.write(f"Nombre y Apellidos: {nombre}\n")
            f.write(f"Fecha de generación: {timestamp}\n\n")
            f.write(contenido_txt)
        seleccionados.append("TXT")

    if var_md.get():
        if not contenido_txt:
            contenido_txt = generar_contenido_txt()
        with open(md_file, "w") as f_md:
            f_md.write(f"# Informe de Auditoría del Sistema Linux\n\n")
            f_md.write(f"**Nombre y Apellidos:** {nombre}\n\n")
            f_md.write(f"**Fecha de generación:** {timestamp}\n\n___\n\n")
            for linea in contenido_txt.splitlines():
                if "=====" in linea:
                    f_md.write(f"\n\n## {linea.strip('= ')}\n")
                elif linea.startswith("\u2022"):
                    f_md.write(f"- {linea[1:].strip()}\n")
                else:
                    f_md.write(f"    {linea}\n")
        seleccionados.append("Markdown")

    if var_html.get():
        if not contenido_txt:
            contenido_txt = generar_contenido_txt()
        html_contenido = f"# Informe de Auditoría del Sistema Linux\n\n**Nombre y Apellidos:** {nombre}\n\n**Fecha de generación:** {timestamp}\n\n___\n\n"
        for linea in contenido_txt.splitlines():
            if "=====" in linea:
                html_contenido += f"\n\n## {linea.strip('= ')}\n"
            elif linea.startswith("\u2022"):
                html_contenido += f"- {linea[1:].strip()}\n"
            else:
                html_contenido += f"    {linea}\n"
        html_convertido = markdown2.markdown(html_contenido)
        with open(html_file, "w") as f_html:
            f_html.write(f"""<!DOCTYPE html><html><head><meta charset='utf-8'><title>Informe</title>
            <style>body {{ font-family: Arial; font-size: 20px; margin: 40px; background:#f9f9f9; }} h1,h2 {{ color:#2c3e50; }}</style></head>
            <body>{html_convertido}</body></html>""")
        seleccionados.append("HTML")

    if var_pdf.get():
        if os.path.exists(html_file):
            try:
                pdfkit.from_file(html_file, pdf_file)
                seleccionados.append("PDF")
            except Exception as e:
                messagebox.showerror("Error al generar PDF", str(e))
        else:
            messagebox.showwarning("PDF no generado", "El PDF no se puede generar sin antes crear HTML.")

    if seleccionados:
        resumen = "Se han generado los siguientes archivos:\n\n" + "\n".join(f"• {f}" for f in seleccionados)
        resumen += f"\n\nUbicación:\n{output_dir}"

    usuario_real = os.environ.get("SUDO_USER") or getpass.getuser()
    try:
        for archivo in [txt_file, md_file, html_file, pdf_file]:
            if os.path.exists(archivo):
                shutil.chown(archivo, user=usuario_real)
        for root_dir, dirs, files in os.walk(output_dir):
            shutil.chown(root_dir, user=usuario_real)
            for d in dirs:
                shutil.chown(os.path.join(root_dir, d), user=usuario_real)
            for f in files:
                shutil.chown(os.path.join(root_dir, f), user=usuario_real)
    except Exception as e:
        print(f"[ADVERTENCIA] No se pudieron cambiar los permisos: {e}")

    ventana.lift()
    ventana.attributes('-topmost', True)
    messagebox.showinfo("Exportación completada", resumen)
    ventana.attributes('-topmost', False)
    ventana_opciones.destroy()

# ========== VENTANA PRINCIPAL ==========
ventana = tk.Tk()
ventana.title("Herramienta de Auditoría Linux")
centrar_ventana(ventana, 600, 600)

label_titulo = tk.Label(ventana, text="Auditoría del Sistema Linux", font=("Helvetica", 16, "bold"))
label_titulo.pack(pady=(20, 10))

imagen_label = tk.Label(ventana)
imagen_label.pack(pady=(0, 20))

label_info = tk.Label(ventana, text="Haz clic en el botón para iniciar la recopilación.")
label_info.pack()

boton_iniciar = tk.Button(ventana, text="Iniciar Auditoría", command=iniciar_proceso,
                          font=("Helvetica", 12), bg="#4CAF50", fg="white")
boton_iniciar.pack(pady=15)

boton_tema = tk.Button(ventana, text="Cambiar Tema (Claro/Oscuro)", command=cambiar_tema,
                       font=("Helvetica", 10))
boton_tema.pack()

aplicar_tema(ventana)
ventana.mainloop()
