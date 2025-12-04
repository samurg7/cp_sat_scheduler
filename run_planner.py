from datetime import date
from scheduler import Scheduler

if __name__ == "__main__":
    advisors = ["A1", "A2", "A3"]

    s = Scheduler(
        advisors=advisors,
        start_date=date.today(),
        holidays=[]
    )

    result = s.solve()
    print(result["pivot"])
    result["pivot"].to_csv("resultado.csv", index=False)
    print("Archivo resultado.csv generado.")

