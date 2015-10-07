#str="1of"
#b=['3','4']
#c=''.join(b)+'\n'
#a = str.replace('of','')

#print(c+a)
#open('222', 'w').write(''.join(set(open('111').readlines())))
#import geopy
#googlev3 = geopy.GoogleV3()
#place,gps = googlev3.geocode(" 1805 Russell Rd Annville PA 17003 ")
#print (place)
#print (gps)
#for i in range(1,4):
    #print(i)
def call_1(a):
    print (str(a*2))

def call_2(b):
    print(str(-b))
    
def main_call(call_method,num):
    call_method(num)

main_call(call_2,3)

for i in range(0):
    print("hi")