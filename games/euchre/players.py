import tensorflow as tf
import numpy as np
import os


class EuchreAgent(object):
    """Thing that has cards and can play them. Its main function is that it builds a NN that can evaluate euchre positions. NN output has 2 parts, tthe final layer has 2 blocks,
        one with size     0=pass, 1=club, 2=spade, 3=heart, 4=diamond, 5=club alone, 6=spade alone 7=heart alone, 8=diamond alone, 9="""
    def __init__(self, cards):
        self.cards = cards
        self.graph = tf.Graph()
        self.sess = tf.Session(graph=self.graph)
        self.

    def human_value(self):
        # returns a dict of the score for each suit ({suit:score})
        scores = {}
        for trump_suit in name_to_suit.values():
            self.trumpify(trump_suit)
            suit_score = 0
            has_best = False
            suits_encountered = []
            trump_cnt = 0
            off_aces = 0
            for trumped_card in self.deck:
                suit_score += trumped_card.val
                if trumped_card.val == RIGHT_VAL:    # having the right bonus
                    suit_score += 8.0
                    has_best = True
                elif trumped_card.real_val == name_to_vals['ace'] and not trumped_card.trump:  # having off aces bonus
                    off_aces += 1
                elif trumped_card.trump:        # trump bonus
                    suit_score += 2.5*trumped_card.val
                    trump_cnt += 1
                suits_encountered.append(trumped_card.suit)
            if has_best:
                if cards.LEFT_VAL in [dealt_card.val for dealt_card in self.deck]:  # bonus for having right + left (almost always make it on that, regardless of anything)
                    suit_score += 15.0
            uniq_suits = len(collections.Counter(suits_encountered))
            if trump_cnt >= 3:  # having 3 trump bonus
                suit_score += 15.0
                suit_score -= (uniq_suits-0.7*off_aces)*3.6     # having low numbers of suits bonus
                suit_score += 1.4*off_aces
            else:
                suit_score -= (uniq_suits-0.7*off_aces)*1.5
                suit_score += 2.1*off_aces
            if uniq_suits == 4:
                suit_score -= 10.    # additional penalty for having 4 suits (very bad)
            scores[trump_suit] = suit_score
            self.detrumpify()
        return scores



    def __repr__(self):
        return str(self.deck)


