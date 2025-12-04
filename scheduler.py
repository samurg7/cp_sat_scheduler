from ortools.sat.python import cp_model
import pandas as pd
import datetime


class Scheduler:
    def __init__(self, year, month, asesor_fijo_apertura, num_semanas):
        if num_semanas < 1 or num_semanas > 8:
            raise ValueError("El número de semanas debe estar entre 1 y 8.")

        self.year = year
        self.month = month
        self.asesores = ["A1", "A2", "A3"]
        self.fijo = asesor_fijo_apertura  # puede ser A1, A2, A3 o "Ninguno"
        self.num_semanas = num_semanas

        # Determinar quiénes rotan
        if self.fijo != "Ninguno":
            self.rotan = [a for a in self.asesores if a != self.fijo]
        else:
            self.rotan = self.asesores.copy()

        self.turnos = ["Apertura", "Cierre", "Intermedio"]

    # -------------------------------------------------------------
    def generar_fechas(self):
        """Genera fechas según las semanas solicitadas, omitiendo domingos."""
        dias_totales = self.num_semanas * 7
        inicio = datetime.date(self.year, self.month, 1)

        fechas = []
        dia = inicio

        for _ in range(dias_totales):
            if dia.weekday() != 6:  # omitir domingo
                fechas.append(dia)
            dia += datetime.timedelta(days=1)

        if len(fechas) == 0:
            raise RuntimeError("No hay fechas válidas para generar la planeación.")

        return fechas

    # -------------------------------------------------------------
    def planear(self):
        try:
            fechas = self.generar_fechas()
        except Exception as e:
            raise RuntimeError(f"Error generando fechas: {e}")

        semanas = list(range(1, self.num_semanas + 1))
        model = cp_model.CpModel()

        # variables
        turno = {}
        for a in self.asesores:
            for s in semanas:
                for t in self.turnos:
                    turno[(a, s, t)] = model.NewBoolVar(f"{a}_{s}_{t}")

        # -------------------------------------------------------------
        # 1. Si hay asesor fijo, asegurarlo en Apertura
        # -------------------------------------------------------------
        if self.fijo != "Ninguno":
            for s in semanas:
                model.Add(turno[(self.fijo, s, "Apertura")] == 1)
                model.Add(turno[(self.fijo, s, "Cierre")] == 0)
                model.Add(turno[(self.fijo, s, "Intermedio")] == 0)

        # -------------------------------------------------------------
        # 2. Cada asesor solo un turno por semana
        # -------------------------------------------------------------
        for a in self.asesores:
            for s in semanas:
                model.Add(sum(turno[(a, s, t)] for t in self.turnos) == 1)

        # -------------------------------------------------------------
        # 3. Todos los turnos se asignan por semana
        # -------------------------------------------------------------
        for s in semanas:
            for t in self.turnos:
                model.Add(sum(turno[(a, s, t)] for a in self.asesores) == 1)

        # -------------------------------------------------------------
        # 4. Rotación entre los asesores que rotan
        # -------------------------------------------------------------
        for a in self.rotan:
            for s in range(1, self.num_semanas):
                # Evitar repetir Cierre
                model.Add(turno[(a, s, "Cierre")] + turno[(a, s + 1, "Cierre")] <= 1)
                # Evitar repetir Intermedio
                model.Add(turno[(a, s, "Intermedio")] + turno[(a, s + 1, "Intermedio")] <= 1)
                # Evitar repetir Apertura si NO hay un fijo
                if self.fijo == "Ninguno":
                    model.Add(turno[(a, s, "Apertura")] + turno[(a, s + 1, "Apertura")] <= 1)

        # -------------------------------------------------------------
        # Resolver
        # -------------------------------------------------------------
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 6
        solver.parameters.num_search_workers = 8

        try:
            result = solver.Solve(model)
        except Exception as e:
            raise RuntimeError(f"Error ejecutando CP-SAT: {e}")

        if result not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise RuntimeError("El modelo no tiene solución con las restricciones actuales.")

        # -------------------------------------------------------------
        # Construcción del DataFrame por fechas
        # -------------------------------------------------------------
        registros = []

        for fecha in fechas:
            dias = (fecha - fechas[0]).days
            semana = (dias // 7) + 1

            fila = {"Fecha": fecha}

            for t in self.turnos:
                for a in self.asesores:
                    if solver.Value(turno[(a, semana, t)]) == 1:
                        fila[t] = a

            registros.append(fila)

        return pd.DataFrame(registros)


