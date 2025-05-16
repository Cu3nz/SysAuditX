# 🛡️ SysAuditX - Auditoría Inteligente de Sistemas Linux con Exportación Multiformato

<p align="center">
  <img src="https://i.imgur.com/BYGjnbP.png" alt="Logo de la herramienta">
</p>

**SysAuditX** es una herramienta de auditoría avanzada para sistemas **Linux** que permite recopilar, analizar y exportar información crítica del sistema de forma visual e intuitiva. A través de una interfaz gráfica interactiva, el usuario puede iniciar una **auditoría completa con un solo clic** y obtener un **informe detallado** sobre la configuración del sistema, servicios activos, usuarios, red, seguridad, historial de comandos y más.

Lo más destacable de **SysAuditX** es su capacidad para generar automáticamente informes profesionales en múltiples formatos: **TXT**, **Markdown**, **HTML** y **PDF**, adaptándose tanto a usuarios técnicos como a quienes necesiten documentación clara y presentable.

Además, incorpora soporte para **modo claro/oscuro**, integra funcionalidades específicas para facilitar el **análisis forense**, el **endurecimiento de sistemas** y la **elaboración de reportes automatizados**.

Como valor añadido, **SysAuditX** permite **enviar los informes generados automáticamente por correo electrónico** desde la propia herramienta, mejorando la **accesibilidad** y facilitando la **distribución inmediata** de los resultados.


✅ Ideal para:
- Auditorías internas de ciberseguridad 🔐  
- Formación práctica en análisis de sistemas 🧪  
- Generación de informes técnicos automatizados 📄  
- Evaluación de configuraciones críticas en Linux 🧰

## 📦 1. Pasos previos antes de descargar y ejecutar el script

Antes de lanzar **SysAuditX**, es necesario preparar el entorno con las dependencias esenciales. A continuación se detallan los pasos necesarios para sistemas basados en **Debian/Ubuntu**.

- ###  1.1 Instalar Python 3 (por si no lo tienes)

 ```bash
 sudo apt update && sudo apt install python3 -y
 ```
Para comprobar que se ha instalado correctamente ejecuta el siguiente comando: 

```
python3 --version
```

- ### 1.2 Instalar pip para Python 3

```
sudo apt install python3-pip -y
```
Para comprobar que se ha instalado correctamente ejecuta el siguiente comando: 

``` 
pip3 --version
````
- ### 1.3 Instalar dependencias adicionales
  La aplicación requiere algunos paquetes gráficos y de exportación que no vienen por defecto. Instálalos con:
  
```
sudo apt install python3-tk wkhtmltopdf -y
```
- **python3-tk:** permite mostrar la interfaz gráfica de la aplicación.
- **wkhtmltopdf**: permite la conversión del informe HTML a formato PDF.
  
- ### 1.4 Instalar la librería Pillow con soporte gráfico
  
  Para que la interfaz funcione correctamente con imágenes en modo claro/oscuro, necesitas instalar Pillow con soporte para `ImageTk`:

```bash
  sudo apt install python3-pil.imagetk -y
```

- ### 1.5 Instalar Netdiscover  
  **Netdiscover** es una herramienta para detectar hosts activos en la red. Es utilizada por SysAuditX para el escaneo inicial.

  ```bash
  sudo apt install netdiscover -y
  ```
  Para comprobar que se ha instalado correctamente ejecuta el siguiente comando: 

  ``` 
   netdiscover --help
  ````

- ### 1.6 Instalar Nmap  
  **Nmap** es una herramienta de escaneo de red que permite descubrir puertos y servicios activos en los equipos conectados. SysAuditX la utiliza para analizar cada IP detectada por Netdiscover.

  ```bash
  sudo apt install nmap -y
  ```
  Para comprobar que se ha instalado correctamente ejecuta el siguiente comando: 

    ``` 
    nmap --version
   ```


## 📥 2. Clonado del Repositorio y Preparación del Entorno 

Una vez instalado todo lo necesario, ya puedes obtener **SysAuditX** en tu máquina. Tienes dos formas de hacerlo:

- **Opción 1: Clonar el repositorio con Git**

  Si tienes **Git** instalado en tu sistema, puedes **clonarlo** directamente con el siguiente comando:

   ```bash
  git clone https://github.com/Cu3nz/SysAuditX
  
    ```
- **Opción 2: Descargar el proyecto en formato ZIP**
    
    También puedes descargar este repositorio en formato **ZIP** desde la parte superior de esta       página. Solo tienes que hacer clic en el botón **"Code"** y luego seleccionar **"Download          ZIP"**. Una vez descargado, simplemente descomprímelo en la carpeta que prefieras.

    Una vez **descargado** o **clonado** el repositorio, abre el proyecto con tu **editor de código** favorito.
  
## 📚 3. Instalación de dependencias necesarias

 Una vez abierto el proyecto en tu editor de código favorito, es el momento de **instalar las dependencias** que necesita la **herramienta para ejecutarse correctamente**.
 
 Estas dependencias están listadas en el archivo **`requirements.txt`**.

 - ### 4.1 Ejecutar el comando de instalación (Importante ejecutar con **sudo**)

  ```bash
sudo pip3 install -r requirements.txt
  ```
> [!WARNING]
> **Posible error en Ubuntu 24.04**

<p align="center">
  <img src="https://i.imgur.com/hnUqkKu.png" alt="Errorxternally-managed-environment">
</p>

>[!NOTE]
>Este error aparece en versiones recientes de **Ubuntu (23.04 o superior)** debido a una **nueva medida de seguridad** llamada **[PEP 668](https://peps.python.org/pep-0668/)**. Esta política **impide** que se puedan **instalar paquetes con `pip`** directamente en el **entorno global del sistema**, para **evitar romper dependencias críticas de Python** en el sistema operativo.

> ✅  **Soluciones segun tu version de Ubuntu**

- Si usas **Ubuntu 22.04 o inferior**:

```
sudo pip3 install -r requirements.txt
```
- Si usas **Ubuntu 23.04 o superior**: 

``` 
sudo pip3 install --break-system-packages -r requirements.txt
```

  O tambien puedes crear un **entorno virtual** ejecutando los siguientes comandos: 

```
python3 -m venv venv
source venv/bin/activate
sudo pip3 install -r requirements.txt
```
## 🚀 4. Ejecutar la herramienta

  Una vez **instaladas** todas las **dependencias** y con el repositorio listo, ya puedes lanzar **SysAuditX** y comenzar la **auditoría de tu sistema Linux**.

### 4.1 Ejecutar la herramienta

Desde la carpeta raíz del proyecto, ejecuta el siguiente comando:

```
sudo python3 linux_scan_tool.py
```
> [!IMPORTANT]
> Es **obligatorio** ejecutar la herramienta con **`sudo`** para que pueda acceder a información sensible del sistema, como logs, historiales del usuario root o configuraciones protegidas.

> [!CAUTION]
>  En caso de **NO ejecutarse** con permisos de **`superusuario`**, la herramienta **solicitará la contraseña de superusuario** y **NO** continuará con el análisis hasta que esta se introduzca correctamente.


### 4.2 Interfaz gráfica de la herramienta

Al ejecutar el script, se abrirá automáticamente una ventana gráfica como la siguiente:

<p align="center">
  <img src="https://i.imgur.com/yv9pFzc.png" alt="Primera vista de la herramienta">
</p>

Desde esta interfaz podrás:

- Iniciar la auditoría del sistema con un solo clic.
- Cambiar entre modo claro y oscuro.

Una vez iniciada la auditoría, se abrirá la ventana de exportación, donde podrás:

<p align="center">
  <img src="https://github.com/user-attachments/assets/29bb463c-0648-4bda-be8e-173e2393728d" alt="Vista de Exportación de informes">
</p>

- Elegir los formatos de exportación que deseas (TXT, Markdown, HTML y PDF).
- Incluir opcionalmente el análisis realizado por la herramienta **[Lynis](https://cisofy.com/lynis/)**
- Añadir el nombre y apellidos de la persona responsable del informe.
- Introducir uno o varios correos electrónicos de destino, separados por comas, para **enviar automáticamente el informe por email.**
  
> [!NOTE]
> Si deseas utilizar el envío de correos automáticos, consulta el apartado [Configuración para el envío de correos electrónicos](#configuracion-correo) más abajo.

- Seleccionar la ruta local donde se generarán y almacenarán los informes exportados.

Una vez **seleccionados los formatos**, la herramienta **generará un informe completo** que podrás utilizar para documentar, analizar o compartir.

<a name="configuracion-correo"></a>

### 4.3 📧 Configuración para el envío de correos electrónicos



Para que la aplicación pueda enviar correos, debes utilizar una **contraseña de aplicación** de Gmail.  

Esto es necesario porque Google no permite acceder directamente usando solo el correo y contraseña normales.

### Pasos para obtener una contraseña de aplicación:
1. Accede a tu [Cuenta de Google](https://myaccount.google.com/) **desde donde quieres enviar los mensajes.** 
2. Ve a la sección **Seguridad**.
3. Asegúrate de que tienes activada la **Verificación en dos pasos** (2FA).
4. Una vez activada, vuelve a **Seguridad** y busca en el buscador **Contraseñas de aplicaciones**.
  
<p align="center">
  <img src="https://github.com/user-attachments/assets/268c0257-b5d3-4aa0-b992-ea1828d66a85" alt="Opcion contraseñas de aplicacion en el buscador">
</p>

6. Define un nombre.

<p align="center">
  <img src="https://github.com/user-attachments/assets/df549154-68b9-4f11-b9bf-ea69f09e0313" alt="Opcion contraseñas de aplicacion en el buscador">
</p>

8. Google generará una contraseña especial de 16 caracteres.
   
  > [!WARNING]
  > **Cópiala y guárdala en un lugar seguro, ya que no podrás verla de nuevo. Si la pierdes, deberás generar una nueva contraseña de aplicación.** 
   
10. Sustituye en el **código** la **contraseña actual** por la **nueva contraseña de aplicación** en esta parte:
  ```python
  remitente = "tucorreo@gmail.com"
  password = "contraseña_de_aplicación"
  ```

### 4.4 Ubicación de los informes generados

Todos los informes se guardan automáticamente en una carpeta dentro del **Escritorio** del usuario que ha iniciado sesión.

La aplicación detecta de forma automática el idioma del sistema para ubicar correctamente el escritorio (por ejemplo, `~/Escritorio/` en sistemas en español o `~/Desktop/` en sistemas en inglés).

Los informes generados se guarda en una carpeta con el siguiente formato:

```
aditoria_<fecha-hora>

```
>[!NOTE]
>🗂️ Cada **auditoría** crea una **nueva carpeta** con **fecha y hora**, para que **mantengas un histórico ordenado de auditorías realizadas.**







