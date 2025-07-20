def shuffle_deck(deck):
    import random
    random.shuffle(deck)
    return deck

def display_game_state(player_hand, dealer_hand, player_score, dealer_score):
    print("Player's Hand:", player_hand, "Score:", player_score)
    print("Dealer's Hand:", dealer_hand, "Score:", dealer_score)