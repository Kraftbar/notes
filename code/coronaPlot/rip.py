import os
dir_name=os.getcwd()
test = os.listdir(dir_name)

for item in test:
    if (item.endswith(".csv" ) or item.endswith(".html" ) ) :
        os.remove(os.path.join(dir_name, item))
import wget
# https://github.com/CSSEGISandData/COVID-19
url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'
url_update = 'https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series'

filename = wget.download(url)

filename = wget.download(url_update,"updatetimes.html")


import re
data =[]
with open('updatetimes.html', 'r') as file:
    data = file.read().replace('\n', '')    
tags = re.findall(r'datetime="(.+?)"', data)
updateDateTime = tags[-1]

# (?<=href=")[^"]*
from pandas import read_csv
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 20})

for item in test:
    if item.endswith(".csv"):
        data = read_csv(item)
        dataold=data
        dataold=dataold.drop(['Lat', 'Long',"Province/State"], axis=1)
        dataold=dataold.set_index("Country/Region")
        dataold=dataold.groupby("Country/Region").sum()
        i=0

        dataold=dataold.T
        dataold=dataold.drop(['Others'], axis=1)
        lol=dataold.index[-1]
        dataold=dataold.T
        dataold=dataold.sort_values(lol,ascending=False)


        dataold=dataold.T
        
        for (columnName, columnData) in dataold.iteritems():
            i=i+1
            if(i>1 and i<6): # skip china
                ts= columnData[28:-1].plot(style='o-',label=columnName,legend="dummy")
            if(columnName=="Norway"):
                ts= columnData[28:-1].plot(style='o-',label=columnName,legend="dummy")
        
        updateDateTime = updateDateTime.split("T")
        updateDate =updateDateTime[0].split("-")
       
        plt.title("Updated: " + updateDate[2] +"/"+updateDate[1] +", " + updateDateTime [1],fontsize=22)

        plt.yscale("log")
#
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

