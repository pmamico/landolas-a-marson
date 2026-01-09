import sys
import math

# Felszín beolvasása és a leszálló zóna magasságának meghatározása
felszin_pontok = int(input())
leszallo_y = None
elozo_x = None
elozo_y = None
for _ in range(felszin_pontok):
    pont_x, pont_y = [int(j) for j in input().split()]
    if elozo_y is not None and elozo_y == pont_y and leszallo_y is None:
        leszallo_y = pont_y
    elozo_x, elozo_y = pont_x, pont_y
if leszallo_y is None:
    leszallo_y = 0

G = 3.711

def korlatoz(ertek, also, felso):
    return max(also, min(felso, ertek))

while True:
    x, y, v_h, v_v, uzemanyag, elfordulas, akt_ero = [int(i) for i in input().split()]

    cel_elfordulas = 0

    mag_felett = max(0.0, y - leszallo_y)
    veg_v_hatar = -39.0

    szuk_u = None

    # Őr: ha már elég lassú az esés, tartsuk az erőt 0-n (megakadályozza a felfelé emelkedést)
    if v_v >= veg_v_hatar:
        kivant_ero = 0
    else:
        if mag_felett <= 1.5:
            # Egy másodperces előrelátás talajközelben: minimális teljesítmény, hogy a következő v >= cél
            kivant_ero = 0
            for p in range(0, 5):
                v_kov = v_v + (p - G)
                if v_kov >= veg_v_hatar:
                    kivant_ero = p
                    break
        else:
            # Minimális állandó tolóerő szükséges, hogy a leszálló szinten a függőleges sebesség ne legyen rosszabb, mint a határ
            # v^2 = v0^2 + 2*a*(-mag_felett)  =>  a_szuk = (v_f^2 - v0^2)/(-2*mag_felett)
            # tolóerő u = a + G
            szuk_u = G + (veg_v_hatar * veg_v_hatar - v_v * v_v) / (-2.0 * mag_felett)
            szuk_u = korlatoz(szuk_u, 0.0, 4.0)
            if szuk_u < 1.0:
                kivant_ero = 0
            else:
                kivant_ero = int(math.ceil(szuk_u - 1e-9))

    kov_ero = korlatoz(kivant_ero, akt_ero - 1, akt_ero + 1)
    kov_ero = korlatoz(kov_ero, 0, 4)

    debug_u = f"{szuk_u:.3f}" if szuk_u is not None else "n/a"
    print(f"x={x} y={y} vh/vv={v_h}/{v_v} uzemanyag={uzemanyag} aktEro={akt_ero} magFelett={mag_felett:.1f} szukU={debug_u} kivEro={kivant_ero} -> kovEro={kov_ero}", file=sys.stderr, flush=True)

    print(f"{cel_elfordulas} {kov_ero}")
