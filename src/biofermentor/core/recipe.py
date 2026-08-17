class Recipe:
    def __init__(self, p):
        self.phases = [
            {"name": "Inóculo / adaptação", "start": 0.0, "end": 2.0,
             "feed": False, "DO_sp": 35.0},
            {"name": "Crescimento batch", "start": 2.0, "end": p["feed_start"],
             "feed": False, "DO_sp": 30.0},
            {"name": "Fed-batch produção", "start": p["feed_start"], "end": p["tf"]+1e-12,
             "feed": True, "DO_sp": 25.0},
        ]

    def phase_at(self, t):
        for phase in self.phases:
            if phase["start"] <= t < phase["end"]:
                return phase
        return self.phases[-1]
