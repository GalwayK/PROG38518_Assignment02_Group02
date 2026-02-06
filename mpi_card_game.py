import math
import time
import random
import mpi4py.MPI as MPI

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

    def get_num_cards_played(self):
        return self.current_index

    def get_num_cards_unplayed(self):
        return 52 - self.current_index

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

class Player:
    def __init__(self, name="Leeroy Jenkins", comm=None):
        self.comm: MPI.COMM_WORLD = comm
        self.name = name
        self.hand = []
        self.score = 0

    def play_game(self):
        is_playing = self.comm.recv(source=0)
        while is_playing:
            self.empty_hand()
            self.receive_hand() # IT WORKS
            self.play_round() # IT WORKS
            is_playing = self.comm.recv(source=0)
        self.comm.send(self, dest=0)

    def receive_hand(self):
        while True:
            card: Card = self.comm.recv(source=0)
            if card is not None:
                self.receive_card(card)
            else:
                break
        self.comm.send(self, dest=0)

    def receive_card(self, card):
        self.hand.append(card)
        self.sort_hand()

    def empty_hand(self):
        self.hand.clear()

    def sort_hand(self):
        if len(self.hand) <= 0:
            self.hand = sorted(self.hand, key=lambda card: card.score, reverse=True)

    def is_hand_empty(self):
        return len(self.hand) == 0

    def play_round(self):
        while True:
            board_card = self.comm.recv(source=0)
            if board_card is None:
                break
            board_card, str_action, earned_points, num_remaining, game_ended = self.play_card(board_card)
            self.comm.send((board_card, str_action, earned_points, num_remaining, game_ended), dest=0)

        self.comm.send(self, dest=0)

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
                break

        return played_card, str_action, earned_points, num_remaining_cards, self.is_hand_empty()

    def __str__(self):
        str_hand = f"{self.name}'s Hand: \n"
        for card in self.hand:
            str_hand = f"{str_hand}{card}\n"
        return str_hand

class Dealer:
    def __init__(self, deck_of_cards, num_players, comm: MPI.COMM_WORLD=None):
        self.comm = comm

        self.list_players = []
        self.num_players = num_players
        self.deck_of_cards: DeckOfCards = deck_of_cards
        self.min_size = 4
        for i in range(0, num_players):
            self.list_players.append(Player(name=LIST_NAMES[i]))

    def can_play_round(self):
        return math.floor((self.deck_of_cards.get_num_cards_unplayed() - 1) / self.num_players) > self.min_size

    def play_game(self):
        num_rounds = 0
        while self.can_play_round():
            for process in range(1, self.num_players + 1):
                self.comm.send(True, process)

            num_rounds = num_rounds + 1
            print(f"Beginning round #{num_rounds}")
            self.deal_cards() # IT WORKS
            self.play_round() # IT ALSO WORKS

        for process in range(1, self.num_players + 1):
            self.comm.send(False, dest=process)

        print(f"There are not enough cards to play another round, the game is over after {num_rounds} rounds! Tallying final results...")
        self.print_player_scores()

    def deal_cards(self):
        max_size = min(math.floor((self.deck_of_cards.get_num_cards_unplayed() - 1) / self.num_players), 8)

        if max_size < self.min_size:
            raise ValueError("Why are there so many players?")

        hand_size = random.randrange(self.min_size, max_size + 1)

        for n in range(0, hand_size):
            for process in range(1, self.num_players + 1):
                card: Card = self.deck_of_cards.draw_card()
                self.comm.send(card, dest=process)

        for process in range(1, self.num_players + 1):
            self.comm.send(None, dest=process)
        self.print_player_hands()

    def play_round(self):
        # Setup card game and draw first card
        first_card = self.deck_of_cards.draw_card()
        card_game = CardGame(first_card)
        board_card = card_game.get_board_card()

        print(f"Undealt Cards: {self.deck_of_cards.get_num_cards_unplayed()}\n")
        print("Beginning to play the round!")
        # Game loop logic
        player_has_won = False
        num_passes = 0
        while not player_has_won:
            for process in range(1, self.num_players + 1):
                player_name = LIST_NAMES[process]
                print(f"{player_name}'s turn! Current card on the board: {board_card}")
                self.comm.send(board_card, dest=process)
                board_card, str_action, earned_points, num_remaining, player_has_won = self.comm.recv(source=process)

                str_move = f"{player_name} {str_action} {board_card} for {earned_points} points, and has {num_remaining} cards in their hand.\n"
                print(str_move)

                # This if block is ugly and messy I can't even
                if str_action == "passed on":
                    num_passes = num_passes + 1
                    if num_passes >= self.num_players:
                        drawn_card = self.deck_of_cards.draw_card()
                        if drawn_card is not None:
                            board_card = drawn_card
                            print(f"No one can play: {board_card} drawn from the deck and placed on the board!")
                            num_passes = 0
                        else:
                            print(f"No one can play and deck is empty: round is over!")
                            player_has_won = True
                            break
                else:
                    num_passes = 0

                if player_has_won:
                    winning_player = player_name
                    print(f"{winning_player} has played their last card, this round is over! Tallying results for the round...")
                    break

        for process in range(1, self.num_players + 1):
            self.comm.send(None, dest=process)
        self.print_player_scores()

    def sort_players(self):
        self.list_players = sorted(self.list_players, key=lambda player: player.score, reverse=True)

    def print_player_hands(self):
        for process in range(1, self.num_players + 1):
            player = self.comm.recv(source=process)
            print(player)

    def print_player_scores(self):
        list_players = []
        for process in range(1, self.num_players + 1):
            list_players.append(self.comm.recv(source=process))

        list_players = sorted(list_players, key=lambda player: player.score, reverse=True)

        str_scores = ""
        for i, player in enumerate(list_players):
            str_scores = f"{str_scores}Player #{i + 1}: {player.name} with {player.score} points!\n"
        print(str_scores)

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        num_players = size - 1
        deck_of_cards = DeckOfCards()
        deck_of_cards.shuffle_deck()

        dealer = Dealer(deck_of_cards=deck_of_cards, num_players=num_players, comm=comm)
        dealer.play_game()
    else:
        player = Player(name=LIST_NAMES[rank], comm=comm)
        player.play_game()
    comm.Barrier()
main()