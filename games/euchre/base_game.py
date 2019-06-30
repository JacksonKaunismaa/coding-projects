import cards
import random
import collections
import hand

def build_deck():
    buffer_deck = []
    for suit_val in cards.name_to_suit.values():
        for val_val in cards.name_to_vals.values():
            buffer_deck.append(cards.Card(f"{cards.vals_to_name[val_val]} of {cards.suit_to_name[suit_val]}", val_val, suit_val))
    return hand.Hand(buffer_deck)


deck = build_deck()
for _ in range(5):
    hands = deck.deal_deck(5)
    for hand in hands:
        print(hand)
        results = hand.human_value()
        good_results = {cards.suit_to_name[suit]:val for suit,val in results.items()}
        print(good_results)
    print("#"*100)
    deck.collect_hands(hands)














