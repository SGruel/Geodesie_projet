import  MC
import parse_pos


list_pos= parse_pos.recup_pos()

Xchap= MC.MC(list_pos)
j=0
for i in range (len(list_pos)):
    list_pos[i].X_mc = Xchap[j]
    j+=1
    list_pos[i].Y_mc = Xchap[j]
    j+=1
    list_pos[i].Z_mc = Xchap[j]
    j+=1
    list_pos[i].add_to_file("resultats.csv")
    
