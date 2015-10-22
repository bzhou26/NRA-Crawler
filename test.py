#a = ("abc",'abc', "calgary","pa",10023,(12.9,13.8))
#b = ("abc",'abc', "calgary","pa",10023,(12.9,13.8))
#print(a==b)
#listc = [1,2,3,1,4,2]
#c = set(listc)
#c.add(22)
#print(c)

#a = set([1,2,3,2,1])
#b = list(a)

#a= [(1,2,3),"122",121]
#b= [(1,2,3),"12",121]
#c= [[(1,2,3),"122",121]]
#if b not in c:
    #print("hahaha")
#if a in c:
    #print("yes")
#def show_time(time):
    #hours = time//3600
    #minutes = (time//60)%60
    #seconds = time%60
    #print ("program runs for "+str(int(hours))+" hours, "+str(int(minutes))+" minutes, "+str(seconds)+" seconds.")

#show_time(1445121.74545841454)

#a=9
#import time
#time.#b=5
##c=a%b
##print (c)
#a= "123"
#b= str(a)
#print(b)


import geopy

googlev3 = geopy.GoogleV3()
place,gps = googlev3.geocode("  Indian Falls Road Corfu	NY 14036")
print (gps)