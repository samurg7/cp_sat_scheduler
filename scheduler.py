from ortools.sat.python import cp_model
import pandas as pd
from datetime import date, timedelta


class SchedulerError(Exception):
    """Errores propios del planificador."""
    pass


class Scheduler:
    TURNS = {
        0: "Apertura",
        1: "Cierre",
        2: "Intermedio"
    }

    def __init__(
        self,
        advisors,
        start_date,
        holidays=None,
        fixed_opening_worker=None,
    ):
        if len(advisors) != 3:
            raise SchedulerError("El modelo requiere exactamente 3 asesores.")

        self.advisors = advisors
        self.start_date = start_date
        self.holidays = set(holidays or [])
        self.fixed_opening_worker = fixed_opening_worker

        self.days = self._generate_days()

        if not self.days:
            raise SchedulerError("No hay días laborales disponibles.")

    def _generate_days(self):
        """Genera los 7 días de la semana, excluyendo domingos y festivos."""
        days = []
        for i in range(7):
            d = self.start_date + timedelta(days=i)
            if d.weekday() == 6:  # domingo
                continue
            if d in self.holidays:
                continue
            days.append(d)
        return days

    def solve(self):
        model = cp_model.CpModel()

        x = {}

        # Variables: x[a][d][t]
        for a in range(3):
            for d in range(len(self.days)):
                for t in range(3):
                    x[(a, d, t)] = model.NewBoolVar(f"x_a{a}_d{d}_t{t}")

        # REGLA 1: Cada asesor tiene un único turno por semana
        turno_asignado = {}
        for a in range(3):
            for t in range(3):
                turno_asignado[(a, t)] = model.NewBoolVar(f"turno_a{a}_t{t}")

            model.Add(sum(turno_asignado[(a, t)] for t in range(3)) == 1)

        # Vincular turno semanal con los días
        for a in range(3):
            for d in range(len(self.days)):
                model.Add(sum(x[(a, d, t)] for t in range(3)) == 1)
                for t in range(3):
                    model.Add(x[(a, d, t)] >= turno_asignado[(a, t)])
                    model.Add(x[(a, d, t)] <= turno_asignado[(a, t)])

        # REGLA 2: Cada turno solo lo cubre 1 asesor por día
        for d in range(len(self.days)):
            for t in range(3):
                model.Add(sum(x[(a, d, t)] for a in range(3)) == 1)

        # REGLA 3 (opcional): asesora fija solo en apertura
        if self.fixed_opening_worker:
            idx = self.advisors.index(self.fixed_opening_worker)

            model.Add(turno_asignado[(idx, 0)] == 1)
            model.Add(turno_asignado[(idx, 1)] == 0)
            model.Add(turno_asignado[(idx, 2)] == 0)

        # Resolver
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10

        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise SchedulerError("No se encontró solución viable.")

        rows = []
        for d_idx, day in enumerate(self.days):
            for a_idx, asesor in enumerate(self.advisors):
                for t in range(3):
                    if solver.Value(x[(a_idx, d_idx, t)]) == 1:
                        rows.append({
                            "date": day,
                            "asesor": asesor,
                            "turno_id": t,
                            "turno": self.TURNS[t]
                        })

        df = pd.DataFrame(rows)
        pivot = df.pivot(index="date", columns="turno", values="asesor").reset_index()

        return {
            "raw": df,
            "pivot": pivot
        }

