import tkinter as tk
from PIL import Image, ImageTk
import random
import pygame
import os

pygame.mixer.init()

class BlackjackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack")
        self.deck = []
        self.dealer_hand = []
        self.current_bet = 100
        self.max_players = 3
        self.players = []  # Lista de jogadores: cada um é um dicionário com 'hand' e 'balance'
        self.saved_balances = {}  # Saldos salvos dos jogadores que saíram
        self.current_player = 0  # Índice do jogador da vez
        self.game_in_progress = False

        # Layout de meia-lua: posições (x, y) para cada jogador
        self.player_positions = [
            (400, 500),   # J1: centro em baixo
            (150, 400),   # J2: canto inferior esquerdo
            (650, 400)    # J3: canto inferior direito
        ]

        self.canvas = tk.Canvas(root, width=800, height=750, bg="#0b5123")
        self.canvas.pack()
        self.root.geometry('800x750')

        self.dealer_frame = tk.Frame(root, bg="#0b5123")
        self.canvas.create_window(400, 100, window=self.dealer_frame)
        self.dealer_label = tk.Label(root, text="Dealer", bg="#0b5123", fg="white", font=("Arial", 14, "bold"))
        self.canvas.create_window(400, 50, window=self.dealer_label)

        # Frames e labels para cada jogador
        self.player_frames = []
        self.player_labels = []
        self.balance_labels = []
        self.turn_arrows = []
        self.add_buttons = []
        for i, (x, y) in enumerate(self.player_positions):
            frame = tk.Frame(root, bg="#0b5123")
            self.player_frames.append(frame)
            self.canvas.create_window(x, y, window=frame)
            # Seta de vez acima do nome
            arrow = tk.Label(root, text="", bg="#0b5123", fg="yellow", font=("Arial", 16, "bold"))
            self.turn_arrows.append(arrow)
            self.canvas.create_window(x, y-125, window=arrow)
            label = tk.Label(root, text=f"Jogador {i+1}", bg="#0b5123", fg="white", font=("Arial", 14, "bold"))
            self.player_labels.append(label)
            self.canvas.create_window(x, y-95, window=label)
            balance_label = tk.Label(root, text="", bg="#0b5123", fg="white", font=("Arial", 12))
            self.balance_labels.append(balance_label)
            # Posicionar labels de saldo fora do Canvas usando place()
            if i == 0:
                balance_label.place(x=x-50, y=570)
            else:
                balance_label.place(x=x-50, y=y+60)
            # Botão + para adicionar jogador (apenas para J2 e J3)
            if i > 0:
                btn_add = tk.Button(root, text="+", command=lambda idx=i: self.add_player_at(idx))
                self.add_buttons.append(btn_add)
                # Posicionar botão + fora do Canvas usando place()
                btn_add.place(x=x-25, y=y-10)
            else:
                self.add_buttons.append(None)

        self.status = tk.Label(root, text="Clique em 'Novo Jogo' para começar", bg="#0b5123", fg="white")
        self.canvas.create_window(400, 670, window=self.status)

        self.btn_new_game = tk.Button(root, text="Novo Jogo", command=self.new_game)
        self.btn_new_game.place(x=360, y=620)

        self.btn_hit = tk.Button(root, text="Hit", command=self.hit, state=tk.DISABLED)
        # Não chame .place() aqui, só crie o botão

        self.btn_stand = tk.Button(root, text="Stand", command=self.stand, state=tk.DISABLED)
        # Não chame .place() aqui, só crie o botão

        # Esconder botões Hit e Stand ao iniciar
        self.btn_hit.place_forget()
        self.btn_stand.place_forget()

        self.images = {}
        self.card_back_image = self.load_image("back")

        self.dealer_points = tk.Label(root, text="", bg="#0b5123", fg="white", font=("Arial", 12))
        self.canvas.create_window(700, 100, window=self.dealer_points)

        self.player_points = []
        for i, (x, y) in enumerate(self.player_positions):
            points = tk.Label(root, text="", bg="#0b5123", fg="white", font=("Arial", 12))
            self.player_points.append(points)
            # Inicialmente, posiciona à direita do frame (ajustado depois dinamicamente)
            self.canvas.create_window(x+100, y, window=points, tags=(f"player_points_{i}"))

        # Inicialmente só o jogador 1 está ativo
        self.players = [{'hand': [], 'balance': 1000, 'active': True}]
        self.update_players_ui()
        self.update_turn_arrow()

    def add_player_at(self, idx):
        if len(self.players) < self.max_players and idx >= len(self.players):
            # Verificar se há saldo salvo para este jogador
            if idx in self.saved_balances:
                balance = self.saved_balances[idx]
                del self.saved_balances[idx]
            else:
                balance = 1000
            self.players.append({'hand': [], 'balance': balance, 'active': True})
            self.update_players_ui()
            self.update_turn_arrow()
        elif idx < len(self.players) and not self.players[idx]['active']:
            # Reativar jogador existente
            self.players[idx]['active'] = True
            self.players[idx]['hand'] = []
            self.update_players_ui()
            self.update_turn_arrow()

    def update_players_ui(self):
        for i in range(self.max_players):
            if i < len(self.players):
                self.player_labels[i].config(text=f"Jogador {i+1}")
                self.balance_labels[i].config(text=f"Saldo: ${self.players[i]['balance']}")
                self.player_labels[i].config(state=tk.NORMAL)
                self.balance_labels[i].config(state=tk.NORMAL)
                self.balance_labels[i].config(fg="white")  # Garantir que o saldo sempre está visível
                self.balance_labels[i].place_configure(relx=0, rely=0)  # Garantir que está visível
                self.player_frames[i].tkraise()
                if self.add_buttons[i]:
                    self.add_buttons[i].place_forget()  # Esconde o botão +
                    self.add_buttons[i]['state'] = tk.DISABLED
                self.show_hand(self.player_frames[i], self.players[i]['hand'])
            else:
                self.player_labels[i].config(text="Vazio")
                # Mostrar saldo se há saldo salvo para este lugar
                if i in self.saved_balances:
                    self.balance_labels[i].config(text=f"Saldo: ${self.saved_balances[i]}")
                else:
                    self.balance_labels[i].config(text="Saldo: $0")
                self.player_labels[i].config(state=tk.DISABLED)
                self.balance_labels[i].config(state=tk.DISABLED)
                self.balance_labels[i].config(fg="gray")  # Saldo em cinza quando lugar vazio
                self.balance_labels[i].place_configure(relx=0, rely=0)  # Garantir que está visível
                for widget in self.player_frames[i].winfo_children():
                    widget.destroy()
            # Mostrar botão + para lugares vazios (J2 e J3) quando não há jogo em andamento
            if i > 0 and self.add_buttons[i]:  # Só J2 e J3 têm botão +
                if i >= len(self.players) and not self.game_in_progress:
                    # Lugar vazio e jogo não em andamento - mostrar botão +
                    self.add_buttons[i].place(x=self.player_positions[i][0]-25, y=self.player_positions[i][1]-10)
                    self.add_buttons[i]['state'] = tk.NORMAL
                    self.add_buttons[i].tkraise()  # Garantir que fica no topo
                else:
                    # Lugar ocupado ou jogo em andamento - esconder botão +
                    self.add_buttons[i].place_forget()
                    self.add_buttons[i]['state'] = tk.DISABLED

    def update_turn_arrow(self):
        for i in range(self.max_players):
            if self.game_in_progress and i == self.current_player and i < len(self.players):
                self.turn_arrows[i].config(text="→ Sua vez")
            else:
                self.turn_arrows[i].config(text="")

    def update_points_labels(self, reveal_dealer=False):
        # Atualiza a pontuação de todos os jogadores
        for i in range(self.max_players):
            if i < len(self.players):
                score = self.calculate_score(self.players[i]['hand'])
                self.player_points[i].config(text=f"{score} / 21")
                # Reposiciona o label à direita das cartas
                n_cartas = len(self.players[i]['hand'])
                x, y = self.player_positions[i]
                new_x = x + 50 * n_cartas + 40  # 50px por carta + margem extra
                self.canvas.coords(f"player_points_{i}", new_x, y)
            else:
                self.player_points[i].config(text="")
        # Dealer
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
            lbl.configure(image=img)
            lbl.pack(side=tk.LEFT, padx=5)
        # Garantir que os labels de saldo permanecem visíveis após mostrar as cartas
        for i in range(len(self.players)):
            if i < len(self.players):
                self.balance_labels[i].config(fg="white")
                self.balance_labels[i].config(state=tk.NORMAL)

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
            self.root.after(200, lambda: [lbl.destroy(), self.root.after(100, lambda: flash(i + 1))])

        flash(0)

    def deal_cards_animation(self):
        self.status.config(text="Distribuindo cartas...")
        self.play_sound("playing-cards-being-dealt.wav", duration_ms=2000)
        # Distribui 2 cartas para cada jogador ativo e para o dealer
        for player in self.players:
            player['hand'] = []
        self.dealer_hand = []
        def deal(index):
            total = len(self.players) * 2 + 2  # 2 cartas por jogador + 2 para dealer
            if index < len(self.players) * 2:
                player_idx = index // 2
                self.players[player_idx]['hand'].append(self.deck.pop())
                self.show_hand(self.player_frames[player_idx], self.players[player_idx]['hand'])
                self.update_points_labels(reveal_dealer=False)
            elif index == len(self.players) * 2:
                # Primeira carta do dealer (visível)
                self.dealer_hand.append(self.deck.pop())
                self.show_hand(self.dealer_frame, self.dealer_hand, hide_first=True)
                # Atualiza pontos do dealer só com a primeira carta
                self.update_points_labels(reveal_dealer=False)
            elif index == len(self.players) * 2 + 1:
                # Segunda carta do dealer (virada para baixo)
                self.dealer_hand.append(self.deck.pop())
                self.show_hand(self.dealer_frame, self.dealer_hand, hide_first=True)
                # Atualiza pontos do dealer só com a segunda carta virada para baixo (mostra só a primeira)
                self.update_points_labels(reveal_dealer=False)
            else:
                self.update_points_labels(reveal_dealer=False)
                self.status.config(text=f"Vez do Jogador {self.current_player+1}")
                # Mostrar botões Hit e Stand ao iniciar rodada
                self.btn_hit.place(x=260, y=670)
                self.btn_stand.place(x=460, y=670)
                self.btn_hit.config(state=tk.NORMAL)
                self.btn_stand.config(state=tk.NORMAL)
                self.update_turn_arrow()
                return
            self.root.after(1000, lambda: deal(index + 1))
        deal(0)

    def new_game(self):
        # Só inicia se não houver jogo em andamento
        if self.game_in_progress:
            self.status.config(text="Aguarde o fim da rodada!")
            return
        # Verifica se todos os jogadores têm saldo suficiente
        for i, player in enumerate(self.players):
            if player['balance'] < self.current_bet:
                self.status.config(text=f"Jogador {i+1} sem saldo suficiente!")
                return
        # Esconder botão Novo Jogo e mostrar Hit/Stand imediatamente
        self.btn_new_game.place_forget()
        self.btn_hit.place(x=260, y=670)
        self.btn_stand.place(x=460, y=670)
        self.deck = self.create_deck()
        for i, player in enumerate(self.players):
            player['balance'] -= self.current_bet
            self.balance_labels[i].config(text=f"Saldo: ${player['balance']}")
            player['hand'] = []
        self.dealer_hand = []
        for i in range(len(self.players)):
            self.show_hand(self.player_frames[i], [])
        self.show_hand(self.dealer_frame, [])
        # Resetar os labels de pontos dos jogadores e dealer
        self.update_points_labels(reveal_dealer=False)
        self.current_player = 0
        self.update_turn_arrow()
        self.game_in_progress = True
        self.update_players_ui()  # Desativa os botões + imediatamente
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
        self.players[self.current_player]['hand'].append(self.deck.pop())
        self.play_sound('flipcard.wav', duration_ms=2000)
        self.show_hand(self.player_frames[self.current_player], self.players[self.current_player]['hand'])
        self.update_points_labels(reveal_dealer=False)
        if self.calculate_score(self.players[self.current_player]['hand']) > 21:
            self.status.config(text=f"Jogador {self.current_player+1} perdeu!")
            self.play_sound('derrota.wav')
            self.btn_hit.config(state=tk.DISABLED)
            self.btn_stand.config(state=tk.DISABLED)
            self.root.after(1000, self.next_player)

    def stand(self):
        self.btn_hit.config(state=tk.DISABLED)
        self.btn_stand.config(state=tk.DISABLED)
        self.root.after(500, self.next_player)

    def next_player(self):
        self.current_player += 1
        if self.current_player < len(self.players):
            self.status.config(text=f"Vez do Jogador {self.current_player+1}")
            self.update_turn_arrow()
            self.update_points_labels(reveal_dealer=False)
            self.btn_hit.config(state=tk.NORMAL)
            self.btn_stand.config(state=tk.NORMAL)
        else:
            self.status.config(text="Vez do Dealer")
            self.update_turn_arrow()
            self.btn_hit.config(state=tk.DISABLED)
            self.btn_stand.config(state=tk.DISABLED)
            self.root.after(1000, self.dealer_turn)

    def dealer_turn(self):
        # Revela as duas cartas iniciais do dealer e mostra o valor (ambas viradas para cima)
        self.show_hand(self.dealer_frame, self.dealer_hand, hide_first=False)
        self.update_points_labels(reveal_dealer=True)
        # Espera 1000 ms antes de começar a comprar cartas adicionais
        def dealer_play():
            dealer_score = self.calculate_score(self.dealer_hand)
            if dealer_score < 17:
                self.dealer_hand.append(self.deck.pop())
                self.play_sound('flipcard.wav', duration_ms=500)
                self.show_hand(self.dealer_frame, self.dealer_hand, hide_first=False)
                self.update_points_labels(reveal_dealer=True)
                self.root.after(1000, dealer_play)
            else:
                self.finish_round()
        self.root.after(1000, dealer_play)

    def finish_round(self):
        dealer_total = self.calculate_score(self.dealer_hand)
        for i, player in enumerate(self.players):
            player_total = self.calculate_score(player['hand'])
            if player_total > 21:
                result = "Perdeu!"
            elif dealer_total > 21 or player_total > dealer_total:
                result = "Ganhou!"
                player['balance'] += self.current_bet * 2
            elif dealer_total > player_total:
                result = "Dealer venceu"
            else:
                result = "Empate"
                player['balance'] += self.current_bet
            self.balance_labels[i].config(text=f"Saldo: ${player['balance']}")
            self.status.config(text=f"Jogador {i+1}: {result}")
        # Atualiza os valores finais das cartas de todos os jogadores e do dealer
        self.update_points_labels(reveal_dealer=True)
        self.game_in_progress = False
        self.btn_hit.config(state=tk.DISABLED)
        self.btn_stand.config(state=tk.DISABLED)
        # Esconder botões Hit e Stand ao final da rodada
        self.btn_hit.place_forget()
        self.btn_stand.place_forget()
        # Mostrar botão Novo Jogo ao final da rodada
        self.btn_new_game.place(x=360, y=620)
        # Remove jogadores 2 e 3 da mesa no final da rodada, mas salva seus saldos
        while len(self.players) > 1:
            player_idx = len(self.players) - 1
            self.saved_balances[player_idx] = self.players[player_idx]['balance']
            self.players.pop()
        self.update_players_ui()  # Reabilita o botão + após rodada


    def reveal_dealer(self):
        self.show_hand(self.dealer_frame, self.dealer_hand)
        self.update_points_labels(reveal_dealer=True)

# Inicializa
root = tk.Tk()
app = BlackjackGUI(root)
root.mainloop()
