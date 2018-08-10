
import requests,json,datetime
from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


plt.style.use('ggplot')




total_vesting_shares = [390505808595.623203, 390547870093.222377, 390824866121.001966, 390929928076.640579, 391093635053.819807]
reward_balance = [743994.027, 744900.977, 748183.169, 749744.481, 750047.346]
recent_claims = [4.72970584378626960e11, 4.73165455410984110e11, 4.71794733758840999e11, 4.71605813043569361e11, 4.72162286547538941e11]
total_vesting_fund_steem = [192270346.255, 192300884.844, 192446781.229, 192509538.006, 192600056.042]

dates = ["21-06-2018", "22-06-2018", "23-06-2018", "24-06-2018", "25-06-2018"]

#d = (total_vesting_shares*reward_balance)/(total_vesting_fund_steem*recent_claims)

#print(type(g))
d = []
interest = []

for i in range(0, len(total_vesting_fund_steem)):
    d.append((total_vesting_shares[i]*reward_balance[i])/(total_vesting_fund_steem[i]*recent_claims[i]))
    interest.append((1+ 1.4*d[i])**52)
    #print(interest[i])

averageInterest = sum(interest) / float(len(interest))
average_d = sum(d) / float(len(d))

print(d)
print(average_d)
print (averageInterest)


