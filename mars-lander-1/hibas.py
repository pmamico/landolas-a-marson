import sys
import math

# Ebben a szintben a tájékozódáshoz nem kell a felszín, de gyakorlásként beolvassuk.
surface_n = int(input())
surface = []
for i in range(surface_n):
    land_x, land_y = [int(j) for j in input().split()]
    surface.append((land_x, land_y))

while True:
    x, y, vizszintes_sebesseg, fuggoleges_sebesseg, benzin, forgatas, gaz = [int(i) for i in input().split()]

    # Mindig függőlegesen tartjuk a hajót ezen a szinten
    cel_forgatas = 0

    szukseges_gaz = 0
    # Ez nem lesz jó, mert ha nincs gáz, gyorsan lezuhanunk
    # Megoldási irány: ha túl gyors az esés, emeljük a teljesítményt
    # lépcsőzetesen a fuggoleges_sebesseg alapján
    # Közeledve a talajhoz óvatosabb üzemmód kell!
    # Minél alacsonyabban vagyunk, annál nagyobb minimum teljesítményt szeretnénk.


    print(f"{cel_forgatas} {szukseges_gaz}")