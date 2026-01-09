import sys
import math


def tavolsag_tup(hely1, hely2):
    # Euklideszi tavolsag ket pont (x, y) kozott
    return math.sqrt((hely1[0] - hely2[0]) ** 2 + (hely1[1] - hely2[1]) ** 2)


def tavolsag_pont(c1, c2):
    # Kulonbseg ket skalar kozott (itt x-koordinata tavolsaga)
    return c1 - c2


def irany_sebesseg(h_seb):
    # Vizszintes sebesseg elojele alapjan visszaadja az iranyt
    if h_seb < 0:
        return -1
    else:
        return 1


def cel_irany(x, cel_x):
    # Megmondja, hogy a cel a jelenlegi x-hez kepest melyik oldalon talalhato
    if x > cel_x:
        return 1
    else:
        return -1


elozo_x, elozo_y, felszin_x, felszin_y = 0, 0, 1, 1

felszin_pontok_szama = int(input())  # a Mars felszinenek kirajzolasahoz hasznalt pontok szama
for i in range(felszin_pontok_szama):
    elozo_x, elozo_y = felszin_x, felszin_y
    felszin_x, felszin_y = [int(j) for j in input().split()]
    if felszin_y == elozo_y:
        leszallas_x = (elozo_x, felszin_x)
        leszallas_y = felszin_y

# Cel meghatarozasa
cel = ((leszallas_x[0] + leszallas_x[1]) // 2, leszallas_y)  # pontosan a kozepen
print('Cel kijelolve - {}'.format(cel), file=sys.stderr)

# Allandok es allapotjelzok
gravitacio = 3.711  # Mars gravitacio
pi = math.pi
kezdo_tav_x = -1
kezdo_h_seb = -1
kezdo_v_seb = -1
kezdes_szamitas = True  # Kezdeti szamitas: cel gyorsulas/idok es kiindulo ertekek
kezdo_mozgas_ellent = False  # Jelezi, hogy ellensulyozni kell-e a kezdeti vizszintes sebesseget
leszallas = False  # Leszallasi fazis
mozgas = False  # Mozgasi fazis

# Jatek ciklus
while True:
    # Bemenet: x y h_seb v_seb uzemanyag forgatasi_szog teljesitmeny
    x, y, h_seb, v_seb, uzemanyag, forgatasi_szog, teljesitmeny = [int(i) for i in input().split()]

    tav_x = tavolsag_pont(x, cel[0])

    # Vizszintes es fuggoleges gyorsulasi komponensek (teljesitmeny es forgatasi szog alapjan)
    gyors_h = teljesitmeny * math.sin(forgatasi_szog * (pi / 180))
    gyors_v = (teljesitmeny * math.cos(forgatasi_szog * (pi / 180))) - gravitacio  # Gravitacioval korrigalva

    # Kezdo szamitasok
    if kezdes_szamitas:
        # Kiindulo ertekek
        kezdo_tav_x = abs(tavolsag_pont(x, cel[0]))
        kezdo_h_seb = h_seb
        kezdo_v_seb = v_seb
        # Cel ertekek
        szukseges_vizszintes_gyorsulas = (kezdo_h_seb ** 2) / (2 * kezdo_tav_x) if kezdo_tav_x != 0 else 0  # Vizszintes gyorsulas
        try:
            cel_ido = (2 * kezdo_tav_x) // (kezdo_h_seb)
        except Exception:
            pass
        if abs(szukseges_vizszintes_gyorsulas) < 2 and kezdo_h_seb != 0:
            print(0, 4)
            continue
        kezdes_szamitas = False  # Kesz a kezdeti kalkulacio
        if kezdo_h_seb != 0:
            kezdo_mozgas_ellent = True
        else:
            mozgas = True
            fordulopont = (x + cel[0]) // 2

    # Stabilizalas kezdeti mozgassal szemben
    if kezdo_mozgas_ellent is True:
        toloero = 4  # Fix toloero a gyors fekezeshez
        irany = -irany_sebesseg(kezdo_h_seb)  # Ellensulyozzuk az indulasi iranyt
        forgatas = irany * (int(math.asin(szukseges_vizszintes_gyorsulas / toloero) * 180 / pi) + 2)
        if v_seb > 0:
            toloero = 2
        if abs(h_seb) < 2:
            forgatas = 0
            kezdo_mozgas_ellent = False  # Stabilizaltuk a vizszintes mozgast
            # Eldontjuk, hogy zonaban vagyunk-e
            if leszallas_x[0] < x < leszallas_x[1]:  # Leszallasi zonaban vagyunk
                leszallas = True
            else:  # Tulcsuszas vagy tul korai fekezes
                mozgas = True
                fordulopont = (x + cel[0]) // 2

    # Mozgasi fazis
    if mozgas is True:
        toloero = 4
        if x < fordulopont:
            forgatas = -30
        elif x >= fordulopont:
            forgatas = 30

        if leszallas_x[0] < x < leszallas_x[1] and abs(h_seb) < 2:
            mozgas = False
            leszallas = True
            mozgas_irany = -1
            forgatas = 0

    # Leszallasi eljaras
    if leszallas is True:
        if abs(v_seb) < 36:
            toloero = 1
        else:
            toloero = 3

    # Diagnosztikai uzenetek a hibakereseshez
    print('Aktualis cel: {}'.format(cel), file=sys.stderr)
    print('Kezdeti tavolsag X iranyban:', kezdo_tav_x, file=sys.stderr)
    print('Vizszintes gyorsulas: {}'.format(gyors_h), file=sys.stderr)
    print('Fuggoleges gyorsulas: {}'.format(gyors_v), file=sys.stderr)
    print('Tavolsag a sik felszinhez: ', tav_x, file=sys.stderr)

    # Kimenet: forgatasi szog (fok), toloero (0..4)
    print(forgatas, toloero)