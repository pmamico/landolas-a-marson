import sys
import math

# 1. rész, felszín pontjainak beolvasása
# Ebben a szintben a tájékozódáshoz nem kell a felszín, de gyakorlásként beolvassuk.
surface_n = int(input())
surface = []
for i in range(surface_n):
    land_x, land_y = [int(j) for j in input().split()]
    surface.append((land_x, land_y))

# 2. rész Stratégia röviden 
# Cél: biztonságos landolás.
# - A dőlésszög mindig 0 (függőleges helyzet).
# - A függőleges sebességet (fuggoleges_sebesseg) -40 m/s és 0 m/s között tartjuk.
# - Ha túl gyorsan esünk, növeljük a tolóerőt; ha lassulunk, csökkentjük, hogy spóroljunk az üzemanyaggal.
# - A játékban a teljesítmény (gaz) csak lépésenként változhat ±1-gyel, ezt betartjuk.

# 3. rész — Játékkörök (minden másodpercben kapunk friss adatokat)
while True:
    x, y, vizszintes_sebesseg, fuggoleges_sebesseg, benzin, forgatas, gaz = [int(i) for i in input().split()]

    # 3/a — Mindig függőlegesen tartjuk a hajót ezen a szinten
    cel_forgatas = 0

    # 3/b — Alapszabály: ha túl gyors az esés, emeljük a teljesítményt
    # Egyszerű lépcsőzetes szabály, amit könnyű követni és élőben magyarázni:
    if fuggoleges_sebesseg <= -40:
        szukseges_gaz = 4
    elif fuggoleges_sebesseg <= -30:
        szukseges_gaz = 3
    elif fuggoleges_sebesseg <= -20:
        szukseges_gaz = 2
    elif fuggoleges_sebesseg <= -10:
        szukseges_gaz = 1
    else:
        szukseges_gaz = 0

    # 3/c — Közeledve a talajhoz óvatosabb üzemmód
    # Minél alacsonyabban vagyunk, annál nagyobb minimum teljesítményt kérünk.
    if y < 500:
        szukseges_gaz = max(szukseges_gaz, 4)
    elif y < 1000:
        szukseges_gaz = max(szukseges_gaz, 3)
    elif y < 1500:
        szukseges_gaz = max(szukseges_gaz, 2)

    print(f"{cel_forgatas} {szukseges_gaz}")