
from steem import Steem
from pprint import pprint
import json
s = Steem()

account_name = "upme"
history = s.get_account_history(account_name, index_from=-1, limit=100)

j1=json.dumps(history)
j2 = json.loads(j1)

print(type(j1))
print(type(j2))

#Write the output of the api request to a json txt
with open(account_name + ".txt", "w") as outfile:

    pprint(j2,stream = outfile)

pprint(j2[0][1]['op'][0])
    

