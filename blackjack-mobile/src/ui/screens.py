class Screen:
    def show_main_menu(self):
        print("Welcome to Blackjack!")
        print("1. Start Game")
        print("2. Exit")

    def update_game_display(self, player_hand, dealer_hand, player_score, dealer_score):
        print(f"Player's Hand: {player_hand} (Score: {player_score})")
        print(f"Dealer's Hand: {dealer_hand} (Score: {dealer_score})")