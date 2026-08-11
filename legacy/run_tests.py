import json

with open("tests.json", "r", encoding="utf-8") as archivo:
    datos = json.load(archivo)

print("🧪 CASOS DE PRUEBA GENERADOS POR IA")
print()

for test in datos["test_cases"]:
    print(f"ID: {test['id']}")
    print(f"Título: {test['title']}")
    print(f"Prioridad: {test['priority']}")
    print("Pasos:")

    for paso in test["steps"]:
        print(f"  - {paso}")

    print(f"Resultado esperado: {test['expected_result']}")
    print("-" * 50)
