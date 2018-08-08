#Run this script daily around 18.00 to get the relevant global variables of Steem
from steem import Steem
import json
s = Steem()

reward_fund = s.get_reward_fund()
reward_json = json.dumps(reward_fund)

global_props = s.get_dynamic_global_properties()
global_json = json.dumps(global_props)

with open("selfvote.json", "a") as outfile:

     outfile.write(reward_json)
     outfile.write('\n')
     outfile.write(global_json)
     outfile.write('\n')
     outfile.write('\n')
