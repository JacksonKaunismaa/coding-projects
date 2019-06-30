import random
import collections

suit_to_name = {0: "diamonds", 1: "spades", 2: "hearts", 3: "clubs"}
name_to_suit = {y:x for x,y in suit_to_name.items()}
vals_to_name = {0: "9", 1: "10", 2: "jack", 3: "queen", 4: "king", 5: "ace"}
name_to_vals = {y:x for x,y in vals_to_name.items()}
TRUMP_INCR = 7
RIGHT_VAL = TRUMP_INCR + len(vals_to_name.keys()) + 1
LEFT_VAL = RIGHT_VAL - 1


class Card():
    def __init__(self, name, val, suit):
        self.name = name
        self.val = val
        self.real_val = val    # real_val is the underlying value that never changes (ie. a jack is always real_val 2, regardless of trump)
        self.suit = suit
        self.trump = False

    def get_trump_changes(self, suit):
        if self.val == name_to_vals['jack']:
            if self.suit == suit:
                self.trump = True
                return RIGHT_VAL-self.val
            elif self.suit&1 == suit&1:
                self.trump = True
                return LEFT_VAL-self.val
            return 0
        elif self.suit == suit:
            self.trump = True
            return TRUMP_INCR
        return 0

    def trumpify(self, suit):
        chng = self.get_trump_changes(suit)
        self.val += chng

    def detrumpify(self):
        self.trump = False
        self.val = self.real_val

    def __gt__(self, other):
        return self.val > other.val
    def __lt__(self, other):
        return self.val < other.val
    def __repr__(self):
        return f"Card(n='{self.name}',v={self.val},s={self.suit})"


class Hand(object):
    def __init__(self, all_cards):
        self.deck = all_cards
        self.size = len(self.deck)

    def trumpify(self, trump_suit):
        for untrumped_card in self.deck:
            untrumped_card.trumpify(trump_suit)

    def detrumpify(self):
        for trumped_card in self.deck:
            trumped_card.detrumpify()

    def deal_deck(self, hands_num):
        # returns a list of Hand of Card objects with each sublist being a Hand, including a final Hand with all leftover cards (variable size based on deck size and num_hands)
        random.shuffle(self.deck)  # shuffle deck
        hand_size = -((-self.size)//hands_num)   # extremely sketchy way to do ceiling division
        dealt_hands = [Hand(self.deck[x*hand_size:(x+1)*hand_size]) for x in range(hands_num)]
        return dealt_hands

    def collect_hands(self, dealt_hands):
        # given a list of Hand objects, it unpacks them and restores them in one large Hand object
        rebuild_deck = [dealt_card for dealt_hand in dealt_hands for dealt_card in dealt_hand.deck]
        self.deck = rebuild_deck
        self.detrumpify()

    def __repr__(self):
        return str(self.deck)

