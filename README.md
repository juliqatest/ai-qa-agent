# 🤖 AI QA Agent

![CI](https://github.com/juliqatest/ai-qa-agent/actions/workflows/qa-check.yml/badge.svg)

AI QA Agent es un proyecto de Quality Assurance que combina Inteligencia Artificial generativa con automatización de pruebas para transformar historias de usuario en casos de prueba ejecutables.

A partir de una historia de usuario, el agente genera casos de prueba con Gemini, crea scripts Playwright, los ejecuta automáticamente, analiza los fallos y genera evidencia y reportes QA.

## 🚀 Funcionalidades

El agente puede:

- Recibir una historia de usuario.
- Generar casos de prueba positivos y negativos con IA.
- Generar automáticamente scripts Playwright en Python.
- Validar la sintaxis del código generado antes de ejecutarlo.
- Intentar autocorregir código inválido generado por IA.
- Ejecutar pruebas automáticamente en Chromium.
- Detectar resultados PASS y FAIL.
- Manejar timeouts.
- Capturar screenshots como evidencia de fallos.
- Analizar fallos utilizando Gemini.
- Clasificar fallos como:
  - `BUG`
  - `TEST_ERROR`
  - `TEST_DATA`
  - `ENVIRONMENT`
  - `NEEDS_INVESTIGATION`
- Generar Bug Reports únicamente cuando corresponde.
- Generar un reporte QA final.
- Ejecutar tests internos del propio agente.
- Ejecutarse automáticamente mediante GitHub Actions.
- Publicar reportes y evidencias como artifacts del pipeline.

## 🧠 Arquitectura

```text
User Story
    │
    ▼
Test Generator
    │
    ▼
Gemini
    │
    ▼
Test Cases
    │
    ▼
Playwright Generator
    │
    ▼
Code Validator
    │
    ├── Código inválido ──► Code Fixer ──► Validación
    │
    ▼
Test Runner
    │
    ├── PASS
    │
    └── FAIL
          │
          ▼
    Failure Analyzer
          │
          ├── BUG ──► Bug Report + Evidence
          │
          └── TEST_ERROR / TEST_DATA /
              ENVIRONMENT / NEEDS_INVESTIGATION
          │
          ▼
     QA Report
```

## 📁 Estructura

```text
ai-qa-agent/
├── app.py
├── src/
│   ├── __init__.py
│   ├── bug_report_generator.py
│   ├── code_fixer.py
│   ├── code_validator.py
│   ├── config.py
│   ├── failure_analyzer.py
│   ├── playwright_generator.py
│   ├── report_generator.py
│   ├── test_generator.py
│   └── test_runner.py
├── tests/
│   ├── conftest.py
│   └── test_core.py
├── legacy/
├── .github/
│   └── workflows/
│       └── qa-check.yml
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## 🛠 Tecnologías

- Python 3.12
- Playwright
- Chromium
- Google Gemini API
- Google GenAI SDK
- pytest
- python-dotenv
- Git
- GitHub Actions

## ⚙️ Instalación

Clonar el repositorio:

```bash
git clone https://github.com/juliqatest/ai-qa-agent.git
cd ai-qa-agent
```

Crear un entorno virtual:

```bash
python3 -m venv .venv
```

Activarlo en macOS/Linux:

```bash
source .venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Instalar Chromium para Playwright:

```bash
playwright install chromium
```

## 🔐 Configuración

Crear el archivo `.env` a partir del ejemplo:

```bash
cp .env.example .env
```

Configurar las variables:

```text
GEMINI_API_KEY=tu_api_key

GEMINI_MODEL=gemini-3.5-flash-lite

BASE_URL=https://www.saucedemo.com/

TEST_USERNAME=standard_user
TEST_PASSWORD=secret_sauce

TEST_TIMEOUT=45
```

El archivo `.env` está excluido de Git para evitar publicar secretos.

## ▶️ Ejecutar el agente

Con el entorno virtual activo:

```bash
python app.py
```

El agente solicitará una historia de usuario.

Ejemplo:

```text
Como usuario quiero iniciar sesión con mi usuario y contraseña para acceder al sistema.
```

A partir de ella ejecutará el flujo completo de generación, automatización, análisis y reporting.

## 📊 Resultados

Durante una ejecución pueden generarse:

```text
tests.json
results.json
qa_report.md
test_TC001.py
test_TC002.py
...
evidence_TCXXX.png
bug_report_TCXXX.md
```

`results.json` contiene los resultados estructurados de ejecución.

`qa_report.md` contiene el reporte QA generado al finalizar.

Los screenshots proporcionan evidencia cuando una prueba falla.

Los Bug Reports se generan únicamente cuando el análisis clasifica el fallo como un bug de la aplicación.

## 🧪 Tests internos

El proyecto también contiene tests para validar componentes del propio agente.

Ejecutarlos con:

```bash
pytest -v
```

Actualmente se validan componentes como:

- Validación de Python generado.
- Detección de PASS.
- Detección de FAIL.
- Manejo de errores del runner.
- Generación de Bug Reports.

## 🔄 CI/CD

El proyecto utiliza GitHub Actions.

En cada push o Pull Request sobre `main`, el pipeline puede:

1. Preparar Python.
2. Instalar dependencias.
3. Instalar Chromium.
4. Validar sintaxis.
5. Validar imports.
6. Ejecutar los tests internos.
7. Ejecutar el AI QA Agent.
8. Publicar resultados y evidencias como artifacts.

El badge ubicado al comienzo del README muestra el estado actual del pipeline.

## 🛡️ Manejo de errores generados por IA

Antes de ejecutar un script generado por Gemini, el agente analiza su sintaxis mediante el AST de Python.

Si el código es inválido:

```text
Código generado
      ↓
Code Validator
      ↓
Syntax Error
      ↓
Code Fixer
      ↓
Segunda validación
```

Si la autocorrección continúa siendo inválida, el resultado se registra como `TEST_ERROR` en lugar de reportarlo incorrectamente como un bug del producto.

## 🎯 Objetivo del proyecto

El objetivo de AI QA Agent es explorar cómo la IA generativa puede asistir al trabajo de Quality Assurance combinando:

- Diseño de pruebas.
- Automatización.
- Ejecución.
- Análisis de fallos.
- Evidencia.
- Clasificación de defectos.
- Reporting.
- Integración continua.

El proyecto prioriza que la IA actúe como asistente del proceso de QA y que los fallos de automatización puedan distinguirse de defectos reales de la aplicación.

## 📌 Estado

**AI QA Agent v1.0 — Release Candidate**

La versión actual incluye el flujo end-to-end, arquitectura modular, validación y autocorrección básica de código, tests internos y ejecución mediante CI/CD.
