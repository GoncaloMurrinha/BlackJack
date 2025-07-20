import time
from game.blackjack import Blackjack
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class BlackjackApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Blackjack Mobile'))
        layout.add_widget(Button(text='Novo Jogo'))
        return layout

def main():
    print("Welcome to Blackjack!")
    game = Blackjack()
    
    while True:
        game.play_round()
        play_again = input("Do you want to play again? (y/n): ")
        if play_again.lower() != 'y':
            print("Thanks for playing!")
            break
        time.sleep(1)

if __name__ == "__main__":
    BlackjackApp().run()
    main()