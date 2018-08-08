
from scipy import stats
import random

from Strategy import Strategy
from Player import Player
from Post import Post

profile = ["honest","cheatOnce","cheatAlways"]

#noProfiles should be a list of integers [3,4,5] denoting the number of players per strategy profile
def simulation(seed,noRounds,nStrategies): #poner nStrategies en tuple

    assert type(nStrategies) == list

    players,posts = init_setup(seed,nStrategies)

    for _round in range(noRounds):
        random.shuffle(players) #randomize voting order in each round

        for player in players:
            post = player.vote(posts)
            #print(post)
            if post != False: #Check if the player actually vote for something
                posts = execute_vote(player,post,posts)

    print_result(posts) #ojo que los ordena por calidad...MIRAR ESTO


    return posts,players


#Reseed and initialize players and posts
def init_setup(seed, noProfiles):
        
    random.seed(seed) #reseed the prng
    players = init_players(noProfiles)
    posts = init_posts(players)

    return players,posts
    
#Initialize players
def init_players(noProfiles):
    number_of_players = get_number_players(noProfiles)
    players = []
    index = 0
    profile_index = 0


    for noProfile in noProfiles:
        #Create noProfile players of profile_index and profile = ["honest", "cheatOnce","cheatAlways"]
        for _i in range(0, noProfile):
            #Add a player (id,quality_range,strategy_profile,sp)
            players.append(Player(index,get_random_quality_range(number_of_players),profile[profile_index],1))
            index += 1

        profile_index += 1

    '''
    Here we can add another layer of customization. Ex:

    for player in players:
        if player.Strategy.type == cheatOnce:
            player.set_sp = 2
    '''

    return players

#Initialize posts
def init_posts(players):
    posts = []
    players_ids = list(range(len(players)))
    for player in players:
        post = player.create_post(player.quality_range, players_ids)
        posts.append(post)
        
    #IGUAL HAY QUE HACER UN RESEED AQUÍ, Y NO ARRIBA??????
    

    random.shuffle(posts) #randomize initial order of post ranking
    
    initial_order_posts = display_list(posts)
    print('Initial order of posts:', initial_order_posts)

    return posts

def execute_vote(player,post,posts):

    #Incluir un loop con voting power decreciendo(más de un voto por ronda)
    post.votes_received += player.sp
    post.voters.append(player.id)
    posts.sort(key=lambda x: x.votes_received, reverse = True) #order post ranking by votes received
    return posts


# Get the number of players in the simulation (as a sum of the number of players of each profile)
def get_number_players(noProfiles):

    ctr = 0
    for profile in noProfiles:
        ctr += profile

    return ctr

# Retrieve a random quality range as a subset of {0,noPlayers}
def get_random_quality_range(nPlayers):

    quality_range = []

    edge1 = random.randint(0,nPlayers)
    edge2 = random.randint(0,nPlayers)

    if edge1 < edge2:
        for i in range(edge1,edge2 + 1):
            quality_range.append(i)
        return quality_range

    elif edge1 > edge2:
        for i in range(edge2,edge1 + 1):
            quality_range.append(i)
        return quality_range

    else:
        quality_range.append(edge1)
        return quality_range

#set a user-defined quality range
def set_quality_range(minQuality,maxQuality,noPlayers):

    assert minQuality >= 0
    assert maxQuality <= noPlayers
    assert minQuality <= maxQuality

    quality_range = []

    if minQuality == maxQuality:
        quality_range.append(minQuality)
        return quality_range

    else:
        for i in range(minQuality,maxQuality + 1):
            quality_range.append(i)
        return quality_range


# Return a list with the author_id of the posts
def display_list(posts):
    posts_ranking = []
    for p in posts:
        posts_ranking.append(p.author_id)
    return posts_ranking

# Getter for the id of the attacker --------WIP
def get_attacker_id(players):
    for player in players:
        if (not player.honest):
            attacker_id = player.id

    return attacker_id

# Calculate the net position difference of the attacker against its expected position ---------WIP
def net_position(players,posts):
    ctr = 0
    attacker_id = get_attacker_id(players)
    for p in posts:
        if p.author_id == attacker_id:
            expected_quality_index = len(posts) - 1 - p.quality
            return ctr - expected_quality_index
        ctr += 1 

# Sort lists of posts by quality
def sort_by_quality(posts):
    posts.sort(key=lambda x: x.quality, reverse = True)# no cambiar orden de los posts
    quality_sorted = display_list(posts)
    return quality_sorted


# Print results of execution
def print_result(posts):

    order_posts = display_list(posts)
    quality_sorted = sort_by_quality(posts)
  
    print ('Final ranking of posts:',order_posts)
    print ('Quality sorted:',quality_sorted)
    print ('Spearman:',stats.spearmanr(quality_sorted, order_posts)[0],'   KendallTau:',stats.kendalltau(quality_sorted, order_posts)[0])
    print ("")


def main():
  
  seed = random.randint(0,1000)

  simulation(seed,5,[15,0,0])
  simulation(seed,5,[10,1,4])
  
  
if __name__== "__main__":
  main()