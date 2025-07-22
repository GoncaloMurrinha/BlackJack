import tkinter as tk
from tkinter import simpledialog, ttk
from PIL import Image, ImageTk
import random
import pygame
import math
import os

pygame.mixer.init()

class BlackjackMesaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack - Mesa Meia-Lua")
        self.root.geometry("1200x900")
        self.root.configure(bg="#064820")

        # Configurações do jogo
        self.max_players = 4
        self.start_balance = 1000
        self.bet_amount = 100

        # Estado do jogo
        self.deck = []
        self.players = []           # lista de dicts: {'hand': [], 'balance': int}
        self.dealer_hand = []
        self.current_player = 0
        self.game_in_progress = False

        # Carrega imagens e sons
        self.images = {}
        self.card_back = self.load_card_back()
        self.load_sounds()

        # Canvas da mesa
        self.canvas = tk.Canvas(self.root, width=1100, height=600, bg="#064820", highlightthickness=0)
        self.canvas.pack(pady=30)
        self.draw_table()

        # Controles e status
        self.status = tk.Label(self.root, text="Escolhe o nº de jogadores e clica em Iniciar", bg="#064820", fg="#f6e27f", font=("Segoe UI", 16, "bold"))
        self.status.pack(pady=10)

        self.controls_frame = tk.Frame(self.root, bg="#064820")
        self.controls_frame.pack(pady=10)

        self.btn_start = ttk.Button(self.controls_frame, text="Iniciar Jogo", command=self.ask_num_players)
        self.btn_start.grid(row=0, column=0, padx=20)

        self.btn_hit = ttk.Button(self.controls_frame, text="Hit", command=self.hit, state=tk.DISABLED)
        self.btn_hit.grid(row=0, column=1, padx=20)

        self.btn_stand = ttk.Button(self.controls_frame, text="Stand", command=self.stand, state=tk.DISABLED)
        self.btn_stand.grid(row=0, column=2, padx=20)

        # Saldos
        self.balance_labels = []
        for i in range(self.max_players):
            lbl = tk.Label(self.root, text="", bg="#064820", fg="white", font=("Segoe UI", 12))
            lbl.pack()
            self.balance_labels.append(lbl)

        self.update_ui()

    def draw_table(self):
        # Desenha a meia-lua da mesa
        w, h = 1100, 600
        self.canvas.create_arc(50, 50, w-50, h*2, start=0, extent=180, fill="#0a2d11", outline="#f6e27f", width=6)
        # Dealer
        self.canvas.create_text(w//2, 450, text="DEALER", fill="#f6e27f", font=("Segoe UI", 18, "bold"))
        # Posições dos jogadores
        self.player_positions = self.get_player_positions()
        for i, (x, y) in enumerate(self.player_positions):
            self.canvas.create_oval(x-40, y-40, x+40, y+40, fill="#0a2d11", outline="#f6e27f", width=3)
            self.canvas.create_text(x, y+55, text=f"Jogador {i+1}", fill="#f6e27f", font=("Segoe UI", 14, "bold"))

    def get_player_positions(self):
        # Calcula posições em arco para os jogadores
        w, h = 1100, 600
        radius = 400
        center_x, center_y = w//2, h-80
        angles = [200, 250, 290, 340][:self.max_players]
        positions = []
        for a in angles:
            rad = math.radians(a)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            positions.append((x, y))
        return positions

    def load_sounds(self):
        self.sounds = {}
        for fname, key in [("shuffling-cards.wav", "shuffle.wav"), ("playing-cards-being-dealt.wav", "deal.wav"), ("flipcard.wav", "card.wav")]:
            path = os.path.join("sons", fname)
            if os.path.exists(path):
                self.sounds[key] = pygame.mixer.Sound(path)

    def play_sound(self, key):
        if key in self.sounds:
            self.sounds[key].play()

    def load_card_back(self):
        path = os.path.join("cartas", "back.png")
        img = Image.open(path).resize((72,96))
        return ImageTk.PhotoImage(img)

    def card_image(self, card):
        mapping = {'J':'jack','Q':'queen','K':'king','A':'ace'}
        v = card[:-1]
        s = card[-1]
        val = mapping.get(v, v)
        suit = {"H":"hearts","D":"diamonds","S":"spades","C":"clubs"}[s]
        fn = f"{val}_of_{suit}.png"
        path = os.path.join("cartas", fn)
        if path not in self.images:
            img = Image.open(path).resize((72,96))
            self.images[path] = ImageTk.PhotoImage(img)
        return self.images[path]

    def ask_num_players(self):
        n = simpledialog.askinteger("Jogadores", f"Nº de jogadores (1–{self.max_players}):", minvalue=1, maxvalue=self.max_players)
        if n:
            self.setup_game(n)

    def setup_game(self, n_players):
        self.players = [{'hand':[], 'balance':self.start_balance} for _ in range(n_players)]
        self.dealer_hand = []
        self.game_in_progress = True
        self.current_player = 0
        self.update_ui()
        self.start_round()

    def start_round(self):
        for i, p in enumerate(self.players):
            if p['balance'] < self.bet_amount:
                self.status.config(text=f"Jogador {i+1} sem saldo! Fim de jogo.")
                self.game_in_progress = False
                self.hide_controls()
                return
        for p in self.players:
            p['balance'] -= self.bet_amount
        self.deck = self.create_deck()
        for p in self.players: p['hand'] = []
        self.dealer_hand = []
        self.play_sound("shuffle.wav")
        self.deal_cards()

    def create_deck(self):
        vals = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        suits = ['H','D','S','C']
        deck = [v+s for v in vals for s in suits]
        random.shuffle(deck)
        return deck

    def deal_cards(self):
        self.play_sound("deal.wav")
        for _ in range(2):
            for p in self.players:
                p['hand'].append(self.deck.pop())
            self.dealer_hand.append(self.deck.pop())
        self.update_ui()
        self.status.config(text=f"Vez do Jogador 1")
        self.show_controls()

    def hit(self):
        p = self.players[self.current_player]
        p['hand'].append(self.deck.pop())
        self.play_sound("card.wav")
        self.update_ui()
        if self.score(p['hand']) > 21:
            self.status.config(text=f"Jogador {self.current_player+1} BUST!")
            self.root.after(1000, self.next_player)

    def stand(self):
        self.root.after(100, self.next_player)

    def next_player(self):
        self.current_player += 1
        if self.current_player < len(self.players):
            self.status.config(text=f"Vez do Jogador {self.current_player+1}")
            self.update_ui()
        else:
            self.hide_controls()
            self.status.config(text="Vez do Dealer")
            self.root.after(500, self.dealer_play)

    def dealer_play(self):
        self.update_ui(reveal_dealer=True)
        while self.score(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())
            self.play_sound("card.wav")
            self.update_ui(reveal_dealer=True)
            self.root.update()
            pygame.time.delay(700)
        self.root.after(500, self.finish_round)

    def finish_round(self):
        dealer_score = self.score(self.dealer_hand)
        for i, p in enumerate(self.players):
            s = self.score(p['hand'])
            if s > 21:
                result = "perdeu"
            elif dealer_score > 21 or s > dealer_score:
                result = "ganhou"
                p['balance'] += self.bet_amount * 2
            elif s == dealer_score:
                result = "empate"
                p['balance'] += self.bet_amount
            else:
                result = "perdeu"
            self.status.config(text=f"Jogador {i+1} {result}.")
            self.root.update()
            pygame.time.delay(1000)
        self.update_ui()
        self.game_in_progress = False
        self.btn_start.config(state=tk.NORMAL)
        self.status.config(text="Jogo terminado. Clica Iniciar para jogar outra ronda.")

    def update_ui(self, reveal_dealer=True):
        self.canvas.delete("card")
        # Dealer cartas (no topo, centro)
        dealer_x, dealer_y = 1100//2, 540
        for i, c in enumerate(self.dealer_hand):
            img = self.card_image(c) if reveal_dealer or i == 0 else self.card_back
            self.canvas.create_image(dealer_x + i*40 - 40, dealer_y, image=img, anchor=tk.CENTER, tags="card")
        # Dealer pontos
        if self.dealer_hand:
            pts = self.score(self.dealer_hand) if reveal_dealer else "??"
            self.canvas.create_text(dealer_x, dealer_y-60, text=f"Pontos: {pts}", fill="white", font=("Segoe UI", 14, "bold"), tags="card")
        # Jogadores
        for i, (x, y) in enumerate(self.player_positions):
            if i < len(self.players):
                p = self.players[i]
                for j, c in enumerate(p['hand']):
                    img = self.card_image(c)
                    self.canvas.create_image(x + j*30 - 30, y, image=img, anchor=tk.CENTER, tags="card")
                pts = self.score(p['hand'])
                self.canvas.create_text(x, y-55, text=f"Pontos: {pts}", fill="white", font=("Segoe UI", 13, "bold"), tags="card")
                self.balance_labels[i].config(text=f"Saldo: ${p['balance']}")
            else:
                self.balance_labels[i].config(text="")

    def score(self, hand):
        total = 0
        aces = 0
        for card in hand:
            val = card[:-1]
            if val in ['J','Q','K']:
                total += 10
            elif val == 'A':
                aces += 1
                total += 11
            else:
                total += int(val)
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def show_controls(self):
        self.btn_hit.config(state=tk.NORMAL)
        self.btn_stand.config(state=tk.NORMAL)
        self.btn_start.config(state=tk.DISABLED)

    def hide_controls(self):
        self.btn_hit.config(state=tk.DISABLED)
        self.btn_stand.config(state=tk.DISABLED)
        self.btn_start.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    game = BlackjackMesaGUI(root)
    root.mainloop()
