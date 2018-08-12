import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def load_csv(filename, y_column, y_col_beat, currency_type):
    df = pd.pandas.read_csv(filename, usecols=['snapped_at',y_column])
    df = df.rename(index=str, columns={y_column: currency_type + " " +y_col_beat})
    df['Date'] =  pd.to_datetime(df['snapped_at'], format='%Y%m%d %H:%M:%S')
    df.set_index('Date',inplace=True)
    return df

def add_to_plot(btc_df,usd_df, btc_ax,usd_ax, color_):
    btc_df.plot(ax=btc_ax,color=color_)
    usd_df.plot(ax=usd_ax,alpha=0)

def plot_price(column):
    y_label_beat = "Price"
    if column != 'price':
        y_label_beat = "Market Cap"
    # Load Datasets
    steem_btc_df = load_csv('data/steem-btc-max.csv',column,y_label_beat, "STEEM" )
    steem_usd_df = load_csv('data/steem-usd-max.csv',column,y_label_beat, "STEEM")
    sdb_btc_df = load_csv('data/sbd-btc-max.csv',column,y_label_beat, "Steem Backed Dollar")
    sdb_usd_df = load_csv('data/sbd-usd-max.csv',column,y_label_beat,  "Steem Backed Dollar")

    # Make magic
    fig, ax = plt.subplots()
    ax1 = ax.twinx()
    # Add data
    add_to_plot(steem_btc_df,steem_usd_df,ax,ax1,'blue')
    add_to_plot(sdb_btc_df,sdb_usd_df,ax,ax1,'orange')
    ax1.legend_.remove()
    
    #set ticks every week
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    #set major ticks format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y %b'))
    ax.set_ylabel('Price[BTC]')
    ax1.set_ylabel('Price[USD]')
    # plot show 
    plt.show()
    fig.savefig(column +'.png',bbox_inches='tight') 

plot_price('price')
plot_price('market_cap')
