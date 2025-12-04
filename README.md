# Planeador de Turnos CP-SAT (Prueba Técnica)

Este proyecto implementa un modelo CP-SAT con OR-Tools para asignar turnos en un Punto de Venta (PDV) con las reglas:

- 3 asesores
- 3 turnos: Apertura, Cierre, Intermedio
- Cada asesor tiene **solo un turno por semana**
- No se asignan turnos en domingos ni festivos
- Opción: una asesora solo puede tener Apertura
- Generación de DataFrame con el resultado
- Sitio web en Flask para mostrar la planeación

## Estructura
app.py -> servidor Flask
scheduler.py -> clase con CP-SAT
run_planner.py -> ejecución por consola
templates/ -> HTML
tests/ -> pruebas unitarias

shell
Copiar código

## Instalar dependencias
pip install -r requirements.txt

shell
Copiar código

## Ejecutar Flask
python app.py

shell
Copiar código

## Ejecutar por consola
python run_planner.py

shell
Copiar código

## Ejecutar pruebas
pytest -q

shell
Copiar código

## Autor
Prueba técnica desarrollada en Python con OR-Tools.
