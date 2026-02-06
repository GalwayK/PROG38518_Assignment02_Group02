import math
import time

import mpi4py
import random

LIST_SUITS = ["Hearts", "Diamonds", "Spades", "Clubs"]
LIST_RANKS = ["Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King", "Ace"]
DICT_SCORES = {"Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10, "Jack": 11, "Queen": 12, "King": 13, "Ace": 14}
LIST_NAMES = ["Astohl", "Barst", "Catria", "Draug", "Est", "Fergus", "Gotoh", "Hector", "Ike", "Jeorge", "Kris", "Leo", "Marth", "Nasir", "Oscar", "Palla", "Quan", "Rickard", "Soren", "Tomas", "Ulki", "Volke", "Wendy", "Xavier", "Yarne", "Zelgius"]

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.score = DICT_SCORES[self.rank]

    def compare(self, card):
        return card.suit == self.suit or card.rank == self.rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"

class DeckOfCards:
    def __init__(self):
        self.deck = DeckOfCards.create_new_deck()
        self.current_index = 0

    def draw_card(self):
        if self.current_index >= len(self.deck):
            return None

        card = self.deck[self.current_index]
        self.current_index += 1
        return card

    def shuffle_deck(self):
        random.shuffle(self.deck)
        self.current_index = 0

    @staticmethod
    def create_new_deck():
        deck = []
        for suit in LIST_SUITS:
            for rank in LIST_RANKS:
                deck.append(Card(rank=rank, suit=suit))
        return deck

    def __str__(self):
        str_deck = ""
        for i, card in enumerate(self.deck):
            str_card = f"{i + 1:2d}. {card}\n"
            str_deck = f"{str_deck}{str_card}"
        return str_deck[:-1]

class CardGame:
    def __init__(self, first_card=None):
        self.played_cards = []
        if first_card:
            self.played_cards.append(first_card)

    def get_num_played_cards(self):
        return len(self.played_cards)

    def get_board_card(self):
        if len(self.played_cards) == 0:
            return None
        return self.played_cards[len(self.played_cards) - 1]

class Dealer:
    def __init__(self, deck_of_cards, num_players):
        self.list_players = []
        self.num_players = num_players
        self.deck_of_cards = deck_of_cards
        for i in range(0, num_players):
            self.list_players.append(Player(name=LIST_NAMES[i]))

    def deal_cards(self):
        max_size = min(math.floor(51 / self.num_players), 8)
        min_size = 4

        if max_size <= min_size:
            raise ValueError("Why are there so many players?")

        hand_size = random.randrange(min_size, max_size)

        for n in range(0, hand_size):
            for player in self.list_players:
                player: Player
                card: Card = self.deck_of_cards.draw_card()
                player.receive_card(card)

    def play_game(self):
        # Setup card game and draw first card
        first_card = self.deck_of_cards.draw_card()
        card_game = CardGame(first_card)
        board_card = card_game.get_board_card()

        print("Beginning to play!")
        # Game loop logic
        game_ended = False
        winning_player = None
        num_passes = 0
        while not game_ended:
            for player in self.list_players:

                print(f"{player.name}'s turn! Current card on the board: {board_card}")
                board_card, str_action, earned_points, num_remaining = player.play_card(board_card)
                str_move = f"{player.name} {str_action} {board_card} for {earned_points} points, and has {num_remaining} cards in their hand.\n"
                print(str_move)

                if str_action == "passed on":
                    drawn_card = self.deck_of_cards.draw_card()
                    if drawn_card is not None:
                        player.receive_card(drawn_card)
                        player.sort_hand()
                        num_passes = 0
                    elif num_passes == self.num_players:
                        print("No one can play, ending game early!")
                        game_ended = True
                        break
                    else:
                        print(f"Deck is empty, cannot draw new card!")
                        num_passes = num_passes + 1

                if num_remaining == 0:
                    winning_player = player
                    print(f"{winning_player.name} has played their last card, the game is over! Tallying results...")
                    game_ended = True
                    break
                time.sleep(0.2)

        self.sort_players()

        for i, player in enumerate(self.list_players):
            print(f"Player #{i + 1}: {player.name} with {player.score} points!")

    def sort_players(self):
        self.list_players = sorted(self.list_players, key=lambda player: player.score, reverse=True)

class Player:
    def __init__(self, name="Leeroy Jenkins"):
        self.name = name
        self.hand = []
        self.score = 0

    def receive_card(self, card):
        self.hand.append(card)
        self.sort_hand()

    def sort_hand(self):
        self.hand = sorted(self.hand, key=lambda card: card.score, reverse=True)

    def play_card(self, board_card: Card):
        played_card = board_card
        str_action = "passed on"
        earned_points = 0
        num_remaining_cards = len(self.hand)

        for i, card in enumerate(self.hand):
            if card.compare(board_card):
                self.hand.pop(i)
                played_card = card
                str_action = "played"
                earned_points = card.score
                num_remaining_cards = len(self.hand)
                self.score = self.score + card.score

        return played_card, str_action, earned_points, num_remaining_cards

    def __str__(self):
        str_hand = f"{self.name}'s Hand: \n"
        for card in self.hand:
            str_hand = f"{str_hand}{card}\n"
        return str_hand[:-1]

def main():
    num_players = 3
    deck_of_cards = DeckOfCards()
    deck_of_cards.shuffle_deck()
    dealer = Dealer(deck_of_cards=deck_of_cards, num_players=num_players)
    dealer.deal_cards()
    dealer.play_game()

main()