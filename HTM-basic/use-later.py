class DistalSynapse:
    def __init__(self, pre_cell, post_seg):
        self.pre_cell = pre_cell
        self.post_seg = post_seg
        self.permanence = np.random.uniform(low=0.4, high=0.6, size=1)[0]
        self.activation = 0
        self.connected = 1 if self.permanence > MIN_PERM_CONNECTED else 0

    def activate(self):
        if self.connected:
            if self.pre_cell.activation:
                self.activation = 1
        else:
            self.activation = 0

    def __repr__(self):
        return f"{TAB}DistalSynapse(pre_loc={self.pre_cell.loc},post_loc={self.post_seg.cell.loc},perm={round(self.permanence,3)},act={self.activation},valid={self.connected})"

class DistalSegment:    # receiver node
    def __init__(self, post_cell):
        self.size = 0 #len(pre_connections)
        self.cell = post_cell
        self.synapses = []
        self.activation = 0

    def activate(self):
        overlap = 0
        for syn in self.synapses:
            overlap += syn.activation
        overlap *= 2
        if overlap > MIN_FF_OVERLAP:
            self.activation = 1
        else:
            self.activation = 0

    def apply_input(self, idxs):
        for idx in idxs:
            if idx in self.idxs:
                for syn in self.synapses:
                    syn.activate(idx)

    def link_inputs(self, pre_cell):
        self.synapses.append(DistalSynapse(pre_cell, self))
        self.size += 1

    def __repr__(self):
        return "DistalSegment(size={},act={},synapses=\n\t{})".format(self.size, self.activation, "\n\t".join([str(syn) for syn in self.synapses]))

