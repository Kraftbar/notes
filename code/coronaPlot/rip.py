import os
dir_name=os.getcwd()
test = os.listdir(dir_name)

for item in test:
    if item.endswith(".csv"):
        os.remove(os.path.join(dir_name, item))
import wget
url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'
filename = wget.download(url)



import matplotlib.pyplot as plt
from pandas import read_csv
import pandas as pd

for item in test:
    if item.endswith(".csv"):
        data = read_csv(item)
        dataold=data
        dataold=dataold.drop(['Lat', 'Long',"Province/State"], axis=1)
        dataold=dataold.set_index("Country/Region")
        dataold=dataold.groupby("Country/Region").sum()
        

        i=0
 #   
        dataold=dataold.T
        for (columnName, columnData) in dataold.iteritems():
            i=i+1
            print(columnName)
            columnData.plot(label=columnName,legend="as")
            if(i==20):
                break
        plt.yscale("log")
                


 #       new = data["Country/Region"].copy() 
 #       data["Province/State"]= data["Province/State"].str.cat(new, sep =", ") 
 #       data=data.drop(['Lat', 'Long',"Country/Region"], axis=1)
 #       data=data.T
 #       i=0
 #       for (columnName, columnData) in data.iteritems():
 #           if(columnName=="0" ):
 #               print("bra")
 #           else:
 #               print(columnData[0])
 #               columnData[1:].plot(label=columnData[0],legend="as")
#            i=i+1
#            if(i==20):
#                break
#        plt.yscale("log")

#        data.time = pd.to_datetime(data['Province/State'], format='%m/%d/%Y')

#        data.set_index(['Province/State'],inplace=True)

