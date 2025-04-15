# 🛡️ SysAuditX - Auditoría Inteligente de Sistemas Linux con Exportación Multiformato

<p align="center">
  <img src="https://i.imgur.com/hTKCzdz.png" alt="Logo de la herramienta">
</p>

**SysAuditX** es una herramienta de auditoría avanzada para sistemas **Linux** que permite recopilar, analizar y exportar información crítica del sistema de forma visual e intuitiva. A través de una interfaz gráfica interactiva, el usuario puede iniciar una **auditoría completa con un solo clic** y obtener un **informe detallado** sobre la configuración del sistema, servicios activos, usuarios, red, seguridad, historial de comandos y más.

Lo más destacable de **SysAuditX** es su capacidad para generar automáticamente informes profesionales en múltiples formatos: **TXT**, **Markdown**, **HTML** y **PDF**, adaptándose tanto a usuarios técnicos como a quienes necesiten documentación clara y presentable. Además, cuenta con soporte para modo claro/oscuro e integra funcionalidades que facilitan el análisis forense, el endurecimiento de sistemas y la elaboración de reportes automatizados.

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
pip3 install -r requirements.txt
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

### 4.1 Ejecutar la aplicación

Desde la carpeta raíz del proyecto, ejecuta el siguiente comando:

```
sudo python3 linux_scan_tool.py
```
> [!IMPORTANT]
> Es recomendable ejecutarlo con **sudo** para que la herramienta pueda **acceder a información sensible del sistema**, como **logs**, **historial de root** o **configuraciones protegidas**.

### 4.2 Interfaz gráfica de la herramienta

Al ejecutar el script, se abrirá automáticamente una ventana gráfica como la siguiente:

<p align="center">
  <img src="https://i.imgur.com/yv9pFzc.png" alt="Primera vista de la herramienta">
</p>

Desde esta interfaz podrás:

- Iniciar la auditoría del sistema con un solo clic.
- Cambiar entre modo claro y oscuro.
- Elegir los formatos de exportación que deseas (TXT, Markdown, HTML y PDF).

Una vez **seleccionados los formatos**, la herramienta **generará un informe completo** que podrás utilizar para documentar, analizar o compartir.

### 4.3 Ubicación de los informes generados
Todos los informes se guardan automáticamente en una carpeta dentro de tu directorio personal:

```
~/auditoria_linux_final/auditoria_<fecha-hora>

```
>[!NOTE]
>🗂️ Cada **auditoría** crea una nueva carpeta con fecha y hora, para que mantengas un histórico ordenado de auditorías realizadas.







