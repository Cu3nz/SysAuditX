#!/usr/bin/env python3
import os
import subprocess
import markdown2
import pdfkit
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, filedialog
from threading import Thread
from PIL import Image, ImageTk
import getpass
import shutil
import re
import socket
from datetime import datetime
#* Para enviar el correo 
import smtplib
from email.message import EmailMessage

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
entry_correo= None


def ejecutar_comando(comando):
    try:
        return subprocess.check_output(comando, shell=True, stderr=subprocess.STDOUT, universal_newlines=True).strip()
    except subprocess.CalledProcessError as e:
        return f"[ERROR]: {e.output.strip()}"

#* Para limpiar la salida de la aplicacion de LYNIS
def limpiar_ansi(texto):
    ansi_escape = re.compile(r'(\x1B\[[0-9;]*[mK])')
    return ansi_escape.sub('', texto)

def obtener_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except Exception as e:
        return f"[ERROR]: No se pudo obtener la IP local: {e}"

def obtener_interfaz_por_ip(ip_local):
    try:
        resultado = subprocess.check_output("ip -o -4 addr show", shell=True, text=True)
        for linea in resultado.splitlines():
            partes = linea.split()
            interfaz = partes[1]
            ip = partes[3].split('/')[0]
            if ip == ip_local:
                return interfaz
        return None
    except Exception as e:
        print(f"[ERROR] No se pudo obtener la interfaz de red: {e}")
        return None

def formatear_lista(salida_raw):
    return '\n'.join([f"\u2022 {linea.strip()}" for linea in salida_raw.splitlines() if linea.strip()])

def mostrar_ayuda_exportacion():
    ventana_ayuda = tk.Toplevel(ventana_opciones)
    ventana_ayuda.title("Ayuda - Exportación de Informe")
    ventana_ayuda.geometry("700x400")
    ventana_ayuda.resizable(False, False)

    # Centrar la ventana
    centrar_ventana(ventana_ayuda, 700, 500)

    
    frame_texto = tk.Frame(ventana_ayuda)
    frame_texto.pack(expand=True, fill="both", padx=10, pady=10)

    scroll = tk.Scrollbar(frame_texto)
    scroll.pack(side="right", fill="y")

    cuadro_texto = tk.Text(frame_texto, wrap="word", yscrollcommand=scroll.set, bg="white", fg="black", font=("Arial", 12))
    scroll.config(command=cuadro_texto.yview)

    texto = (
        "📄 FORMATOS DE EXPORTACIÓN:\n\n"
        "- La herramienta permite generar informes en uno o varios de los siguientes formatos: TXT, Markdown (.md), HTML y PDF.\n\n"
        "- Cada formato puede seleccionarse de forma individual mediante las casillas correspondientes.\n\n"
        "- Para exportar en formato PDF, es imprescindible seleccionar también el formato HTML, ya que el PDF se genera a partir de este contenido.\n\n"
        "- Todos los archivos se almacenarán automáticamente en una carpeta con fecha y hora, para facilitar su identificación y organización.\n\n"


        "📧 CORREO ELECTRÓNICO:\n\n"
        "- Se puede introducir uno o varios correos electrónicos en el campo correspondiente.\n\n"
        "- Los correos deben ir separados exclusivamente por comas (,).\n\n"
        "- Si se introduce cualquier carácter de separación incorrecto (como punto y coma, -, / , [ , ], etc.), se mostrará un mensaje que indicará:\n\n"
        "   • El o los caracteres erróneos detectados.\n\n"
        "   • La línea exacta donde se ha producido el error.\n\n"
        "- Además, si alguno de los correos no está correctamente formateado (por ejemplo, falta la '@' o el dominio), se mostrará una advertencia específica del correo mal formateado.\n\n"
        "- Ejemplo válido:\n\n"
        "   persona1@mail.com,persona2@mail.com\n\n"


        "🛠 LYNIS:\n\n"
        "- Lynis es una herramienta avanzada de auditoría de seguridad para sistemas Unix/Linux.\n\n"
        "- Su propósito es evaluar el estado de seguridad del sistema mediante un escaneo completo que revisa configuraciones, servicios activos, permisos, módulos del kernel, herramientas de red, contraseñas, autenticación, firewall, servicios web, entre otros.\n\n"
        "- Lynis requiere permisos de superusuario (`sudo`) para realizar un análisis completo y acceder a todos los componentes clave del sistema.\n\n"
        "- Durante el análisis, Lynis también comprueba si tienes instaladas determinadas herramientas o configuraciones recomendadas. Si alguna no está presente, lo indica como “Not Installed” o “Not Found”.\n\n"
        "- Los elementos analizados se clasifican mediante etiquetas visuales que indican su nivel de seguridad:\n\n"
        "   • [ OK ] — Todo está correcto y no requiere cambios.\n"
        "   • [ SUGGESTION ] — Recomendación de mejora sin riesgo grave.\n"
        "   • [ WARNING ] — Debilidad relevante que debe corregirse.\n"
        "   • [ EXPOSED ] / [ UNSAFE ] — Configuración peligrosa o crítica que requiere atención inmediata.\n\n"
        "📊 Resultado Final:\n"
        "Al concluir el escaneo, Lynis muestra un índice de endurecimiento del sistema (Hardening Index), junto con una lista detallada de advertencias y sugerencias, muchas de ellas acompañadas de enlaces a la documentación oficial para facilitar su corrección.\n\n"

        "📁 RUTA DE GUARDADO:\n\n"
        "- Por defecto, el sistema establece como ruta predeterminada el escritorio del usuario activo en la sesión.\n\n"
        "- Esta ubicación se adapta automáticamente al idioma configurado en el sistema operativo, detectando correctamente nombres como “Escritorio”, “Desktop” u otros equivalentes.\n\n"
        "- Si lo prefieres, puedes introducir manualmente la ruta absoluta de destino escribiéndola directamente en el campo correspondiente.\n\n"
        "- Alternativamente, haciendo clic en el botón 📁 situado a la derecha, se abrirá una ventana del explorador de archivos que te permitirá seleccionar visualmente la carpeta donde deseas guardar los informes.\n\n"

        "🎨 TEMA:\n\n"
        "- El texto cambia de color automáticamente según el tema claro/oscuro."
    )

    cuadro_texto.insert(tk.END, texto)
    cuadro_texto.config(state="disabled")
    cuadro_texto.pack(expand=True, fill="both")

""" def mostrar_ayuda_exportacion():
    messagebox.showinfo("Ayuda - Exportación de Informe",
        "📄 FORMATOS DE EXPORTACIÓN:\n"
       "- La herramienta permite generar informes en uno o varios de los siguientes formatos: TXT, Markdown (.md), HTML y PDF.\n"
        "- Estos formatos pueden marcarse individualmente mediante las casillas disponibles.\n"
        "- Para exportar un informe en formato PDF, es obligatorio seleccionar también el formato HTML, ya que el PDF se genera a partir del contenido HTML.\n"
        "- Todos los archivos generados se guardarán en una carpeta con fecha y hora para facilitar su organización.\n\n"
        "📧 CORREO ELECTRÓNICO:\n"
        "- Introduce uno o varios correos separados por comas.\n"
        "- No se aceptan espacios, punto y coma ni otros caracteres.\n"
        "- Ejemplo válido: persona1@mail.com,persona2@mail.com\n\n"
        "🛠 LYNIS:\n"
        "- Es una herramienta opcional de auditoría.\n"
        "- Necesita permisos de administrador (sudo).\n\n"
        "📁 RUTA DE GUARDADO:\n"
        "- Puedes escribirla manualmente o usar 📁 para seleccionarla.\n\n"
        "🎨 TEMA:\n"
        "- El texto cambia de color automáticamente según el tema claro/oscuro."
    ) """

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

def enviar_correo_con_archivos(destinatarios):
    try:
        remitente = "" #!change the sender email here
        password = "" #! (IMPORTANT) SMTP password or application-specific password for the sender

        mensaje = EmailMessage()
        mensaje['Subject'] = 'Informes de Auditoría Linux SysAuditX'
        mensaje['From'] = remitente
        mensaje['To'] = ", ".join(destinatarios)
        
        fecha_hora_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        mensaje.set_content(f"Se adjuntan los informes generados durante la auditoría del sistema Linux realizada el {fecha_hora_actual}. Muchas gracias por utilizar SysAuditX.")

        # Adjuntar archivos
        for archivo in [txt_file, md_file, html_file, pdf_file]:
            if os.path.exists(archivo):
                with open(archivo, 'rb') as f:
                    contenido = f.read()
                    mensaje.add_attachment(contenido, maintype='application', subtype='octet-stream', filename=os.path.basename(archivo))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(remitente, password)
            smtp.send_message(mensaje)

        ventana.lift()
        ventana.attributes('-topmost', True)
        messagebox.showinfo("Correo enviado", f"Los informes se han enviado a: {', '.join(destinatarios)} correctamente.")
        ventana.attributes('-topmost', False)
    except Exception as e:
        ventana.lift()
        ventana.attributes('-topmost', True)
        messagebox.showerror("Error al enviar correo", str(e))
        ventana.attributes('-topmost', False)

def comprobar_o_instalar_lynis():
    if shutil.which("lynis") is None:
        respuesta = messagebox.askyesno("Lynis no encontrado", "Lynis no está instalado. ¿Deseas instalarlo automáticamente?")
        if respuesta:
            instalar = ejecutar_comando("sudo apt update && sudo apt install -y lynis")
            ventana.lift()
            ventana.attributes('-topmost', True)
            messagebox.showinfo("Instalación completa", "Lynis se ha instalado correctamente. Pulsa OK para ejecutar el análisis y añadir el resultado al informe. Este proceso puede tardar unos segundos.")
            #messagebox.showinfo("Instalación completa", "Lynis ha sido instalado correctamente. Pulse OK para ejecutar el comando e insertarlo en el informe, puede tardar unos segundos")
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

    # 🖥 INFORMACIÓN GENERAL DEL SISTEMA 

    log("INFORMACION DEL SISTEMA", "uname -a")
    log("DISTRIBUCION", "cat /etc/os-release")
    log("UPTIME", "uptime")
    log("FECHA Y HORA", "date")
    log("VARIABLES DE ENTORNO", "printenv", como_lista=True)
    log("CONFIGURACION DE CIFRADO DE DISCO", "sudo cat /etc/crypttab", como_lista=True)
    log("PARAMETROS DE CONFIGURACION DEL KERNEL", "sysctl -a | grep kernel", como_lista=True)

    # 🧠 HARDWARE Y ALMACENAMIENTO

    log("CPU", "lscpu")
    log("MEMORIA RAM", "free -h")
    log("DISCOS", "lsblk -o NAME,SIZE,TYPE,MOUNTPOINT")
    log("ESPACIO EN DISCO", "df -h")

    # 🌐 RED Y CONEXIONES
    ip_detectada = obtener_ip_local()
    interfaz = obtener_interfaz_por_ip(ip_detectada)

    log("INTERFACES DE RED", "ip -brief address", como_lista=True)
    log("IP LOCAL DEL SISTEMA", f"echo {ip_detectada}")
    log("INTERFAZ ASOCIADA A LA IP LOCAL", f"echo {interfaz}")
    log("HOSTS DESCUBIERTOS EN LA RED", f"sudo netdiscover -i {interfaz} -r {ip_detectada} -P -c 50")
    log("INTERFACES DE RED", "ip -brief address", como_lista=True)
    log("INTERFACES EN PROMISCUO", "ip link | grep PROMISC", como_lista=True)
    log("RUTA POR DEFECTO", "ip route show")
    log("RUTAS DE RED", "ip route show table all")
    log("SERVIDORES DNS", "cat /etc/resolv.conf")
    log("PUERTOS ESCUCHANDO", "ss -tulnp")
    log("CONEXIONES ACTIVAS DEL SISTEMA", "ss -tpna | grep ESTAB", como_lista=True)
    #log("PROCESOS CON CONEXION", "ss -plntu")
    log("REGLAS DEL CORTAFUEGOS (iptables)", "iptables -L -n -v")
    log("RESTRICCIONES DE RED (/etc/hosts.allow)", "cat /etc/hosts.allow")
    log("RESTRICCIONES DE RED (/etc/hosts.deny)", "cat /etc/hosts.deny")

    # 👤 USUARIOS, GRUPOS Y PERMISOS
    usuario_real = os.environ.get("SUDO_USER") or getpass.getuser()
    log("USUARIOS DEL SISTEMA", "cut -d: -f1 /etc/passwd", como_lista=True)
    log("USUARIOS HUMANOS DEL SISTEMA (UID >= 1000)", "awk -F: '$3 >= 1000 {print $1}' /etc/passwd", como_lista=True)
    log("USUARIOS CON SHELL ACTIVA", "grep -v '/usr/sbin/nologin' /etc/passwd | cut -d: -f1", como_lista=True)
    log(f"ESTADO DE LA CONTRASEÑA DEL USUARIO ACTUAL ({usuario_real})", f"passwd -S {usuario_real}")
    log("USUARIOS EN GRUPO SUDO", "getent group sudo")
    log(f"GRUPOS DEL USUARIO ACTUAL ({usuario_real})", f"groups {usuario_real}")
    log("GRUPOS DEL SISTEMA", "cut -d: -f1 /etc/group", como_lista=True)
    log("LISTAS DE CONTROL DE ACCESO (ACLs) EN HOME", f"getfacl -R {os.path.expanduser('~')}")
    log(f"CONFIGURACION DE SUDO PARA EL USUARIO ({usuario_real})", f"sudo -l -U {usuario_real}")
    log("REGLAS ACTIVAS DE SUDO (sin comentarios)", "sudo grep -vE '^#|^$' /etc/sudoers")
    #log("REGLAS ACTIVAS DE SUDO (incluye comentarios)", "sudo cat /etc/sudoers")
    log("ARCHIVOS CON SUID ACTIVADO (riesgo de escalada de privilegios)", "find / -perm -4000 -type f 2>/dev/null", como_lista=True)

    # 📁 ARCHIVOS Y POSIBLES INDICIOS DE COMPROMISO

    dias_retroceso = 60  # 60 son dos meses atras
    # Calcular la fecha de inicio
    fecha_inicio = (datetime.now() - timedelta(days=dias_retroceso)).strftime("%d/%m/%Y")
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    #log("SCRIPTS OCULTOS (.sh, .py, .pl)", 'find /tmp /var/tmp /dev/shm /home -type f \\( -name ".*.sh" -o -name ".*.py" -o -name ".*.pl" \\) 2>/dev/null',como_lista=True)
    log("SCRIPTS OCULTOS (.sh, .py, .pl) CON FECHA Y TAMAÑO (ordenados por fecha y hora descendente)",'''find /tmp /var/tmp /dev/shm /home -type f \\( -name ".*.sh" -o -name ".*.py" -o -name ".*.pl" \\) -printf "%T@|%p|%TY-%Tm-%Td %TH:%TM:%S|%s\\n" 2>/dev/null | sort -nr | awk -F"|" '{ split($3,t,":"); printf "%-60s %-20s %10s bytes\\n", $2, t[1] ":" t[2] ":" sprintf("%02d", t[3]), $4 }' ''',
    como_lista=True)
    log(f"SCRIPTS OCULTOS MODIFICADOS DESDE EL {fecha_inicio} HASTA {fecha_actual}", f'''find /tmp /var/tmp /dev/shm /home -type f \\( -name ".*.sh" -o -name ".*.py" -o -name ".*.pl" \\) -mtime -{dias_retroceso} -printf "%T@|%p|%TY-%Tm-%Td %TH:%TM:%TS|%s\\n" 2>/dev/null | sort -nr | awk -F"|" '{{ split($3,t,":"); printf "%-60s %-20s %10s bytes\\n", $2, t[1] ":" t[2] ":" int(t[3]), $4 }}' ''',como_lista=True)
    log("TAREAS CRON ACTIVAS POR USUARIO","for user in $(cut -f1 -d: /etc/passwd); do echo \"------ Usuario: $user ------\"; crontab -l -u $user 2>/dev/null || echo '(sin tareas cron)'; echo; done",como_lista=True)
    log(f"ARCHIVOS DEL SISTEMA RELACIONADOS CON CRON MODIFICADOS DESDE EL {fecha_inicio} HASTA {fecha_actual}",f'''find /etc /var/spool/cron -path "*/cron*" -type f -mtime -{dias_retroceso} -printf "%T@|%p|%TY-%Tm-%Td %TH:%TM:%TS|%s\\n" 2>/dev/null | sort -nr | awk -F"|" '{{ split($3,t,":"); printf "%-60s %-20s %10s bytes\\n", $2, t[1] ":" t[2] ":" int(t[3]), $4 }}' ''',como_lista=True)
    log("LOGS GRANDES EN /home (>10MB)", 'find /home -type f -name "*.log" -size +10M 2>/dev/null', como_lista=True)

    # 🔐 AUTENTICACIÓN Y AUDITORÍA

    log("LOG DE AUTENTICACION", "grep -i 'authentication' /var/log/auth.log | tail -n 20", como_lista=True)
    log("ULTIMOS INICIOS DE SESION EXITOSOS", "last -n 10", como_lista=True)
    log("FALLOS DE LOGIN", "grep 'Failed password' /var/log/auth.log | tail -n 10")
    log(f"HISTORIAL DE COMANDOS DEL USUARIO ({usuario_real})", f"tail -n 20 /home/{usuario_real}/.bash_history")
    log("HISTORIAL DE COMANDOS EJECUTADOS POR ROOT", "sudo tail -n 20 /root/.bash_history")
    log("HISTORIAL DE ULTIMOS ERRORES DEL SISTEMA", "journalctl -p err -n 20", como_lista=True) # new
    log("ARCHIVOS DE LOG DISPONIBLES EN /var/log", "find /var/log -type f -name '*.log'", como_lista=True)

    # ⚙️ PROCESOS Y SERVICIOS

    log("PROCESOS EN EJECUCION (TOP 20 POR MEMORIA)", "ps aux --sort=-%mem | head -n 20", como_lista=True)
    log("PROCESOS ACTIVOS (USUARIO, GRUPO, COMANDO, TIEMPO)", "ps -eo user,group,comm,etime")
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
            elif isinstance(child, tk.Entry):
                child.configure(bg=colores["fondo"], fg=colores["texto"], insertbackground=colores["texto"])
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
    # === Menú superior con opción de ayuda ===
    menu_bar = tk.Menu(ventana_opciones)
    ayuda_menu = tk.Menu(menu_bar, tearoff=0)
    ayuda_menu.add_command(label="Ver ayuda", command=mostrar_ayuda_exportacion)
    menu_bar.add_cascade(label="Ayuda", menu=ayuda_menu)
    ventana_opciones.config(menu=menu_bar)
    ventana_opciones.title("Exportar informe")
    centrar_ventana(ventana_opciones, 600, 700) #! lo pongo mas abajo para solucionar el error de la ventana vacia

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
        messagebox.showinfo(
    "Lynis",
    "Lynis es una herramienta de auditoría de seguridad para sistemas Unix/Linux.\n\n"
    "Analiza configuraciones del sistema operativo, detecta vulnerabilidades, "
    "identifica configuraciones inseguras y proporciona recomendaciones para reforzar la seguridad.\n\n"
    "Requiere permisos de administrador para un análisis completo."
    )
        #messagebox.showinfo("Lynis", "Lynis es una herramienta de auditoría de seguridad para sistemas Unix.\nSe ejecuta con privilegios y revisa configuraciones del sistema, debilidades y medidas de seguridad.")

    label_info.bind("<Button-1>", mostrar_tooltip)
    frame_lynis.pack(pady=10)

    tk.Label(ventana_opciones, text="Nombre y Apellidos:").pack(pady=(20, 5))
    entry_nombre = tk.Entry(ventana_opciones, width=50)
    entry_nombre.pack(pady=5)
    
    #todo Para recoger el correo mediante input
    global entry_correo
    tk.Label(ventana_opciones, text="Correo electrónico de destino:").pack(pady=(20, 5))
    entry_correo = tk.Entry(ventana_opciones, width=50)
    entry_correo.pack(pady=5)

        # Insertar placeholder inicial
    placeholder_texto = "correo1@example.com,correo2@example.com"
    entry_correo.insert(0, placeholder_texto)
    entry_correo.config(fg="gray")

    def borrar_placeholder(event):
        if entry_correo.get() == placeholder_texto:
            entry_correo.delete(0, tk.END)
        entry_correo.config(fg="#FFFFFF" if modo_oscuro else "#000000")  # blanco en oscuro, negro en claro

    def restaurar_placeholder(event):
        if entry_correo.get() == "":
            entry_correo.insert(0, placeholder_texto)
            entry_correo.config(fg="gray")
        else:
            entry_correo.config(fg="#FFFFFF" if modo_oscuro else "#000000")  # blanco o negro si escribe


    entry_correo.bind("<FocusIn>", borrar_placeholder)
    entry_correo.bind("<FocusOut>", restaurar_placeholder)

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
    ventana_opciones.update_idletasks() 
    centrar_ventana(ventana_opciones, 600, 700) 
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

    
    placeholder_texto = "correo1@example.com,correo2@example.com"

    
    correo_destino = entry_correo.get().strip()
    lista_destinatarios = []

    if correo_destino and correo_destino != placeholder_texto:
        correo_limpio = correo_destino.replace(" ", "")
        separadores_invalidos = set(re.findall(r"[^a-zA-Z0-9@.,]", correo_limpio))
        #separadores_invalidos = set(re.findall(r"[^\w@.,\-]", correo_limpio))
        if separadores_invalidos:
            caracteres = "', '".join(separadores_invalidos)
            mensaje_error = f"Se detecto un caracter de separación no válido: '{caracteres}'.\nPor favor, separa los correos únicamente con comas."
            messagebox.showerror("Error de correo", mensaje_error)
            return

        lista_destinatarios = [correo.strip() for correo in correo_limpio.split(',') if correo.strip()]
        patron_correo = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

        for correo in lista_destinatarios:
            if not patron_correo.match(correo):
                razon = ""
                if '@' not in correo:
                    razon = "Falta el símbolo '@'."
                else:
                    usuario_dominio = correo.split('@')
                    if len(usuario_dominio) != 2:
                        razon = "Has introducido más de un '@'."
                    elif not usuario_dominio[0]:
                        razon = "Falta la parte antes del '@'."
                    elif not usuario_dominio[1]:
                        razon = "Falta el dominio después del '@'."
                    elif '.' not in usuario_dominio[1]:
                        razon = "Falta un punto ('.') en el dominio del correo (por ejemplo, '.com')."
                    elif usuario_dominio[1].endswith('.'):
                        razon = "Falta el nombre del dominio tras el punto final (por ejemplo, '.com')."
                    else:
                        razon = "Formato no válido."
                messagebox.showerror("Error de correo", f"El correo '{correo}' no es válido. \n{razon}\nRecuerda separar correctamente por comas los correos.")
                return


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
    
    if lista_destinatarios:
        enviar_correo_con_archivos(lista_destinatarios)
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
