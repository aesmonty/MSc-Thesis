
from Post import Post

class Strategy:
    def __init__(self, type, id):
        self.type = type
        self.id = id

    def vote(self,posts):
        if self.type == "honest":  
            for post in posts:
                if (self.id in post.potential_voters and self.id not in post.voters):
                    return post
            return False

        elif self.type == "cheatOnce":
            for post in posts:
                if(post.author_id == self.id and self.id not in post.voters):
                    return post
                
            for post in posts:
                if (self.id in post.potential_voters and self.id not in post.voters):
                    return post
            return False

        elif self.type == "cheatAlways":
            for post in posts:
                if(post.author_id == self.id and self.id not in post.voters):
                    return post
            return False

    def __str__(self):
        return str(self.type)