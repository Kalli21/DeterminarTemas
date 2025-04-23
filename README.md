# 📘 Documentación Técnica - Microservicio Determinación de Temas

## 1. 🎯 Arquitectura

Este proyecto forma parte de una arquitectura basada en microservicios con comunicación RESTful. En el diagrama general del sistema se representa su posición, sin embargo, este documento se enfoca únicamente en el microservicio **Determinación de Temas**.

### Documentación del proyecto
https://drive.google.com/file/d/10JRsbyRGNGjKlKvHWzPM2TNxsGtw8gUo/view?usp=sharing
---

## 2. 🧩 Patrón de diseño

El patrón de diseño utilizado es **MVC** (Modelo - Vista - Controlador). El componente principal que implementa este patrón es `main.py`, el cual expone las APIs necesarias. Además, el diseño incluye una base de datos que respalda el análisis temático de los comentarios.

---

## 3. ⚙️ Instalación y Configuración

### 3.1 Requisitos Previos

- Python 3.9 o superior (**3.10 recomendado**)
- `pip` (gestor de paquetes de Python)
- `virtualenv` (opcional pero recomendado)
- Credenciales de **Firebase Database**

### 3.2 Instalación

```bash
# Clona el repositorio
git clone https://github.com/Kalli21/DeterminarTemas.git
cd DeterminarTemas

# (Opcional) Crea y activa un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instala las dependencias
pip install -r requirements.txt

# Corre el proyecto
uvicorn main:app --reload
