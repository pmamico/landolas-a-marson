import sys
import math

# 1. rész — Inicializálás: felszín pontjainak beolvasása
# Ebben a szintben a tájékozódáshoz nem kell a felszín, de a bemeneti formátum miatt beolvassuk.
surface_n = int(input())
surface = []
for i in range(surface_n):
    land_x, land_y = [int(j) for j in input().split()]
    surface.append((land_x, land_y))

# 2. rész — Stratégia röviden (magyarázat)
# Cél: biztonságos landolás.
# - A dőlésszög mindig 0 (függőleges helyzet).
# - A függőleges sebességet (v_speed) -40 m/s és 0 m/s között tartjuk.
# - Ha túl gyorsan esünk, növeljük a tolóerőt; ha lassulunk, csökkentjük, hogy spóroljunk az üzemanyaggal.
# - A játékban a teljesítmény (power) csak lépésenként változhat ±1-gyel, ezt betartjuk.

# 3. rész — Játékkörök (minden másodpercben kapunk friss adatokat)
while True:
    x, y, h_speed, v_speed, fuel, rotate, power = [int(i) for i in input().split()]

    # 3/a — Mindig függőlegesen tartjuk a hajót ezen a szinten
    target_rotate = 0

    # 3/b — Alapszabály: ha túl gyors az esés, emeljük a teljesítményt
    # Egyszerű lépcsőzetes szabály, amit könnyű követni és élőben magyarázni:
    if v_speed <= -40:
        desired_power = 4
    elif v_speed <= -30:
        desired_power = 3
    elif v_speed <= -20:
        desired_power = 2
    elif v_speed <= -10:
        desired_power = 1
    else:
        desired_power = 0

    # 3/c — Közeledve a talajhoz óvatosabb üzemmód
    # Minél alacsonyabban vagyunk, annál nagyobb minimum teljesítményt kérünk.
    if y < 300:
        desired_power = max(desired_power, 4)
    elif y < 800:
        desired_power = max(desired_power, 3)
    elif y < 1500:
        desired_power = max(desired_power, 2)

    # 3/d — A teljesítmény változását (±1) tiszteletben tartjuk
    def clamp(value, low, high):
        return max(low, min(high, value))

    next_power = clamp(desired_power, power - 1, power + 1)
    next_power = clamp(next_power, 0, 4)

    # 3/e — Oktatási célú debug (stderr-re írunk, a játék ezt figyelmen kívül hagyja)
    print(f"x={x} y={y} h={h_speed} v={v_speed} fuel={fuel} curP={power} desP={desired_power} -> outP={next_power}", file=sys.stderr, flush=True)

    # 3/f — Kimenet: dőlésszög és teljesítmény
    print(f"{target_rotate} {next_power}")