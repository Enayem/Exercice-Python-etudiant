Tour = input("Entrez votre nombre de tours:")
T = int(Tour)
list1=[]
A = []
B = []

for n in range(0,T):
    
    print("Temp au ",n,"eme","tour (en sec):")
    Timesec0 = input()
    list1 = [int(Timesec0)]
    A.append(list1)
    
print("Meilleur Temps au tour:",max(A),"secondes")

