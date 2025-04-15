#!/usr/bin/env python3
import os
import subprocess
import markdown2
import pdfkit
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from threading import Thread
from PIL import Image, ImageTk

# Variables globales
txt_file = md_file = html_file = pdf_file = timestamp = output_dir = ""
modo_oscuro = False
imagen_label = None
imagen_actual = None

# ========== FUNCIONES BÁSICAS ==========
def ejecutar_comando(comando):
    try:
        return subprocess.check_output(comando, shell=True, stderr=subprocess.STDOUT, universal_newlines=True).strip()
    except subprocess.CalledProcessError as e:
        return f"[ERROR]: {e.output.strip()}"

def formatear_lista(salida_raw):
    return '\n'.join([f"• {linea.strip()}" for linea in salida_raw.splitlines() if linea.strip()])

def generar_contenido_txt():
    contenido = []
    def log(seccion, comando, como_lista=False):
        resultado = ejecutar_comando(comando)
        bloque = f"\n==================== {seccion} ====================\n"
        bloque += formatear_lista(resultado) + "\n" if como_lista else resultado + "\n"
        contenido.append(bloque)
    
        # ========== INFORMACIÓN GENERAL DEL SISTEMA ==========
    log("INFORMACIÓN DEL SISTEMA", "uname -a")
    log("DISTRIBUCIÓN", "cat /etc/os-release")
    log("UPTIME", "uptime")
    log("FECHA Y HORA", "date")
    log("VARIABLES DE ENTORNO", "printenv", como_lista=True)
    log("CONFIGURACIÓN DE CIFRADO DE DISCO", "sudo cat /etc/crypttab", como_lista=True)


    # ========== HARDWARE ==========
    log("CPU", "lscpu")
    log("MEMORIA RAM", "free -h")
    log("DISCOS", "lsblk -o NAME,SIZE,TYPE,MOUNTPOINT", como_lista=True)
    log("ESPACIO EN DISCO", "df -h")

    # ========== RED ==========
    log("INTERFACES DE RED", "ip -brief address", como_lista=True)
    log("INTERFACES EN PROMISCUO", "ip link | grep PROMISC", como_lista=True)
    log("RUTA POR DEFECTO", "ip route show")
    log("RUTAS DE RED", "ip route show table all")
    log("SERVIDORES DNS", "cat /etc/resolv.conf")
    log("PUERTOS ESCUCHANDO", "ss -tulnp")
    log("PROCESOS CON CONEXIÓN", "ss -plntu")

    # ========== USUARIOS Y GRUPOS ==========
    log("USUARIOS DEL SISTEMA", "cut -d: -f1 /etc/passwd", como_lista=True)
    log("USUARIOS CON SHELL ACTIVA", "grep -v '/usr/sbin/nologin' /etc/passwd | cut -d: -f1", como_lista=True)
    log("USUARIOS EN GRUPO SUDO", "getent group sudo")
    log("GRUPOS DEL SISTEMA", "cut -d: -f1 /etc/group", como_lista=True)
    log("CONFIGURACIÓN DE SUDO", "sudo -l -U $(whoami)")

    # ========== SEGURIDAD Y AUTENTICACIÓN ==========
    log("LOG DE AUTENTICACIÓN", "grep -i 'authentication' /var/log/auth.log | tail -n 20", como_lista=True)
    log("FALLOS DE LOGIN", "grep 'Failed password' /var/log/auth.log | tail -n 10")
    log("ÚLTIMOS INICIOS DE SESIÓN", "last -n 10", como_lista=True)

    # ========== HISTORIAL DE COMANDOS ==========
    log("HISTORIAL DE COMANDOS DEL USUARIO", "tail -n 20 ~/.bash_history")
    log("HISTORIAL DE COMANDOS EJECUTADOS POR ROOT", "sudo tail -n 20 /root/.bash_history")

    # ========== PROCESOS Y SERVICIOS ==========
    log("PROCESOS EN EJECUCIÓN (TOP 15)", "ps aux --sort=-%mem | head -n 15", como_lista=True)
    log("SERVICIOS ACTIVOS", "systemctl list-units --type=service --state=running | grep '.service'", como_lista=True)


    for archivo in ["/etc/passwd", "/etc/shadow", "/etc/sudoers"]:
        if os.path.exists(archivo):
            permisos = ejecutar_comando(f"ls -l {archivo}")
            contenido.append(f"\n==================== PERMISOS DE {archivo} ====================\n{permisos}\n")

    return "".join(contenido)

# ========== EXPORTACIÓN ==========
def exportar_formatos():
    seleccionados = []
    contenido_txt = None
    if not any([var_txt.get(), var_md.get(), var_html.get(), var_pdf.get()]):
        messagebox.showwarning("Nada seleccionado", "Debes seleccionar al menos un formato.")
        return

    for ruta, variable in [(txt_file, var_txt), (md_file, var_md), (html_file, var_html), (pdf_file, var_pdf)]:
        if not variable.get() and os.path.exists(ruta):
            try: os.remove(ruta)
            except: pass

    if var_txt.get():
        contenido_txt = generar_contenido_txt()
        with open(txt_file, "w") as f: f.write(contenido_txt)
        seleccionados.append("TXT")

    if var_md.get():
        if not contenido_txt: contenido_txt = generar_contenido_txt()
        with open(md_file, "w") as f_md:
            f_md.write(f"# Informe de Auditoría del Sistema Linux\n\n**Fecha de generación:** {timestamp}\n\n___\n\n")
            for linea in contenido_txt.splitlines():
                if "=====" in linea: f_md.write(f"\n\n## {linea.strip('= ')}\n")
                elif linea.startswith("•"): f_md.write(f"- {linea[1:].strip()}\n")
                else: f_md.write(f"    {linea}\n")
        seleccionados.append("Markdown")

    if var_html.get():
        if not contenido_txt: contenido_txt = generar_contenido_txt()
        html_contenido = f"# Informe de Auditoría del Sistema Linux\n\n**Fecha de generación:** {timestamp}\n\n___\n\n"
        for linea in contenido_txt.splitlines():
            if "=====" in linea: html_contenido += f"\n\n## {linea.strip('= ')}\n"
            elif linea.startswith("•"): html_contenido += f"- {linea[1:].strip()}\n"
            else: html_contenido += f"    {linea}\n"
        html_convertido = markdown2.markdown(html_contenido)
        with open(html_file, "w") as f_html:
            f_html.write(f"""<!DOCTYPE html><html><head><meta charset='utf-8'><title>Informe</title>
            <style>body {{ font-family: Arial; margin: 40px; background:#f9f9f9; }} h1,h2 {{ color:#2c3e50; }}</style></head>
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
        messagebox.showinfo("Exportación completada", resumen)
        ventana_opciones.destroy()

# ========== GUI ==========
def aplicar_tema(widget):
    colores = {
        "fondo": "#2E2E2E" if modo_oscuro else "#FFFFFF",
        "texto": "#FFFFFF" if modo_oscuro else "#000000",
        "boton": "#4CAF50" if not modo_oscuro else "#3E8E41"
    }
    widget.configure(bg=colores["fondo"])
    for child in widget.winfo_children():
        try:
            child.configure(bg=colores["fondo"], fg=colores["texto"])
        except:
            pass
    actualizar_imagen()

def actualizar_imagen():
    global imagen_actual
    ruta = "img/white.png" if modo_oscuro else "img/black.png"
    if os.path.exists(ruta):
        imagen = Image.open(ruta)
        imagen = imagen.resize((240, 240))
        imagen_actual = ImageTk.PhotoImage(imagen)
        imagen_label.config(image=imagen_actual)

def mostrar_opciones_exportacion():
    global ventana_opciones, var_txt, var_md, var_html, var_pdf

    ventana_opciones = tk.Toplevel(ventana)
    ventana_opciones.title("Exportar informe")
    ventana_opciones.geometry("400x300")

    var_txt = tk.BooleanVar()
    var_md = tk.BooleanVar()
    var_html = tk.BooleanVar()
    var_pdf = tk.BooleanVar()

    tk.Label(ventana_opciones, text="Selecciona los formatos para exportar:").pack(pady=10)
    tk.Checkbutton(ventana_opciones, text="TXT", variable=var_txt).pack(anchor='w', padx=40)
    tk.Checkbutton(ventana_opciones, text="Markdown (.md)", variable=var_md).pack(anchor='w', padx=40)
    tk.Checkbutton(ventana_opciones, text="HTML (.html)", variable=var_html).pack(anchor='w', padx=40)
    tk.Checkbutton(ventana_opciones, text="PDF (.pdf)", variable=var_pdf).pack(anchor='w', padx=40)

    tk.Button(ventana_opciones, text="Exportar", command=exportar_formatos).pack(pady=20)
    aplicar_tema(ventana_opciones)

def preparar_exportacion():
    global txt_file, md_file, html_file, pdf_file, timestamp, output_dir
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.expanduser(f"~/auditoria_linux_final/auditoria_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    txt_file = os.path.join(output_dir, "reporte.txt")
    md_file = os.path.join(output_dir, "reporte.md")
    html_file = os.path.join(output_dir, "reporte.html")
    pdf_file = os.path.join(output_dir, "reporte.pdf")

    messagebox.showinfo("Auditoría preparada", "Datos listos. Ahora selecciona los formatos.")
    mostrar_opciones_exportacion()

def iniciar_proceso():
    Thread(target=preparar_exportacion).start()

def cambiar_tema():
    global modo_oscuro
    modo_oscuro = not modo_oscuro
    aplicar_tema(ventana)

# ========== VENTANA PRINCIPAL ==========
ventana = tk.Tk()
ventana.title("Herramienta de Auditoría Linux")
ventana.geometry("600x600")

tk.Label(ventana, text="Auditoría del Sistema Linux", font=("Helvetica", 16, "bold")).pack(pady=(20, 10))

imagen_label = tk.Label(ventana)
imagen_label.pack(pady=(0, 20))

tk.Label(ventana, text="Haz clic en el botón para iniciar la recopilación.").pack()

tk.Button(ventana, text="Iniciar Auditoría", command=iniciar_proceso,
          font=("Helvetica", 12), bg="#4CAF50", fg="white").pack(pady=15)

tk.Button(ventana, text="Cambiar Tema (Claro/Oscuro)", command=cambiar_tema,
          font=("Helvetica", 10)).pack()

aplicar_tema(ventana)
ventana.mainloop()

