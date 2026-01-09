import sys
import math

# Read surface and detect landing zone altitude
surface_n = int(input())
landing_y = None
prev_x = None
prev_y = None
for _ in range(surface_n):
    land_x, land_y_point = [int(j) for j in input().split()]
    if prev_y is not None and prev_y == land_y_point and landing_y is None:
        landing_y = land_y_point
    prev_x, prev_y = land_x, land_y_point
if landing_y is None:
    landing_y = 0

G = 3.711

def clamp(value, low, high):
    return max(low, min(high, value))

while True:
    x, y, h_speed, v_speed, fuel, rotate, power = [int(i) for i in input().split()]

    target_rotate = 0

    h_above = max(0.0, y - landing_y)
    v_final_limit = -39.0

    u_req = None

    # Guard: if already slow enough, keep power 0 (prevents upward flight)
    if v_speed >= v_final_limit:
        desired_power = 0
    else:
        if h_above <= 1.5:
            # One-second lookahead near ground: minimal p so that next v >= target
            desired_power = 0
            for p in range(0, 5):
                v_next = v_speed + (p - G)
                if v_next >= v_final_limit:
                    desired_power = p
                    break
        else:
            # Minimal constant thrust needed so that at y=landing_y the vertical speed is not worse than v_final_limit
            # v^2 = v0^2 + 2*a*(-h_above)  =>  a_req = (v_f^2 - v0^2)/(-2*h_above)
            # thrust u = a + G
            u_req = G + (v_final_limit * v_final_limit - v_speed * v_speed) / (-2.0 * h_above)
            u_req = clamp(u_req, 0.0, 4.0)
            if u_req < 1.0:
                desired_power = 0
            else:
                desired_power = int(math.ceil(u_req - 1e-9))

    next_power = clamp(desired_power, power - 1, power + 1)
    next_power = clamp(next_power, 0, 4)

    debug_u = f"{u_req:.3f}" if u_req is not None else "n/a"
    print(f"x={x} y={y} hv={h_speed}/{v_speed} fuel={fuel} curP={power} hAbove={h_above:.1f} uReq={debug_u} desP={desired_power} -> outP={next_power}", file=sys.stderr, flush=True)

    print(f"{target_rotate} {next_power}")