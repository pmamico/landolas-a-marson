# Mars Lander — 2. epizód: Stratégia és feladatbontás

Röviden:
- Döntés megengedett ±30°-ig; a dőlésszög segítségével vízszintes gyorsítást/fékezést végzünk, hogy a leszállózóna fölé érjünk.
- Két fő cél: (1) eljutni a sík leszállózóna középvonalához, (2) ott stabil, biztonságos függőleges leszállást végrehajtani.
- Megvalósítás három fázisban: kezdeti vízszintes stabilizálás, megközelítés a zóna fölé, majd leszállási eljárás.
- A tolóerő 0..4 közötti, a kód egyszerűsítve közvetlenül állítja az értékeket; a dőlésszög a megközelítésnél ±30°, a leszállásnál 0°.
- A vertikális sebesség célkorlátja ~36 m/s körül (abszolútérték); ez alatt kisebb teljesítmény is elég lehet.


Amit le kell tudnunk programonzni::
- távolság két (x, y) pont között.
- Két skalár különbsége (itt főként az x‑távolság).
- A vízszintes sebesség előjele alapján irány meghatározása
- A cél az aktuális x‑hez képest melyik oldalon található?

Fő lépések:
1) Felszín beolvasása, sík szakasz detektálása és a leszállózóna meghatározása (x1, x2 és Y).
2) Célpont kijelölése: a sík szakasz közepe (x_c = (x1+x2)/2, y_c = Y). A kód naplózza a hibakimenetre.
3) Kezdeti kalkulációk:
   - induló vízszintes távolság a cél x‑től,
   - induló vízszintes és függőleges sebességek,
   - becsült szükséges vízszintes gyorsulás a megálláshoz/megtartáshoz.
4) Kezdeti stabilizálás (vízszintes sebesség ellensúlyozása):
   - nagy tolóerő (tipikusan 4), a dőlésszög előjele az induló vízszintes sebesség ellentettje,
   - ha a vízszintes sebesség nagysága 2 alá csökken, visszaállás 0°‑ra; ha ekkor már a zóna fölött vagyunk, áttérés a leszállásra, különben megközelítés.
5) Megközelítés a leszállózóna fölé:
   - teljesítmény 4, dőlésszög: ha a fordulópont előtt vagyunk, −30°, különben +30°,
   - amikor a zóna x‑tartományában és kis vízszintes sebességgel vagyunk, 0° dőlésszögre állás és váltás leszállásra.
6) Leszállási eljárás:
   - a dőlésszög 0°,
   - ha az abszolút függőleges sebesség < 36 m/s, elég közepes teljesítmény (pl. 2), különben 4.
7) Kimenet: mindig „forgatasi_szog teljesitmeny” formában kerül kiírásra; a diagnosztika a hibakimenetre megy.

Részfeladatok (mindegyik önálló metódus lesz):
- Felszín beolvasása és sík szakasz detektálása
  - Bemenet: a bemeneti pontok sorozata (x, y).
  - Kimenet: leszállózóna x‑tartománya (x1, x2) és magassága (Y).
- Célpont számítása a leszállózóna közepére
  - Bemenet: (x1, x2), Y.
  - Kimenet: célpozíció (x_c, y_c), ahol x_c = (x1+x2)/2 és y_c = Y.
- Kezdeti állapot és cél vízszintes gyorsulás becslése
  - Bemenet: aktuális x, v_x, v_y, cél x_c.
  - Kimenet: induló x‑távolság, induló sebességek, becsült horizontális lassítás/gyorsítás igény.
- Kezdeti vízszintes stabilizálás (ellenirányú döntés és nagy tolóerő)
  - Feladat: a vízszintes sebesség abszolútértékét ~2 alá csökkenteni, miközben a süllyedést nem engedjük el.
  - Kimenet: (forgatas, toloero) parancs és állapotváltás (megközelítés vagy leszállás).
- Megközelítés vezérlése fordulóponttal
  - Feladat: gyorsan a zóna fölé érni; dőlésszög: −30° a fordulópontig, utána +30°, toloero=4.
  - Kimenet: (forgatas, toloero) és váltás leszállási módba, ha a zónába értünk és kicsi a vízszintes sebesség.
- Leszállási vezérlés (0° dőlésszög)
  - Feladat: a függőleges sebességet 36 m/s alá szabályozni; ha gyors a süllyedés → toloero=4, különben 2.
  - Kimenet: (forgatas=0, toloero) a talaj érintéséig.
- Parancskiadás és diagnosztika
  - Feladat: a kiválasztott dőlésszög és teljesítmény kiírása; belső állapotok naplózása a hibakimenetre.

Összevetés az 1. epizóddal:
- Az 1. részben nem döntjük a hajót, csak a tolóerőt szabályozzuk; lásd: [mars-lander-1/strategia.md](mars-lander-1/strategia.md).
- Itt a döntés adja a vízszintes komponens kontrollját, ezért kétlépcsős a feladat: vízszintes pozicionálás, majd 0°‑on történő leszállás.