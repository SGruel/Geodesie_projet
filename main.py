import  MC
import parse_pos
import proj

list_pos= parse_pos.recup_pos()

Xchap= MC.MC(list_pos)
j=0
for i in range (len(list_pos)):
    if not list_pos[i].parent:
        list_pos[i].X_MC = Xchap[j]
        j+=1
        list_pos[i].Y_MC = Xchap[j]
        j+=1
        list_pos[i].Z_mc = Xchap[j]
        j+=1
        list_pos[i].add_to_file("Resultats/resultats.csv")

points = proj.lecture("resultats.csv")
pr = proj.choix_proj_cc(points)

print('Paramètres de la projection conique conforme minimisant le module linéaire:\n', 'Phi0 =',\
      rad_to_deg(pr.phi0), '\n', 'Phi1 =', rad_to_deg(pr.phi1), '\n', 'Phi2 =',rad_to_deg(pr.phi2),\
      '\n', 'X0 :', pr.X0, 'Y0 :', pr.Y0, '\n', "ellipsoide de référence WGS 84")

proj.affiche(points, pr)

