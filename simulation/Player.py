
from Post import Post
from Strategy import Strategy

class Player:
    def __init__(self, id, quality_range, type, sp):
        self.id = id
        self.quality_range = quality_range
        self.strategy = Strategy(type,id)
        self.sp = sp

    def set_strategy(self, strategy):
        self.strategy = strategy

    def set_sp(self, sp):
        self.sp = sp

    def set_quality_range(self,quality_range):
        self.quality_range = quality_range

    def create_post(self,quality,players):
        post = Post(self.id,self.quality_range,players)
        return post

    def vote(self,posts):
        return self.strategy.vote(posts)
