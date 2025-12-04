from datetime import date, timedelta
from scheduler import Scheduler


def next_monday():
    today = date.today()
    return today + timedelta(days=(7 - today.weekday()) % 7)


def test_scheduler_basic():
    sched = Scheduler(
        advisors=["A1", "A2", "A3"],
        start_date=next_monday(),
        holidays=[]
    )
    res = sched.solve()

    df = res["raw"]

    # Debe haber tantos días como días laborales (no domingos)
    for d in df["date"].unique():
        assert d.weekday() != 6

    # Cada día, 3 turnos
    for d in df["date"].unique():
        rows = df[df["date"] == d]
        assert len(rows) == 3
        assert set(rows["turno"]) == {"Apertura", "Cierre", "Intermedio"}


def test_fixed_opening():
    sched = Scheduler(
        advisors=["A1", "A2", "A3"],
        start_date=next_monday(),
        holidays=[],
        fixed_opening_worker="A3"
    )
    res = sched.solve()

    df = res["raw"]
    rows = df[df["asesor"] == "A3"]

    assert all(rows["turno"] == "Apertura")

