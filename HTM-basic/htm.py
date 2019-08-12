import numpy as np
import time
from PIL import Image
import cv2
import util_funcs
np.set_printoptions(precision=3)
np.random.seed(12)
NL = "\n"
TAB = "\t"

INPUT_SIZE = 50
NET_WIDTH = 25
NET_HEIGHT = 25
COL_HEIGHT = 4
NETWORK_SIZE = NET_WIDTH * NET_HEIGHT * COL_HEIGHT
MAX_SEGMENT_SIZE = 8
MIN_SEGMENT_SIZE = 2
NUM_PROXIMAL_INPUTS = 24
NUM_COLUMNS = NET_HEIGHT * NET_WIDTH
NUM_OUTPUTS_PER_CELL = 32

MIN_FF_OVERLAP = 12
MIN_PERM_CONNECTED = 0.5
INHIBITION_RADIUS = 64    # it wraps circularly around for stastical reasons (although this is nonsensical in normal brains)
DESIRED_ACTIVITY = 48     # its a winning col if its score is greater than score of 10th greatest column in inhibition radius
PERMANENCE_INC = 0.01
BOOSTING_WEIGHT = 0.99    # (=> an input wil decay to having 0.01 significance after 
BOOST_INC = 0.05


delete_flag = 10
add_flag = 20
class ProximalSynapse:
    def __init__(self, inpt_idx, column=None):
        self.column = column
        self.idx = inpt_idx
        self.activation = 0
        self.connected = 0

    def activate(self, inpt_idx):
        if self.connected:    # if it had a permanence value high enough and the input the synapse is linked to is activated, the synapse is activated
            if self.idx == inpt_idx:
                self.activation = 1
        else:
            self.activation = 0

    def increment_permanence(self):
        return self.set_permanence(self.permanence + PERMANENCE_INC)

    def decrement_permanence(self):
        return self.set_permanence(self.permanence - PERMANENCE_INC)

    def set_permanence(self, perm):
        self.permanence = max(min(1.0, perm), 0.0)
        if not self.connected and self.permanence > MIN_PERM_CONNECTED:     # if not connected before and should be connected now
            self.connected = 1
            return add_flag
        elif self.connected and self.permanence < MIN_PERM_CONNECTED:      # if connected before and shouldn't be connected now
            self.connected = 0
            return delete_flag
        else:
            return False

    def __repr__(self):
        return f"{TAB}ProximalSynapse(link={self.idx},perm={round(self.permanence,3)},act={self.activation},valid={self.connected})"


class ProximalSegment:
    def __init__(self, num_connections, column=None):
        center = column % INPUT_SIZE
        self.size = num_connections
        self.column = column
        self.idxs = util_funcs.rand_choice_center_fast(INPUT_SIZE, NUM_PROXIMAL_INPUTS, center)      #np.random.choice(INPUT_SIZE, num_connections, replace=False)
        perms = util_funcs.truncated_normal_perms(center, self.idxs, INPUT_SIZE)
        self.synapses = [ProximalSynapse(idx, column=self.column) for i, idx in enumerate(self.idxs)]
        for syn, perm in zip(self.synapses, perms):
            syn.set_permanence(perm)
        self.activation = 0

        sorted_synapses = sorted(self.synapses, key=lambda x: x.idx)
        self.valid_synapses = [x for x in sorted_synapses if x.connected]

    def get_overlap(self, inpt_idxs):
        self.apply_input(inpt_idxs)
        overlap = 0
        for syn in self.synapses:
            overlap += syn.activation
        return overlap

    def apply_input(self, inpt_idxs):
        for inpt_idx in inpt_idxs:
            for syn in self.synapses:
                syn.activate(inpt_idx)

    def update_synapses(self):
        for syn in self.synapses:
            if syn.activation:                # should always be called after self.apply_input(), then update permanences (if synapses got activated, increase it, else, decrease it)
                if syn.increment_permanence() == add_flag:    # ie. should be newly added 
                    self.valid_synapses.insert(util_funcs.binary_insert(self.valid_synapses, syn, key=lambda x: x.idx), syn)
            else:
                if syn.decrement_permanence() == delete_flag:
                    self.valid_synapses.pop(util_funcs.binary_find(self.valid_synapses, syn, key=lambda x: x.idx))

    def get_receptive_field(self):
        try:
            return util_funcs.modular_radius(self.valid_synapses, INPUT_SIZE, key=lambda x: x.idx)
        except IndexError:
            print("WORTHLESS COLUMN", self)
            return 0

    def __repr__(self):
        return f"ProximalSegment(size={self.size},act={self.activation},synapses={NL}{TAB}{(NL+TAB).join([str(syn) for syn in self.synapses])})"

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

class Cell:
    def __init__(self, loc, region, post_cells, column):   # Network randomly provides cells for Cell to be its output
        self.column = column
        self.region = region
        self.post_cells = post_cells
        self.segments = []
        self.loc = loc     # this is a 3-vector of (x, y, col_height)
        self.activation = 0     # can take values 0, 1e-8, 1  to be (inactive, predictive, active)
        self.ff_act = 0

    def next_segment(self):
        for seg in self.segments:
            if seg.size < MAX_SEGMENT_SIZE:
                return seg
        new_seg = DistalSegment(self)
        self.segments.append(new_seg)
        return new_seg

    def link_distal(self):
        for post_loc in self.post_cells:   # for out in outputs
            post_seg = self.region.cells[post_loc].next_segment()    # for segment to link up to 
            post_seg.link_inputs(self)     # since this is the outputting cell, it is the pre_cell

    def link_proximal(self, proximal_seg):
        self.proximal = proximal_seg

    def feed_forward(self, inpt_idxs):
        self.proximal.apply_input(inpt_idxs)
        activation, overlap = self.proximal.activate()
        if activation:
            self.ff_act = overlap
        else:
            self.ff_act = 0

    def prune(self):
        bad_idxs = []
        for idx, seg in enumerate(self.segments):
            if seg.size < MIN_SEGMENT_SIZE:
                bad_idxs.append(idx)
        for bad_idx in bad_idxs[::-1]:
            del self.segments[bad_idx]

    def __repr__(self):
        return f"Cell(col={self.column},loc={self.loc},outs={self.post_cells},prox_seg={self.proximal},dist_segs={NL}{TAB}{(NL+TAB).join([str(seg) for seg in self.segments])})"

class Column:
    def __init__(self, cell_list, col_idx, region_ref):
        self.region_ref = region_ref
        self.cells = cell_list
        self.loc = col_idx
        self.overlap = 0
        self.boost_factor = 1.0
        self.activity = 0    # activity should be in [0,1]
        self.overlap_freq = 0

    def link_proximal(self):
        proximal_seg = ProximalSegment(NUM_PROXIMAL_INPUTS, column=self.loc)
        self.proximal = proximal_seg
        for cell in self.cells:
            cell.link_proximal(proximal_seg)

    def overlap_input(self, inpt_idxs):
        overlap = self.proximal.get_overlap(inpt_idxs)
        if overlap < MIN_FF_OVERLAP:
            self.overlap = 0
            self.overlap_freq *= BOOSTING_WEIGHT
        else:
            self.overlap_freq = self.overlap_freq*BOOSTING_WEIGHT + (1-BOOSTING_WEIGHT)
            self.overlap = overlap * self.boost_factor

    def activate(self):
        for cell in self.cells:
            cell.activation = 1
            self.activity = self.activity*BOOSTING_WEIGHT + (1-BOOSTING_WEIGHT) * 1
        self.proximal.update_synapses()

    def not_activate(self):
        self.activity = self.activity*BOOSTING_WEIGHT

    def inhibit(self, sliding_window, sorted_window, add_val):
        del_val = sliding_window.pop(0)
        sliding_window.append(add_val)
        sorted_window.remove(del_val)
        sorted_window.insert(util_funcs.binary_insert(sorted_window, add_val), add_val)
        if self.overlap and self.overlap >= sorted_window[DESIRED_ACTIVITY]:
            self.activate()
        else:
            self.not_activate()

    def boost(self, sliding_window, sorted_window, add_val):
        del_val = sliding_window.pop(0)
        sliding_window.append(add_val)
        sorted_window.remove(del_val)
        sorted_window.insert(util_funcs.binary_insert(sorted_window, add_val), add_val)

        min_activity = sorted_window[0] * 0.01
        if self.activity >= min_activity:
            self.boost_factor = 1.0
        else:
            self.boost_factor += BOOST_INC

        if self.overlap_freq < min_activity:
            for syn in self.proximal.synapses:
                syn.permanence += 0.1 * MIN_PERM_CONNECTED

    def get_receptive_field(self):
        return self.proximal.get_receptive_field()

    def __repr__(self):
        return f"Column(loc={self.loc}, cells={[x.loc for x in self.cells]}, overlap={self.overlap}, proximal_seg={self.proximal})"

class Region:
    def __init__(self):
        #self.grid = grid
        self.linked = False
        self.cells = np.empty(NETWORK_SIZE, dtype=Cell)
        full_neighbourhood = np.arange(NETWORK_SIZE)
        print("Initializing network of size", NETWORK_SIZE, "...")
        pct = 0.05
        next_pct = 0.0
        print(" "*6, end='', flush=True)
        for lin_loc in range(NETWORK_SIZE):  #self.grid is shape (HEIGHT*WIDTH*COL_HEIGHT, 3) so you do like grid[523]->(5, 5, 3) [523//(25*4), (523%100)//4, 523%4]
            neighbourhood = np.concatenate((full_neighbourhood[:lin_loc], full_neighbourhood[lin_loc+1:]), 0)
            post_cells = np.random.choice(neighbourhood, size=(NUM_OUTPUTS_PER_CELL), replace=True)
            self.cells[lin_loc] = Cell(lin_loc, self, post_cells, lin_loc//4)
            if float(lin_loc)/NETWORK_SIZE >= next_pct:
                print("\b\b\b\b\b\b# | %02d%%" % (int(100*float(lin_loc)/NETWORK_SIZE)), end='', flush=True)
                next_pct += pct
        print("\b\b\b\b\b\b# | 100%")
        print("Linking distal connections...")
        self.link()
        print("Pruning empty segments...")
        self.prune()

        self.inputs_to_cells = None
        cols_np = self.cells.reshape(NUM_COLUMNS, COL_HEIGHT)
        self.cols = np.empty(NUM_COLUMNS, dtype=Column)
        for i, col_np in enumerate(cols_np):
            self.cols[i] = Column(col_np, i, self)
        self.link_cols()

    def visualize(self):
        reshaped = self.cells.reshape(NET_WIDTH, NET_HEIGHT, COL_HEIGHT).swapaxes(0,-1)
        for col_layer in reshaped:
            img = np.zeros_like(col_layer).astype(np.uint8)
            for x,row in enumerate(col_layer):
                for y,cell in enumerate(row):
                    if cell.activation:
                        if cell.activation == 1:
                            img[x,y] = 255
                        else:
                            img[x,y] = 128
            #img_resize = cv2.resize(img, (1024, 1024), interpolation=cv2.INTER_NEAREST)
            pil_img = Image.fromarray(img, "L")
            #pil_img = Image.fromarray(img_resize, "L")
            pil_img.show()


    def apply_input(self, idxs):
        for col in self.cols:
            col.overlap_input(idxs)

    def inhibit(self):
        sliding_window = [x.overlap for x in np.take(self.cols, range(-INHIBITION_RADIUS//2, INHIBITION_RADIUS//2))]
        sorted_window = list(sorted(sliding_window))
        for loc, col in enumerate(self.cols):
            add_val = self.cols[(loc+INHIBITION_RADIUS//2)%len(self.cols)].overlap
            col.inhibit(sliding_window, sorted_window, add_val)

    def boost(self):
        global INHIBITION_RADIUS
        sliding_window = [x.activity for x in np.take(self.cols, range(-INHIBITION_RADIUS//2, INHIBITION_RADIUS//2))]
        sorted_window = list(sorted(sliding_window))
        for loc, col in enumerate(self.cols):
            add_val = self.cols[(loc+INHIBITION_RADIUS//2)%len(self.cols)].activity
            col.boost(sliding_window, sorted_window, add_val)
        INHIBITION_RADIUS = int(self.average_receptive_field())

    def average_receptive_field(self):
        total = 0
        for col in self.cols:
            total += col.get_receptive_field()
        return float(total) / NUM_COLUMNS


    def link_cols(self):
        for col in self.cols:
            col.link_proximal()

    def link(self):
        if not self.linked:
            for cell in self.cells:
                #cell.link_distal()
                pass
            self.linked = True

    def prune(self):
        for cell in self.cells:
            cell.prune()

def main():
    #grid_region = np.mgrid[0:NET_WIDTH, 0:NET_HEIGHT, 0:COL_HEIGHT].reshape(3,-1).T#.swapaxes(0,-1).swapaxes(0,2).swapaxes(0,1)
    cell_region = Region()
    print(cell_region.cells[49])
    print(f"{'#'*100}\n"*3,end='')
    print(cell_region.cols[12])
    print(f"{'#'*100}\n"*3,end='')
    #cell_region.cells[123].activation = 1
    #cell_region.cells[124].activation = 1
    #cell_region.cells[125].activation = 1
    cell_region.apply_input(np.random.choice(INPUT_SIZE, size=18, replace=False))
    #cell_region.visualize()
    #input()
    cell_region.inhibit()
    #cell_region.visualize()
    #input()
    cell_region.boost()
    print(INHIBITION_RADIUS)
    cell_region.visualize()


if __name__ == "__main__":
    main()

