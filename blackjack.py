import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
import pygame
import os

pygame.mixer.init()

class BlackjackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack")
        self.root.configure(bg="#0b5123")
        self.root.resizable(False, False)
        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.balance = 1000
        self.current_bet = 100

        self.images = {}
        self.card_back_image = self.load_image("back")

        # Title
        title = tk.Label(root, text="BLACKJACK", font=("Arial", 24, "bold"), fg="white", bg="#0b5123")
        title.pack(pady=10)

        # Dealer
        self.dealer_frame = tk.Frame(root, bg="#0b5123")
        self.dealer_frame.pack(pady=10)
        self.dealer_label = tk.Label(root, text="Dealer", font=("Arial", 14, "bold"), fg="white", bg="#0b5123")
        self.dealer_label.pack()
        self.dealer_points = tk.Label(root, text="", font=("Arial", 12), fg="white", bg="#0b5123")
        self.dealer_points.pack()

        # Separator
        ttk.Separator(root, orient="horizontal").pack(fill="x", padx=40, pady=5)

        # Player
        self.player_label = tk.Label(root, text="You", font=("Arial", 14, "bold"), fg="white", bg="#0b5123")
        self.player_label.pack()
        self.player_frame = tk.Frame(root, bg="#0b5123")
        self.player_frame.pack(pady=10)
        self.player_points = tk.Label(root, text="", font=("Arial", 12), fg="white", bg="#0b5123")
        self.player_points.pack()

        # Status
        self.status = tk.Label(root, text="Click 'New Game' to start", font=("Arial", 12), fg="white", bg="#0b5123")
        self.status.pack(pady=5)

        # Balance
        self.balance_label = tk.Label(root, text=f"Balance: ${self.balance}", font=("Arial", 12), fg="white", bg="#0b5123")
        self.balance_label.pack()

        # Buttons
        button_frame = tk.Frame(root, bg="#0b5123")
        button_frame.pack(pady=20)

        self.btn_new_game = ttk.Button(button_frame, text="New Game", command=self.new_game)
        self.btn_new_game.grid(row=0, column=0, padx=10)

        self.btn_hit = ttk.Button(button_frame, text="Hit", command=self.hit, state=tk.DISABLED)
        self.btn_hit.grid(row=0, column=1, padx=10)

        self.btn_stand = ttk.Button(button_frame, text="Stand", command=self.stand, state=tk.DISABLED)
        self.btn_stand.grid(row=0, column=2, padx=10)

    def update_points_labels(self, reveal_dealer=False):
        player_score = self.calculate_score(self.player_hand)
        self.player_points.config(text=f"{player_score} / 21")

        if reveal_dealer:
            dealer_score = self.calculate_score(self.dealer_hand)
        else:
            dealer_score = self.calculate_score(self.dealer_hand[1:])

        self.dealer_points.config(text=f"{dealer_score} / 21")

    def play_sound(self, name, duration_ms=None):
        try:
            path = os.path.join("sons", name)
            sound = pygame.mixer.Sound(path)
            channel = sound.play()
            if duration_ms:
                self.root.after(duration_ms, channel.stop)
        except:
            pass

    def card_to_filename(self, card):
        value_map = {
            '2': '2', '3': '3', '4': '4', '5': '5', '6': '6',
            '7': '7', '8': '8', '9': '9', '10': '10',
            'J': 'jack', 'Q': 'queen', 'K': 'king', 'A': 'ace'
        }
        suit_map = {
            'H': 'hearts', 'D': 'diamonds', 'S': 'spades', 'C': 'clubs'
        }

        if card[:-1] == '10':
            value = '10'
            suit = card[-1]
        else:
            value = card[0]
            suit = card[1]

        return f"{value_map[value]}_of_{suit_map[suit]}"

    def load_image(self, card):
        if card == "back":
            filename = "back"
        else:
            filename = self.card_to_filename(card)

        path = os.path.join("cartas", f"{filename}.png")
        if path not in self.images:
            image = Image.open(path).resize((72, 96))
            self.images[path] = ImageTk.PhotoImage(image)
        return self.images[path]

    def show_hand(self, frame, hand, hide_first=False):
        for widget in frame.winfo_children():
            widget.destroy()
        for i, card in enumerate(hand):
            if i == 0 and hide_first:
                img = self.card_back_image
            else:
                img = self.load_image(card)
            lbl = tk.Label(frame, image=img, bg="#0b5123")
            lbl.image = img
            lbl.pack(side=tk.LEFT, padx=5)

    def create_deck(self):
        suits = ['H', 'D', 'S', 'C']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [v + s for v in values for s in suits]
        random.shuffle(deck)
        return deck

    def shuffle_animation(self, callback):
        self.status.config(text="Shuffling deck...")
        self.play_sound("shuffling-cards.wav", duration_ms=2000)

        def flash(i):
            if i >= 10:
                callback()
                return
            lbl = tk.Label(self.dealer_frame, image=self.card_back_image, bg="#0b5123")
            lbl.pack(side=tk.LEFT, padx=2)
            self.root.after(100, lambda: [lbl.destroy(), self.root.after(50, lambda: flash(i + 1))])

        flash(0)

    def deal_cards_animation(self):
        self.status.config(text="Dealing cards...")
        self.play_sound("playing-cards-being-dealt.wav", duration_ms=2000)
        self.player_hand = []
        self.dealer_hand = []

        def deal(index):
            if index == 0:
                self.player_hand.append(self.deck.pop())
            elif index == 1:
                self.dealer_hand.append(self.deck.pop())
            elif index == 2:
                self.player_hand.append(self.deck.pop())
            elif index == 3:
                self.dealer_hand.append(self.deck.pop())
            else:
                self.show_hand(self.player_frame, self.player_hand)
                self.show_hand(self.dealer_frame, self.dealer_hand, hide_first=True)
                self.update_points_labels(reveal_dealer=False)
                self.status.config(text="Your turn...")
                self.btn_hit.config(state=tk.NORMAL)
                self.btn_stand.config(state=tk.NORMAL)
                return

            self.show_hand(self.player_frame, self.player_hand)
            self.show_hand(self.dealer_frame, self.dealer_hand, hide_first=True)
            self.root.after(400, lambda: deal(index + 1))

        deal(0)

    def new_game(self):
        if self.balance < self.current_bet:
            self.status.config(text="Insufficient balance!")
            return

        self.deck = self.create_deck()
        self.balance -= self.current_bet
        self.balance_label.config(text=f"Balance: ${self.balance}")
        self.player_hand.clear()
        self.dealer_hand.clear()
        self.show_hand(self.player_frame, [])
        self.show_hand(self.dealer_frame, [])
        self.shuffle_animation(self.deal_cards_animation)

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

    def hit(self):
        self.player_hand.append(self.deck.pop())
        self.play_sound('flipcard.wav', duration_ms=2000)
        self.show_hand(self.player_frame, self.player_hand)
        self.update_points_labels(reveal_dealer=False)
        if self.calculate_score(self.player_hand) > 21:
            self.status.config(text="You lost!")
            self.play_sound('derrota.wav')
            self.btn_hit.config(state=tk.DISABLED)
            self.btn_stand.config(state=tk.DISABLED)
            self.reveal_dealer()

    def stand(self):
        self.reveal_dealer()
        self.update_points_labels(reveal_dealer=True)

        def dealer_turn():
            dealer_score = self.calculate_score(self.dealer_hand)
            if dealer_score < 17:
                self.dealer_hand.append(self.deck.pop())
                self.play_sound('flipcard.wav', duration_ms=500)
                self.show_hand(self.dealer_frame, self.dealer_hand)
                self.update_points_labels(reveal_dealer=True)
                self.root.after(800, dealer_turn)
            else:
                self.finish_round()

        dealer_turn()

    def finish_round(self):
        player_total = self.calculate_score(self.player_hand)
        dealer_total = self.calculate_score(self.dealer_hand)

        if dealer_total > 21 or player_total > dealer_total:
            self.status.config(text="You won!")
            self.play_sound('bonus-points.wav')
            self.balance += self.current_bet * 2
        elif dealer_total > player_total:
            self.status.config(text="Dealer wins")
            self.play_sound('derrota.wav')
        else:
            self.status.config(text="Tie")
            self.balance += self.current_bet

        self.balance_label.config(text=f"Balance: ${self.balance}")
        self.btn_hit.config(state=tk.DISABLED)
        self.btn_stand.config(state=tk.DISABLED)

    def reveal_dealer(self):
        self.show_hand(self.dealer_frame, self.dealer_hand)
        self.update_points_labels(reveal_dealer=True)

# Inicializa
root = tk.Tk()
app = BlackjackGUI(root)
root.mainloop()
