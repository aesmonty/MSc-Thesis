
import requests,json,datetime
from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


plt.style.use('ggplot')

# Make a get request to get the latest position of the international space station from the opennotify api.
response = requests.get("https://steemdb.com/api/props")

# Print the status code of the response.
text = response.text

# print(text)

#Write the output of the api request to a json txt
# with open("globVariables.json", "w") as outfile:

#     outfile.write(text)

#parse json txt into objects
with open('globVariables.json', encoding='utf-8') as data_file:
    data = json.loads(data_file.read())

#print(data[0])

#data formatting
date1 = data[0]["time"]["$date"]["$numberLong"]
fmt1 = "%d-%m-%Y %H:%M:%S"
fmt2 = "%d/%m/%Y"
dates = []
supply= []

for i in range(0,len(data)):
    x = data[i]["time"]["$date"]["$numberLong"]
    y = data[i]['total_pow']

    #y = data[i]["sbd_print_rate"]
    t_utc = datetime.datetime.utcfromtimestamp(float(x)/1000.)
    #print(t_utc.strftime(fmt1)) # prints 2012-08-28 00:45:17
    dates.append(t_utc.strftime(fmt2)) #populates the list with date formate 23-05-1997
    supply.append(y)
    


with open("data.txt", "w") as outfile:

    pprint(data[0],stream=outfile)
    

    #print(len(data))

    #Print the the current supply data for each block
    # for i in range(0,len(data)):
    #     pprint( data[i]["current_supply"],stream=outfile)


### Plotting global variables against dates

#dates = ['01/02/1991','01/03/1991','01/04/1991']
x = [datetime.datetime.strptime(d,'%d/%m/%Y').date() for d in dates]
y = supply

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator())
plt.plot(x,y)
plt.gcf().autofmt_xdate()

plt.title('Total POW blocks')
plt.savefig('pow_blocks.jpg')

plt.show()

