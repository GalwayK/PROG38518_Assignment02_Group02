import math

import mpi4py
import random

LIST_SUITS = ["Hearts", "Diamonds", "Spades", "Clubs"]
LIST_RANKS = ["Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King", "Ace"]
DICT_SCORES = {"Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10, "Jack": 11, "Queen": 12, "King": 13, "Ace": 14}

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

class Dealer:
    def __init__(self):
        pass

class Player:
    def __init__(self):
        self.hand = []

    def receive_card(self, card):
        self.hand.append(card)

    def sort_hand(self):
        self.hand = sorted(self.hand, key=lambda card: card.score, reverse=True)

    def play_card(self, board_card: Card):
        # If cannot play card send board card back to dealer
        # If can play card send newly played card back to dealer
        pass

    def __str__(self):
        str_hand = ""
        for card in self.hand:
            str_hand = f"{str_hand}{card}\n"
        return str_hand[:-1]

class CardGame:
    def __init__(self, first_card=None):
        self.played_cards = []
        if first_card:
            self.played_cards.append(first_card)

    def get_board_card(self):
        if len(self.played_cards) == 0:
            return None
        return self.played_cards[len(self.played_cards) - 1]

def main():
    deck_of_cards = DeckOfCards()
    deck_of_cards.shuffle_deck()

    num_players = 3
    hand_size = math.floor(51 / num_players)
    if hand_size < 1:
        raise Exception("Why are there so many players?")

    list_players = []
    for i in range(0, num_players):
        list_players.append(Player())

    for n in range(0, hand_size):
        for i, player in enumerate(list_players):
            player: Player
            card: Card = deck_of_cards.draw_card()
            player.receive_card(card)

    for i, player in enumerate(list_players):
        player.sort_hand()
        print(f"Player {i + 1} Cards:\n{player}\n")

    # Setup card game and draw first card
    first_card = deck_of_cards.draw_card()
    card_game = CardGame(first_card)

    # Game loop logic
    # has_won = False
    # while not has_won:
    #     for player in list_players:
    #         board_card = card_game.get_board_card()
    # zz
    #
main()