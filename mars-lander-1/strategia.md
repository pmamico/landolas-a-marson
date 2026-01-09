# Mars Lander — 1. epizód: Rövid összefoglaló és stratégiák

Röviden:
- Csak a tolóerőt szabályozzuk; a dőlésszög mindig 0 (nincs forgatás).
- Cél: biztonságos földet érni; a függőleges sebesség abszolútértékben legfeljebb 40 m/s érkezéskor.
- A lefelé irányuló sebesség negatív; a leszálló zóna alattunk van.
- A teljesítmény 0–4, és körönként legfeljebb ±1‑gyel változhat.

Egyszerű megközelítések:
- Küszöb alapú szabályozás (ajánlott kezdéshez)
  - Ha a függőleges sebesség nagyon nagy (pl. ≤ −40 m/s), kérj maximális teljesítményt.
  - Mérsékeltebb zuhanásnál elég a 3/2/1 fokozat; kis esésnél 0 is lehet.
  - Talajközelben emeld a minimumot: Y < 1500 → min 2; Y < 800 → min 3; Y < 300 → min 4.
- Célsebesség követése (egyszerű, PID‑mentes)
  - Válassz cél függőleges sebességet (pl. −35 m/s), tartsd, majd 500 m alatt fokozatosan csökkents −20…−10 m/s tartományra.
- Üzemanyagkímélő „késői fékezés”
  - Magasan kicsi vagy 0 teljesítmény, 800 m alatt agresszív fékezés 3–4‑re; kockázatosabb, pontos időzítést igényel.

Stratégiai pontok:
- Dőlésszög mindig 0 ezen a szinten.
- Tartsd be a teljesítmény változásának korlátját (legfeljebb egy fokozat körönként) és a 0–4 határokat.
- Gondolkodj „magassági kapukban”: 1500 m felett stabilizálás, 800 m alatt lassítás, 300 m alatt végfék.
- Ha a becsapódás előtt ~−20 m/s körül jársz, nem kell feltétlen a maximum.

Hasznos gyakorlati megjegyzések:
- Az inicializáláskor beolvasott felszínt itt nem kell felhasználni, de a formátum miatt kötelező beolvasni.
- A naplózást írd a hiba kimenetre, hogy ne zavarja a kimeneti parancsokat (CodinGame sajátosság).

Kapcsolódó kód:
- [mars-lander-episode-1.py](mars-lander-1/mars-lander-episode-1.py)
- [mars-lander-episode-1_just_in_time.py](mars-lander-1/mars-lander-episode-1_just_in_time.py)

## Just‑in‑time fékezés (üzemanyagkímélő)

Röviden:
- 0 tolóerő mindaddig, amíg a maradék magasság mellett éppen időben fékezhető a süllyedés.
- A leszállózóna Y magasságát a sík felszínszakaszból határozzuk meg.
- Kinematikai becslés a szükséges állandó tolóerőre: u_req = G + (v_f² − v²)/(-2·h), ahol G=3.711, v_f≈−39 m/s a cél.
- Csak akkor kezdünk fékezni, ha u_req ≥ 1 (kvantált teljesítmény miatt). Ezzel későn, de takarékosan fékezünk.
- Talajközelben (≈1.5 m) 1 másodperces előrenézéssel választjuk a legkisebb p‑t, hogy v_next ≥ −39 m/s legyen.
- Ha már elég lassú a süllyedés (v_speed ≥ −39), a teljesítmény 0 marad – így nem gyorsítunk „felfelé”.

Algoritmus lépései:
1) Inicializálás: felszín beolvasás, sík szakasz detektálása, landing_y meghatározása.
2) Körönként:
   - h_above = max(0, y − landing_y), v_limit = −39.
   - Ha v_speed ≥ v_limit → desired_power = 0.
   - Egyébként, ha h_above ≤ 1.5:
     - Keressük a legkisebb p∈[0..4] értéket, amire v_next = v_speed + (p − G) ≥ v_limit.
   - Különben kinematikai becslés:
     - u_req = G + (v_limit² − v_speed²)/(-2·h_above), 0..4 közé szorítva.
     - Ha u_req < 1 → desired_power = 0; különben desired_power = ceil(u_req).
   - next_power = clamp(desired_power, power−1, power+1), végül 0..4 közé szorítva.
   - rotate = 0 (ezen a szinten nincs döntés).

Miért működik:
- Üzemanyagkímélő: amíg lehet, 0 teljesítmény; csak akkor fékez, amikor fizikailag szükséges.
- Stabil: figyelembe veszi a diszkrét teljesítményt és a ±1/s változtatási korlátot.
- Nem „ránt fel”: v_speed ≥ −39 esetén 0 teljesítmény, talajközelben pedig a legkisebb szükséges p‑t választja.

Finomhangolás:
- v_limit: −35…−39 m/s között állítható a kockázati preferencia szerint.
- Talajközeli küszöb (1.0–2.0 m) és a ráhagyás (pl. kerekítési epsilon) módosítható.
- Ha kevés az üzemanyag, a módszer továbbra is a minimális szükséges fékezést célozza.

Peremhelyzetek:
- Ha nem található sík szakasz, landing_y = 0 (alapérték).
- Ha elfogy az üzemanyag, a továbbiakban 0 teljesítmény – ez már a pályától függően lehet kockázatos.
- Vízszintes sebesség ezen a szinten nem releváns; a dőlésszög végig 0.

Kapcsolódó kód:
- [mars-lander-episode-1_just_in_time.py](mars-lander-1/mars-lander-episode-1_just_in_time.py)