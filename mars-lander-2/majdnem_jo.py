import sys
import math

# 1. rész — Inicializálás: felszín beolvasása és leszállózóna detektálása
surface_n = int(input())
surface = []
landing_left = None
landing_right = None
landing_y = None
prev = None
for _ in range(surface_n):
    land_x, land_y_point = [int(j) for j in input().split()]
    surface.append((land_x, land_y_point))
    if prev is not None:
        px, py = prev
        if py == land_y_point:
            landing_left = px
            landing_right = land_x
            landing_y = land_y_point
    prev = (land_x, land_y_point)

if landing_left is None:
    landing_left, landing_right, landing_y = 0, 6999, 0

G = 3.711

def clamp(value, low, high):
    return max(low, min(high, value))

def approach(cur, target, step):
    if cur < target:
        return min(cur + step, target)
    return max(cur - step, target)

# 2. rész — Segédfüggvények a célértékek meghatározásához
def select_v_limit(h_above):
    return -39

def desired_hspeed_for(dx, h_above):
    if abs(dx) <= 100:
        return 0.0
    if h_above > 1500:
        max_h = 60.0
        k = 1.0 / 8.0
    elif h_above > 800:
        max_h = 45.0
        k = 1.0 / 10.0
    else:
        max_h = 30.0
        k = 1.0 / 12.0
    return clamp(dx * k, -max_h, max_h)

while True:
    x, y, h_speed, v_speed, fuel, rotate, power = [int(i) for i in input().split()]

    center_x = 0.5 * (landing_left + landing_right)
    dx = center_x - x
    h_above = max(0.0, y - landing_y)

    v_limit = select_v_limit(h_above)

    inside_zone = landing_left <= x <= landing_right

    # 3/a — Vízszintes célsebesség és dőlésszög meghatározása
    target_hspeed = desired_hspeed_for(dx, h_above)
    if inside_zone:
        # A zónán belül a vízszintes sebességet lenullázzuk
        target_hspeed = 0.0
    else:
        # Közeledési folyosó: a leszállózóna körül alacsony magasságban korlátozzuk a cél hSpeed-et,
        # hogy belépéskor már kicsi legyen a vízszintes sebesség.
        zone_margin = 600
        ext_left = landing_left - zone_margin
        ext_right = landing_right + zone_margin
        if ext_left <= x <= ext_right and h_above < 1500:
            cap = 22.0 if h_above >= 800 else 18.0 if h_above >= 500 else 12.0
            target_hspeed = clamp(target_hspeed, -cap, cap)

    h_err = target_hspeed - h_speed
    # Arányos szabályozó -> cél dőlésszög
    target_rotate = int(clamp(-h_err * 1.1, -45.0, 45.0))

    # Zónán belül azonnal függőlegesen tartjuk a hajót
    if inside_zone:
        target_rotate = 0

    # Talajközelben is csak a zónában állunk teljesen függőlegesre

    # 3/b — Kimenet előkalkuláció: dőlésszögből vertikális komponens
    desired_power = 0

    # Zónán belül: függőleges süllyedés, nem döntünk oldalra
    # (Előfeltétel: a folyosó logika a belépés előtt lefékezi a vízszintes sebességet)

    # Ha NEM a zóna felett vagyunk és alacsonyan repülünk nagy vízszintes sebességgel, fékezzünk oldalra
    if not inside_zone and h_above < 600 and abs(h_speed) > 25:
        target_rotate = 45 if h_speed > 0 else -45


    # Biztonsági dőlésszög-korlát a szükséges vertikális komponenshez
    if inside_zone or h_above < 600:
        a_req_safety = (v_limit * v_limit - v_speed * v_speed) / (-2.0 * h_above) if h_above > 0.0 else 0.0
        cos_needed = (a_req_safety + G) / 4.0
        cos_needed = clamp(cos_needed, 0.0, 1.0)
        max_abs_tilt = 0 if cos_needed >= 1.0 else int(math.degrees(math.acos(cos_needed)))
        # Ha messze vagyunk a zónától, hagyjunk minimum dönthetőséget az oldalirányú fékezéshez
        if not inside_zone and abs(h_speed) > 40:
            max_abs_tilt = max(max_abs_tilt, 15)
        # Ha nagyon gyors az esés, limitáljuk a dőlést
        if v_speed < v_limit - 10:
            max_abs_tilt = min(max_abs_tilt, 20)
        target_rotate = int(clamp(target_rotate, -max_abs_tilt, max_abs_tilt))

    # A következő körben elérhető dőlésszög (±15° limit)
    preview_rotate = int(clamp(approach(rotate, target_rotate, 15), -90, 90))
    cos_v = max(0.1, math.cos(math.radians(preview_rotate)))  # vertikális tolóerő-komponens

    # 3/c — Teljesítmény becslése kinematikával a vertikális komponensre
    # Cél: v_speed >= v_limit legyen, mire elérjük a landing_y-t
    if v_speed >= v_limit:
        desired_power = 0
    else:
        if h_above <= 1.5:
            # 1 mp-es előrenézés a talaj közelében
            desired_power = 0
            for p in range(0, 5):
                v_next = v_speed + (p * cos_v - G)
                if v_next >= v_limit:
                    desired_power = p
                    break
        else:
            # v^2 = v0^2 + 2*a*s, ahol s = -h_above, a = u*cos(theta) - G
            a_req = (v_limit * v_limit - v_speed * v_speed) / (-2.0 * h_above)
            u_req = (a_req + G) / cos_v
            u_req = clamp(u_req, 0.0, 4.0)
            desired_power = 0 if u_req < 1.0 else int(math.ceil(u_req - 1e-9))

    # Dőlésszög miatti óvatosság
    if abs(preview_rotate) > 35:
        desired_power = max(desired_power, 4)
    elif abs(preview_rotate) > 20:
        desired_power = max(desired_power, 3)

    # Magasság-alapú minimum teljesítmény
    if h_above < 150:
        desired_power = max(desired_power, 4)
    elif h_above < 500:
        desired_power = max(desired_power, 3)
    elif h_above < 1000:
        desired_power = max(desired_power, 2)

    # 3/d — A kimeneti értékek változási limitjeinek betartása
    next_power = clamp(desired_power, power - 1, power + 1)
    next_power = clamp(next_power, 0, 4)

    next_rotate = preview_rotate

    # 3/d — Oktatási céljú debug (stderr-re írunk)
    print(
        f"x={x} y={y} hv={h_speed}/{v_speed} fuel={fuel} "
        f"land=({landing_left},{landing_right}) yL={landing_y} dx={dx:.1f} hAbove={h_above:.1f} "
        f"tHS={target_hspeed:.1f} tRot={target_rotate} vLim={v_limit} "
        f"curRot/P={rotate}/{power} -> outRot/P={next_rotate}/{next_power}",
        file=sys.stderr,
        flush=True
    )

    # 3/e — Kimenet
    print(f"{next_rotate} {next_power}")