# 🤖 AI QA Agent

AI QA Agent es un proyecto experimental de Quality Assurance que combina
Inteligencia Artificial generativa con automatización de pruebas utilizando
Python, Gemini y Playwright.

El objetivo es transformar una historia de usuario en casos de prueba,
ejecutarlos automáticamente y utilizar IA para analizar los resultados.

## 🚀 Funcionalidades

El agente puede:

- Recibir una historia de usuario.
- Generar casos de prueba automáticamente.
- Generar escenarios positivos y negativos.
- Generar código Playwright.
- Ejecutar pruebas en Chromium.
- Detectar PASS y FAIL.
- Capturar screenshots cuando una prueba falla.
- Analizar errores utilizando IA.
- Diferenciar entre:
  - Bug de aplicación
  - Error de automatización
  - Datos de prueba incorrectos
  - Problemas de ambiente
- Generar reportes QA.
- Generar Bug Reports cuando corresponde.

## 🧠 Arquitectura

Historia de usuario

↓

Gemini

↓

Casos de prueba

↓

Playwright

↓

Ejecución automática

↓

PASS / FAIL

↓

Análisis con IA

↓

Reporte QA / Bug Report

## 🛠 Tecnologías

- Python 3.12
- Playwright
- Google Gemini API
- Google GenAI SDK
- python-dotenv
- Git

## ▶️ Instalación

Crear un entorno virtual:

```bash
python3 -m venv .venv
