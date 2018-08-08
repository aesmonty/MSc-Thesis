
import random

class Post:
    def __init__(self, player_id, quality_range, players):
        self.author_id = player_id
        self.quality = random.choice(quality_range)
        self.potential_voters = random.sample(players,self.quality)
        self.votes_received = 0
        self.voters = []

    def __str__(self):
        return str(self.author_id)