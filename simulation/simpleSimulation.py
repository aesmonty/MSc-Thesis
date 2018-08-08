
from scipy import stats
import random

rounds_of_votes = 5
number_of_players = 15


class Player():
    def __init__(self,player_id):
        self.player_id = player_id
        self.quality = player_id
        self.honest = True

    
    def create_post(self,quality,players):
        post = Post(self.player_id,players,self.player_id)
        return post


class Post():
    def __init__(self, quality, players, player_id):
        self.author_id = player_id
        self.quality = quality
        self.potential_voters = random.sample(players,quality)
        self.votes_received = 0
        self.voters = []

    def __str__(self):
        return str(self.author_id)

#Reseed and initialize players and posts
def init_setup(seed):
        
    random.seed(seed) #reseed the prng
    players = init_players()
    posts = init_posts(players)

    return players,posts

    
#Initialize players
def init_players():
    players = []
    for i in range(number_of_players):
        players.append(Player(i))
    bad_guy = random.randint(0,len(players)-1)
    players[bad_guy].honest = False #Choose dishonest player at random
    print ("Bad guy: ", players[bad_guy].player_id)
    return players

#Initialize posts
def init_posts(players):
    posts = []
    for player in players:
        post = player.create_post(player.quality, players)
        posts.append(post)
        
    random.shuffle(posts) #randomize initial order of post ranking
    
    initial_order_posts = display_list(posts)
    print('Initial order of posts:', initial_order_posts)

    return posts


#all players behave honestly
def execute_all_honest(seed):
    
    players,posts = init_setup(seed)
    
    for _round in range(rounds_of_votes):
        random.shuffle(players) #randomize voting order in each round

        for player in players:
            posts = vote (player,posts)

    posts1 = display_list(posts)
    attacker_net_position_1 = net_position(players,posts)
    print_result(posts,posts1,attacker_net_position_1)

    return posts1,attacker_net_position_1

#one player is dishonest. Dishonest player self-vote his post in the first round
def execute_1_self_vote(seed):#WIP
    
    players, posts = init_setup(seed)
    
    for round in range(rounds_of_votes):
        random.shuffle(players) #randomize voting order in each round
        for player in players:
            #self-voting. Find his post and vote for it
            if(not player.honest and round == 0):
                posts = selfvote(player, posts)    
                break #jump to next player
            posts = vote (player,posts)

    posts2 = display_list(posts)
    attacker_net_position_2 = net_position(players,posts)
    print_result(posts,posts2,attacker_net_position_2)

    return posts2,attacker_net_position_2

#one player is dishonest. Dishonest player self-vote his post in every round
def execute_2_self_vote(seed):#WIP
    
    players, posts = init_setup(seed)
    
    for _round in range(rounds_of_votes):
        random.shuffle(players) #randomize voting order in each round

        for player in players:
            if(not player.honest):
                posts = selfvote (player, posts)
                break   #jump to next player        

            posts = vote (player,posts)

    posts3 = display_list(posts)
    attacker_net_position_3 = net_position(players,posts)
    print_result(posts,posts3,attacker_net_position_3)

    return posts3,attacker_net_position_3

def vote (player, posts):

    for p in posts:
        if (player in p.potential_voters and player.player_id not in p.voters):
            p.votes_received += 1
            p.voters.append(player.player_id)
            posts.sort(key=lambda x: x.votes_received, reverse = True) #order post ranking by votes received
            return posts
    return posts

def selfvote(player, posts):

    for p in posts:
        if(p.author_id == player.player_id):
            p.votes_received += 1
            p.voters.append(player.player_id)
            posts.sort(key=lambda x: x.votes_received, reverse = True) #order post ranking by votes received
            return posts
    return posts

def display_list(posts):
    posts_ranking = []
    for p in posts:
        posts_ranking.append(p.author_id)
    return posts_ranking

def get_attacker_id(players):
    for player in players:
        if (not player.honest):
            attacker_id = player.player_id

    return attacker_id


def net_position(players,posts):
    ctr = 0
    attacker_id = get_attacker_id(players)
    for p in posts:
        if p.author_id == attacker_id:
            expected_quality_index = len(posts) - 1 - p.quality
            return ctr - expected_quality_index
        ctr += 1 


def sort_by_quality(posts):
    posts.sort(key=lambda x: x.quality, reverse = True)
    quality_sorted = display_list(posts)
    return quality_sorted


def print_result(posts,order_posts,attacker_position):

    quality_sorted = sort_by_quality(posts)
  
    print ('Final ranking of posts:',order_posts, '     Attacker net position:', attacker_position)
    print ('Spearman:',stats.spearmanr(quality_sorted, order_posts)[0],'   KendallTau:',stats.kendalltau(quality_sorted, order_posts)[0])
    print ("")


    

def main():
  
  seed = random.randint(0,1000)

  execute_all_honest(seed)
  execute_1_self_vote(seed)
  execute_2_self_vote(seed)
  
  
if __name__== "__main__":
  main()