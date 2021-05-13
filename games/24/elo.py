import math
import numpy as np

class EloTable(object):
    def __init__(self, tname):
        self.tname = tname
        self.start_elo = 1550
        self.start_volatility = 25
        self.player_name = "player-elo"
        self.performance = 1500
        try:
            with open(self.tname, "r") as f:
                raw = f.readlines()
                self.table = {row.split('\t')[0]: float(row.split('\t')[1]) for row in raw}
        except FileNotFoundError:
            print(f"Elo file {tname} not found, creating empty elo file")
            self.table = {}

        try:
            with open(self.tname+".record", "r") as f:
                raw = f.readlines()
                self.records = {row.split('\t')[0]: [float(x) for x in row.split('\t')[1].split(",")] for row in raw}
        except FileNotFoundError:
            self.records = {}

    def get_rand_elo(self):
        return np.random.normal(self.start_elo, 50)


    def get_elo(self, p):
        try:
            return self.table[p]
        except KeyError:
            return self.get_rand_elo()

    def get_record(self, p):
        try:
            return self.records[p]
        except KeyError:
            return None

    def record_save(self):
        record_write = []
        for name, new_e in self.table.items():
            get_record = self.get_record(name)
            try:
                round_new = float("%.2f" % new_e)
            except TypeError:
                print("name", name)
                print("new_e", new_e)
                print("type(new_e)", type(new_e))
                print("type(name", type(name))
                print("get_record", get_record)
                raise
            if get_record is None:                                 # if new puzzle encountered that has no records so far, create new entry
                record_write.append(f"{name}\t{'%.2f' % new_e}")
            elif not math.isclose(self.get_record(name)[-1], round_new):   # if record exists and was encountered in session, append entry
                self.records[name].append("%.2f" % new_e)
                record_write.append(f"{name}\t{','.join([str(x) for x in self.records[name]])}")
            else:                                                       # in no changes made in elo table, we stil need to save it, just dont add a new entry
                record_write.append(f"{name}\t{','.join([str(x) for x in self.records[name]])}")
        with open(self.tname+".record", "w") as f:
            f.write('\n'.join(record_write))

    def save(self):
        str_table = [f"{str(k)}\t{str(v)}" for k,v in self.table.items()]
        with open(self.tname, "w") as f:
            f.write("\n".join(str_table))

    def update_player(self, p, score):
        """Score are from the player's point of view, so if player wins, score should be +1)"""
        old_elo = self.get_elo(self.player_name)
        new_elo, _ = self.update_elo(self.player_name, p, score, volatility1=25)
        self.performance += (new_elo - old_elo)

    def update_elo(self, p1, p2, score, volatility1=None, volatility2=None):
        """Update elos, based on the score (which is in [0, 1] from elo1's point of view (ie. if elo1 won, score=+1)"""
        if score > 1:
            raise ValueError(f"Score for elos must be in [0,1], score was {score}!")

        if volatility1 is None:
            volatility1 = self.start_volatility
        if volatility2 is None:
            volatility2 = self.start_volatility

        p1_elo = self.get_elo(p1)
        p2_elo = self.get_elo(p2)
        p1_expected_score = 1 / (1 + (10 ** ((p2_elo - p1_elo) / 400)))
        p2_expected_score = 1 / (1 + (10 ** ((p1_elo - p2_elo) / 400)))
        p1_new_elo = p1_elo + volatility1 * (score - p1_expected_score)
        p2_new_elo = p2_elo + volatility2 * (abs(1 - score) - p2_expected_score)
        self.table[p1] = p1_new_elo
        self.table[p2] = p2_new_elo
        self.save()
        return p1_new_elo, p2_new_elo










