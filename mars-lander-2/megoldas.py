import sys
import math


def tavolsag_pont(hely1, hely2):
    # Euklideszi tavolsag ket pont (x, y) kozott
    return math.sqrt((hely1[0] - hely2[0]) ** 2 + (hely1[1] - hely2[1]) ** 2)


def tavolsag(c1, c2):
    return c1 - c2


def irany_sebesseg(vizszintes_sebesseg):
    # Vizszintes sebesseg elojele alapjan visszaadja az iranyt
    if vizszintes_sebesseg < 0:
        return -1
    else:
        return 1


def cel_irany(x, cel_x):
    # Megmondja, hogy a cel a jelenlegi x-hez kepest melyik oldalon talalhato
    if x > cel_x:
        return 1
    else:
        return -1


def mozgasi_fazis(x, vizszintes_sebesseg, fordulopont, leszallas_x):
    toloero = 4
    if x < fordulopont:
        forgatas = -30
    else:
        forgatas = 30
    if leszallas_x[0] < x < leszallas_x[1] and abs(vizszintes_sebesseg) < 2:
        forgatas = 0
        return forgatas, toloero, False, True, fordulopont
    return forgatas, toloero, True, False, fordulopont


def leszallasi_fazis(fuggoleges_sebesseg):
    if abs(fuggoleges_sebesseg) < 36:
        toloero = 2
    else:
        toloero = 4
    forgatas = 0
    return forgatas, toloero


def vezerles(kezdeti_stabilizalas_szukseges, kezdeti_vizszintes_sebesseg, vizszintes_sebesseg, fuggoleges_sebesseg, cel_gyors_h, leszallas_x, x, cel, mozgas, leszallas, fordulopont, pi):
    if kezdeti_stabilizalas_szukseges:
        toloero = 4
        irany = irany_sebesseg(kezdeti_vizszintes_sebesseg)
        try:
            alap_szog = int(math.asin(cel_gyors_h / toloero) * 180 / pi)
        except Exception:
            alap_szog = 0
        forgatas = irany * (alap_szog + 2)
        if fuggoleges_sebesseg > 0:
            toloero = 2
        if abs(vizszintes_sebesseg) < 2:
            forgatas = 0
            kezdeti_stabilizalas_szukseges = False
            if leszallas_x[0] < x < leszallas_x[1]:
                leszallas = True
            else:
                mozgas = True
                fordulopont = (x + cel[0]) // 2
            if mozgas:
                f, t, mozgas, leszallas, fordulopont = mozgasi_fazis(x, vizszintes_sebesseg, fordulopont, leszallas_x)
                return f, t, kezdeti_stabilizalas_szukseges, mozgas, leszallas, fordulopont
            if leszallas:
                f, t = leszallasi_fazis(fuggoleges_sebesseg)
                return f, t, kezdeti_stabilizalas_szukseges, mozgas, leszallas, fordulopont
        return forgatas, toloero, kezdeti_stabilizalas_szukseges, mozgas, leszallas, fordulopont
    else:
        if mozgas:
            f, t, mozgas, leszallas, fordulopont = mozgasi_fazis(x, vizszintes_sebesseg, fordulopont, leszallas_x)
            return f, t, kezdeti_stabilizalas_szukseges, mozgas, leszallas, fordulopont
        if leszallas:
            f, t = leszallasi_fazis(fuggoleges_sebesseg)
            return f, t, kezdeti_stabilizalas_szukseges, mozgas, leszallas, fordulopont
        return 0, 4, kezdeti_stabilizalas_szukseges, mozgas, leszallas, fordulopont


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
kezdeti_vizszintes_sebesseg = -1
kezdeti_fuggoleges_sebesseg = -1
kezdes_szamitas = True  # Kezdeti szamitas: cel gyorsulas/idok es kiindulo ertekek
ellensulyozni_kell = False  # Jelezi, hogy ellensulyozni kell-e a kezdeti vizszintes sebesseget
leszallas = False  # Leszallasi fazis
mozgas = False  # Mozgasi fazis
fordulopont = 0

# Jatek ciklus
while True:
    # Bemenet: x y vizszintes_sebesseg fuggoleges_sebesseg uzemanyag forgatasi_szog teljesitmeny
    x, y, vizszintes_sebesseg, fuggoleges_sebesseg, uzemanyag, forgatasi_szog, teljesitmeny = [int(i) for i in input().split()]

    tav_x = tavolsag(x, cel[0])

    # Vizszintes es fuggoleges gyorsulasi komponensek (teljesitmeny es forgatasi szog alapjan)
    gyors_h = teljesitmeny * math.sin(forgatasi_szog * (pi / 180))
    gyors_v = (teljesitmeny * math.cos(forgatasi_szog * (pi / 180))) - gravitacio  # Gravitacioval korrigalva

    # Kezdo szamitasok
    if kezdes_szamitas:
        # Kiindulo ertekek
        kezdo_tav_x = abs(tavolsag(x, cel[0]))
        kezdeti_vizszintes_sebesseg = vizszintes_sebesseg
        kezdeti_fuggoleges_sebesseg = fuggoleges_sebesseg
        # Cel ertekek
        cel_gyors_h = (kezdeti_vizszintes_sebesseg ** 2) / (2 * kezdo_tav_x) if kezdo_tav_x != 0 else 0  # Vizszintes gyorsulas
        try:
            cel_ido = (2 * kezdo_tav_x) // (kezdeti_vizszintes_sebesseg)
        except Exception:
            pass
        if abs(cel_gyors_h) < 2 and kezdeti_vizszintes_sebesseg != 0:
            print(0, 4)
            continue
        kezdes_szamitas = False  # Kesz a kezdeti kalkulacio
        if kezdeti_vizszintes_sebesseg != 0:
            ellensulyozni_kell = True
        else:
            mozgas = True
            fordulopont = (x + cel[0]) // 2

    # Fazisvezerles: ellensulyozas + mozgas/leszallas delegalva egy helyre
    forgatas, toloero, ellensulyozni_kell, mozgas, leszallas, fordulopont = vezerles(
        ellensulyozni_kell,
        kezdeti_vizszintes_sebesseg,
        vizszintes_sebesseg,
        fuggoleges_sebesseg,
        cel_gyors_h,
        leszallas_x,
        x,
        cel,
        mozgas,
        leszallas,
        fordulopont,
        pi
    )

    # Diagnosztikai uzenetek a hibakereseshez
    print('Aktualis cel: {}'.format(cel), file=sys.stderr)
    print('Kezdeti tavolsag X iranyban:', kezdo_tav_x, file=sys.stderr)
    print('Vizszintes gyorsulas: {}'.format(gyors_h), file=sys.stderr)
    print('Fuggoleges gyorsulas: {}'.format(gyors_v), file=sys.stderr)
    print('Tavolsag a sik felszinhez: ', tav_x, file=sys.stderr)

    # Kimenet: forgatasi szog (fok), toloero (0..4)
    print(forgatas, toloero)