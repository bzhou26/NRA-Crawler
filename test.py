#str="1of"
#b=['3','4']
#c=''.join(b)+'\n'
#a = str.replace('of','')

#print(c+a)
#open('222', 'w').write(''.join(set(open('111').readlines())))
import geopy
googlev3 = geopy.GoogleV3()
place,gps = googlev3.geocode(" 1805 Russell Rd Annville PA 17003 ")
#print (place)
print (gps)
#for i in range(1,4):
    #print(i)
