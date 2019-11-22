
from pytrends.request import TrendReq


### Now let’s look at another time series plot with a different keyword search. Let’s search ‘Trump Halloween’:


### We can also define a function that allows us to compare the number of searches for many keywords:
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
def get_plot(key_words):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([key_words], cat=0, timeframe='2012-10-01 2019-11-15', gprop='',geo="US-NY")
    df = pytrends.interest_over_time()
    print(df.head(10))
    df['timestamp'] = df.index
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print(df.head())
    sns.set()
    ax = sns.lineplot(df['timestamp'], df[key_words], label = key_words)
    plt.ylabel("Number of Searchers")
    ax.legend()
    plt.show()
    return df
### Now we can call the function with many different keywords. Let’s stick to the pop culture searches:
get_plot("Linux")
get_plot("Ubuntu")


### To make a decision on our results we can define a function that returns the sum of the number of searches for a given keyword:
def get_sum(key_words):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([key_words], cat=0, timeframe='2019-10-01 2019-10-30', gprop='',geo="US-NY")
    df = pytrends.interest_over_time()
    print(df.head(10))
    df['timestamp'] = df.index
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print(df.head())
    return df[key_words].sum()
### And we can store the results in a dataframe and print the table:


