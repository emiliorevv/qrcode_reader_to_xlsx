# Lector de Códigos QR → Excel (.xlsx)

Convierte lecturas de **Códigos QR** (desde cámara web) en filas de Excel con las columnas fijas:

**Nombre | Número de empleado | Área | timestamp**

Este proyecto usa **OpenCV** para leer la cámara y decodificar el QR (sin dependencias nativas como zbar) y **openpyxl** para escribir Excel.

---

## 📦 Requisitos

* **Python** 3.9 – 3.12 (recomendado 3.12).
* Cámara web funcional (o archivo de video para pruebas).
* Sistema operativo: **Windows**, **macOS**, o **Linux**.

### Dependencias Python

Incluidas en `requirements.txt`:

```
opencv-python>=4.8.0
openpyxl>=3.1.2
qrcode>=7.4     # opcional, solo si deseas generar QRs de prueba
Pillow>=10.0.0  # opcional, requerido por qrcode para generar imágenes
```

---

## 🚀 Instalación y ejecución (Windows / macOS / Linux)

> Los comandos asumen que estás en la carpeta del proyecto (donde está `main.py`).

### 1) Crear entorno virtual

**Windows (PowerShell):**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux (bash/zsh):**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3) Ejecutar el lector

```bash
python main.py
```

> Cierra la app con la tecla **q**.

---

## 🧪 Formatos de QR aceptados

El lector extrae **Nombre / Número de empleado / Área** desde:

* **JSON**

```json
{"nombre":"Ana Pérez","numero_empleado":"7789","area":"Ventas"}
```

* **Multilínea con dos puntos**

```
Nombre: Ana Pérez
N° de empleado: 7789
Área: Ventas
```

* **Una sola línea separada por comas o punto y coma**

```
Nombre: Ana Pérez, N° de empleado: 7789, Area: Ventas
```

* **Clave=valor**

```
nombre=Ana Pérez; empleado id=7789; dept=Ventas
```

> El parser es tolerante a acentos, mayúsculas y sinónimos comunes: `N°/No./ID empleado`, `Dept/Departamento`, `Area/Área/División`, etc.

---

## 🧾 Salida (Excel)

* Archivo: **`empleados_qr.xlsx`** (se crea automáticamente en la carpeta del proyecto).
* Hoja activa con encabezados:

```
Nombre | Número de empleado | Área | timestamp
```

Cada lectura válida agrega una nueva fila. Se evita el **duplicado inmediato** de un mismo QR en bucle.

---

## 🔧 Solución de problemas de cámara

### 1) macOS — permisos de cámara

* Ve a **Configuración del sistema → Privacidad y seguridad → Cámara** y habilita **Python** o tu IDE (PyCharm/VSCode).
* Ejecuta una vez desde **Terminal** para que macOS solicite permisos.

### 2) Seleccionar backend de captura en OpenCV

En `main.py` se intenta primero **AVFOUNDATION** (mejor en macOS) y luego `CAP_ANY`:

```python
cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
if not cap.isOpened():
    cap = cv2.VideoCapture(0, cv2.CAP_ANY)
```

Otras opciones a probar si falla:

```python
# Índice alternativo de cámara\ ncap = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)

# En Windows a veces ayuda:
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# En Linux (V4L2):
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
```

### 3) ¿La cámara está ocupada?

Cierra otras apps que la usen (Zoom, Teams, navegador) e intenta de nuevo.

### 4) Probar con script mínimo

Crea `test_cam.py`:

```python
import cv2
cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
if not cap.isOpened():
    cap = cv2.VideoCapture(0, cv2.CAP_ANY)
print("opened?", cap.isOpened())
while True:
    ok, frame = cap.read()
    if not ok:
        print("no frame"); break
    cv2.imshow("cam", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release(); cv2.destroyAllWindows()
```

### 5) Usar un archivo de video para avanzar sin cámara

```python
cap = cv2.VideoCapture("video_qr_prueba.mp4")
```

---

## 🛠️ Solución de problemas del parser

* Si ves el mensaje: `⚠️ Faltan campos: ...`, el QR no contenía los tres campos requeridos.
* Puedes activar **modo debug** en `parser_qr.py` para ver cómo se interpretan los pares clave:valor.

```python
DEBUG = True  # al inicio del archivo
```

La consola mostrará los pares detectados, útil para ajustar el contenido del QR de origen.

---

## 🧰 Comandos útiles

### Entorno / dependencias

```bash
# crear y activar venv
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# instalar dependencias
pip install -r requirements.txt

# exportar dependencias actuales al requirements.txt
pip freeze > requirements.txt
```

### Ejecutar

```bash
python main.py
```

### Git (si usas GitHub)

```bash
# primera vez
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin git@github.com:<tu_usuario>/<tu_repo>.git
git push -u origin main

# si el remoto tiene cambios que no tienes localmente
git pull origin main --rebase
# resuelve conflictos si aparecen, luego:
git push origin main

# si quieres forzar a sobreescribir el remoto (cuidado)
git push origin main --force
```

---

## 🧪 (Opcional) Generar QRs de prueba

Crea `generate_qr.py` para generar imágenes QR de ejemplo (requiere `qrcode` y `Pillow`):

```python
import qrcode, json

payload = {
    "nombre": "Ana Pérez",
    "numero_empleado": "7789",
    "area": "Ventas"
}
img = qrcode.make(json.dumps(payload, ensure_ascii=False))
img.save("qr_empleado.png")
print("QR generado: qr_empleado.png")
```

---

## 📁 Estructura sugerida del proyecto

```
.
├─ main.py           # loop principal: cámara → QR → parseo → Excel
├─ qr_reader.py      # usa OpenCV QRCodeDetector (sin zbar)
├─ parser_qr.py      # mapea Nombre/Numero/Área desde distintos formatos
├─ excel_utils.py    # crea/abre empleados_qr.xlsx y agrega filas
├─ requirements.txt
└─ generate_qr.py    # opcional, genera QR de prueba
```

---

## ❓ Preguntas frecuentes

**¿Necesito zbar/pyzbar?** No. Este lector usa `cv2.QRCodeDetector()`.

**¿Dónde se guarda el Excel?** En la misma carpeta, como `empleados_qr.xlsx`.

**¿Qué pasa si el QR trae más campos?** Solo se usan *Nombre*, *Número de empleado* y *Área*; lo demás se ignora.

**¿Puedo cambiar el nombre del archivo Excel o columnas?** Sí, edita `EXCEL_FILE` y `HEADERS` en `excel_utils.py`.

---

¡Listo! Si necesitas empaquetar esto como ejecutable (Windows `.exe` con PyInstaller o app en macOS), avísame y te dejo la receta. 🔧🧡
