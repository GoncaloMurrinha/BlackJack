from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.core.audio import SoundLoader
import random
import os

CARDS_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'cards')

class BlackjackGame:
    def __init__(self, num_players=2, starting_balance=1000, bet=100):
        self.num_players = num_players
        self.starting_balance = starting_balance
        self.bet = bet
        self.reset_game()

    def reset_game(self):
        self.deck = self.create_deck()
        self.players = [{'hand': [], 'balance': self.starting_balance} for _ in range(self.num_players)]
        self.dealer_hand = []
        self.current_player = 0
        self.in_progress = False

    def create_deck(self):
        suits = ['H', 'D', 'S', 'C']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [v + s for v in values for s in suits]
        random.shuffle(deck)
        return deck

    def deal(self):
        for player in self.players:
            player['hand'] = [self.deck.pop(), self.deck.pop()]
            player['balance'] -= self.bet
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.in_progress = True
        self.current_player = 0

    def hit(self, player_idx):
        self.players[player_idx]['hand'].append(self.deck.pop())

    def stand(self):
        self.current_player += 1

    def dealer_play(self):
        while self.calculate_score(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())

    def calculate_score(self, hand):
        value = 0
        aces = 0
        for card in hand:
            v = card[:-1]
            if v in ['J', 'Q', 'K']:
                value += 10
            elif v == 'A':
                value += 11
                aces += 1
            else:
                value += int(v)
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def finish_round(self):
        self.dealer_play()
        dealer_total = self.calculate_score(self.dealer_hand)
        results = []
        for player in self.players:
            player_total = self.calculate_score(player['hand'])
            if player_total > 21:
                results.append("Perdeu!")
            elif dealer_total > 21 or player_total > dealer_total:
                results.append("Ganhou!")
                player['balance'] += self.bet * 2
            elif dealer_total > player_total:
                results.append("Dealer venceu")
            else:
                results.append("Empate")
                player['balance'] += self.bet
        self.in_progress = False
        return results

class CardImages(BoxLayout):
    def __init__(self, cards, reveal_all=True, **kwargs):
        super().__init__(orientation='horizontal', spacing=5, **kwargs)
        for idx, card in enumerate(cards):
            if card == '??' or (not reveal_all and idx > 0):
                self.add_widget(Image(source=os.path.join(CARDS_PATH, 'back.png'), size_hint=(None, None), size=(60, 90)))
            else:
                img_path = os.path.join(CARDS_PATH, f"{card}.png")
                if not os.path.exists(img_path):
                    img_path = os.path.join(CARDS_PATH, 'back.png')
                self.add_widget(Image(source=img_path, size_hint=(None, None), size=(60, 90)))

class BlackjackApp(App):
    def build(self):
        self.game = BlackjackGame(num_players=2)
        self.root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.status = Label(text="Clique em 'Novo Jogo' para começar")
        self.root.add_widget(self.status)
        self.btn_new_game = Button(text="Novo Jogo", on_press=self.new_game)
        self.root.add_widget(self.btn_new_game)
        self.btn_hit = Button(text="Hit", on_press=self.hit, disabled=True)
        self.root.add_widget(self.btn_hit)
        self.btn_stand = Button(text="Stand", on_press=self.stand, disabled=True)
        self.root.add_widget(self.btn_stand)
        self.players_hands = []
        self.players_labels = []
        self.players_scores = []
        self.players_balances = []
        self.players_layout = GridLayout(cols=1, size_hint_y=None)
        self.players_layout.bind(minimum_height=self.players_layout.setter('height'))
        for i in range(self.game.num_players):
            player_box = BoxLayout(orientation='vertical', size_hint_y=None, height=120)
            label = Label(text=f"Jogador {i+1}")
            player_box.add_widget(label)
            hand = CardImages([])
            player_box.add_widget(hand)
            score = Label(text="Score: 0")
            player_box.add_widget(score)
            balance = Label(text=f"Saldo: {self.game.starting_balance}")
            player_box.add_widget(balance)
            self.players_labels.append(label)
            self.players_hands.append(hand)
            self.players_scores.append(score)
            self.players_balances.append(balance)
            self.players_layout.add_widget(player_box)
        self.root.add_widget(self.players_layout)
        # Dealer
        self.dealer_label = Label(text="Dealer")
        self.root.add_widget(self.dealer_label)
        self.dealer_hand = CardImages([])
        self.root.add_widget(self.dealer_hand)
        self.dealer_score = Label(text="Score: 0")
        self.root.add_widget(self.dealer_score)
        # Sound placeholder
        self.sound_win = None
        self.sound_lose = None
        self.sound_card = None
        return self.root

    def play_sound(self, sound_type):
        # Placeholder for sound logic
        # Example: self.sound_win = SoundLoader.load('assets/sounds/win.wav')
        pass

    def new_game(self, instance):
        self.game.reset_game()
        self.game.deal()
        self.status.text = f"Jogador 1: Sua vez! Hit ou Stand?"
        self.btn_hit.disabled = False
        self.btn_stand.disabled = False
        self.btn_new_game.disabled = True
        self.update_hands()

    def hit(self, instance):
        idx = self.game.current_player
        self.game.hit(idx)
        self.update_hands()
        if self.game.calculate_score(self.game.players[idx]['hand']) > 21:
            self.status.text = f"Jogador {idx+1} perdeu! Próximo jogador..."
            self.play_sound('lose')
            self.next_player_or_end()

    def stand(self, instance):
        idx = self.game.current_player
        self.status.text = f"Jogador {idx+1} parou. Próximo jogador..."
        self.next_player_or_end()

    def next_player_or_end(self):
        self.game.stand()
        if self.game.current_player >= self.game.num_players:
            self.end_round()
        else:
            self.status.text = f"Jogador {self.game.current_player+1}: Sua vez! Hit ou Stand?"
            self.update_hands()

    def end_round(self):
        results = self.game.finish_round()
        self.update_hands(reveal_dealer=True)
        result_text = "\n".join([f"Jogador {i+1}: {results[i]}" for i in range(self.game.num_players)])
        self.status.text = f"Resultado:\n{result_text}"
        self.btn_hit.disabled = True
        self.btn_stand.disabled = True
        self.btn_new_game.disabled = False
        # Play win/lose sounds if you want

    def update_hands(self, reveal_dealer=False):
        # Update players
        for i, player in enumerate(self.game.players):
            self.players_layout.remove_widget(self.players_hands[i])
            hand_widget = CardImages(player['hand'])
            self.players_hands[i] = hand_widget
            self.players_layout.add_widget(hand_widget, index=2*i+1)
            self.players_scores[i].text = f"Score: {self.game.calculate_score(player['hand'])}"
            self.players_balances[i].text = f"Saldo: {player['balance']}"
            if i == self.game.current_player and self.btn_hit.disabled is False:
                self.players_labels[i].text = f"Jogador {i+1} (Sua vez)"
            else:
                self.players_labels[i].text = f"Jogador {i+1}"
        # Update dealer
        if reveal_dealer:
            self.root.remove_widget(self.dealer_hand)
            self.dealer_hand = CardImages(self.game.dealer_hand)
            self.root.add_widget(self.dealer_hand, index=len(self.root.children)-2)
            self.dealer_score.text = f"Score: {self.game.calculate_score(self.game.dealer_hand)}"
        else:
            self.root.remove_widget(self.dealer_hand)
            dealer_cards = [self.game.dealer_hand[0], '??'] if self.game.dealer_hand else []
            self.dealer_hand = CardImages(dealer_cards, reveal_all=False)
            self.root.add_widget(self.dealer_hand, index=len(self.root.children)-2)
            self.dealer_score.text = "Score: ?"

if __name__ == '__main__':
    BlackjackApp().run()
