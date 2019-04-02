class EloTable(object):
    def __init__(self, tname):
        self.tname = tname
        self.start_elo = 1500
        self.start_volatility = 19
        try:
            with open(tname, "r") as f:
                raw = f.readlines()
                self.table = {row.split('\t')[0]: row.split('\t')[1] for row in raw}
        except FileNotFoundError:
            print(f"Elo file {tname} not found, creating empty elo file")
            self.table = {}

    def get_elo(self, p):
        try:
            return self.table[p]
        except KeyError:
            return self.start_elo

    def save(self):
        str_table = [f"{str(k)}\t{str(v)}" for k,v in self.table.items()]
        with open(self.tname, "w") as f:
            f.write("\n".join(str_table))

    def update_elo(self, p1, p2, score):
        """Update elos, based on the score (which is in [0, 1] from elo1's point of view (ie. if elo1 won, score=+1)"""
        if score > 1:
            raise ValueError(f"Score for elos must be in [0,1], score was {score}!")
        p1_elo = self.get_elo(p1)
        p2_elo = self.get_elo(p2)
        p1_expected_score = 1 / (1 + (10 ** ((p2_elo - p1_elo) / 400)))
        p2_expected_score = 1 / (1 + (10 ** ((p1_elo - p2_elo) / 400)))
        p1_new_elo = p1_elo + self.start_volatility * (score - p1_expected_score)
        p2_new_elo = p2_elo + self.start_volatility * (abs(1 - score) - p2_expected_score)
        self.table[p1] = p1_new_elo
        self.table[p2] = p2_new_elo
        self.save()











