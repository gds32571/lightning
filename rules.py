# rules file for the detect program

def myRules(strikedelta,stormDistance):
    
 
    if strikedelta > 25 and stormDistance < 5:
       prob = 100   
    elif strikedelta > 15 and stormDistance < 8:
       prob = 95   
    elif strikedelta > 5 and stormDistance < 10:
       prob = 90   
    elif strikedelta > 3 and stormDistance < 13:
       prob = 60
    elif strikedelta > 1 and stormDistance < 18:
       prob = 30
    elif strikedelta == 1 and stormDistance < 16:
       prob = 20
    elif strikedelta == 0 and stormDistance < 6:
       prob = 5
    else:
       prob = 0
#    print(strikedelta,stormDistance,prob)

    return prob