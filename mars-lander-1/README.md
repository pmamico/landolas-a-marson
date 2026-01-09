# Mars Lander — 1. epizód

## Történet

Hajnali 2 óra. Hangos kiabálás visszhangzik az Űrközpont elhagyatott folyosóin.
„Az isten szerelmére, Mike! Kevesebb mint egy hónap múlva az indulás, és még mindig nincs megbízható megoldás!”  
  
Szögletes állkapocs, katonás hajviselet — Jeff a Mars küldetés vezetője, és éppen alapos fejmosást tart a vezető mérnökének.  

„De a szimulációk 99%-os sikerarányt mutatnak.”  
„Na és? Az az 1% óriási! Rátennéd a küldetés sikerét erre? Ne feledd, ha lezuhan, nekünk is végünk.”  
„A NASA legjobb mérnökei már dolgoztak ezen a projekten. Ennél jobbat nem tudunk elérni!”  
„Akkor vonjunk be külső erőforrásokat, és nézzük meg, születik‑e valami jobb.”  

## Leírás

A feladatod, hogy biztonságosan leszállítsd a „Mars Lander” űrhajót. Program vezérli a leszállást, és jelenleg a NASA szimulátorán a hibaarány elfogadhatatlan.  

Bár elsőre nehéznek tűnhet, valójában ez a feladvány egyszerű.  
Ez a háromszintű sorozat első szintje, ezért bemutatunk olyan vezérlőket is, amelyekre itt még nem lesz szükséged.
A szimulátor játékként működik: a Mars Lander egy korlátozott marsi légtérben mozog.  

- A pálya 7000 m széles és 3000 m magas.  
- Ebben a szintben a Mars Lander a leszálló zóna fölött, függőleges helyzetben és kezdősebesség nélkül indul.  
- A felszínen egyetlen, legalább 1000 m széles sík terület található.  

Minden másodpercben, a pillanatnyi repülési paraméterek (pozíció, sebesség, üzemanyag stb.) alapján a programnak meg kell adnia az új cél dőlésszöget és a hajtómű tolóerejét:  

- A dőlésszög tartománya: −90° ... 90°  
- A tolóerő tartománya: 0 ... 4  

Ezen a szinten csak a tolóerőt kell szabályoznod: a dőlésszög legyen mindig 0.  

A játék légkör nélküli szabadesést szimulál. A Mars gravitációja 3.711 m/s². X tolóerő mellett X m/s² gyorsulás keletkezik és X liter üzemanyagot fogyasztunk másodpercenként. Következésképp majdnem függőleges helyzetben a gravitáció ellensúlyozásához 4-es tolóerő szükséges.

Sikeres leszállás feltételei:  
- sík talajra érkezés,  
- függőleges helyzet (dőlésszög = 0°),  
- korlátozott függőleges sebesség (abszolút értékben ≤ 40 m/s),  
- korlátozott vízszintes sebesség (abszolút értékben ≤ 20 m/s).  

Egyszerűsítések ebben a szintben:  
- a leszálló zóna közvetlenül a jármű alatt van — a forgatást figyelmen kívül hagyhatod és mindig 0‑t adhatsz meg dőlésszögként;  
- a Mars felszínének pontjait nem szükséges eltárolni a megoldáshoz;  
- elegendő a függőleges leszállási sebességet 0 és 40 m/s közé korlátozni; a vízszintes sebesség 0.  
- zuhanáskor a függőleges sebesség negatív; emelkedéskor pozitív.  

Ezen az első szinten a Mars Lander egyetlen teszten megy keresztül.

A program először a bemenetet olvassa be a szabványos bemenetről. Ezután egy végtelen ciklusban minden körben beolvassa a Mars Lander aktuális állapotát, és utasításokat ír a szabványos kimenetre a mozgáshoz.  

## Bemenet

### Inicializálás
- 1. sor: egy egész szám, surfaceN — a Mars felszínét leíró pontok száma.
- A következő surfaceN sor: két egész, landX landY — egy talajpont koordinátái. A pontokat sorrendben összekötve kapjuk a Mars felszínének szegmenseit. Az első pontnál landX = 0, az utolsónál landX = 6999.

### Egy játékkör bemenete
- Egy sor, 7 egész számmal: X Y hSpeed vSpeed fuel rotate power
- X, Y: a Mars Lander koordinátái (m).
- hSpeed, vSpeed: a vízszintes és függőleges sebesség (m/s). Iránytól függően lehetnek negatívak.
- fuel: a maradék üzemanyag literben. Ha elfogy, a tolóerő automatikusan 0.
- rotate: a Mars Lander dőlésszöge fokban.
- power: a hajtómű tolóereje.

## Kimenet

### Egy játékkör kimenete
- Egy sor, 2 egész számmal: rotate power
- rotate: a kívánt dőlésszög. Minden körben a tényleges szög legfeljebb ±15°‑kal térhet el az előző kör értékétől.
- power: a kívánt tolóerő (0 = kikapcsolva, 4 = maximum). Minden körben a tényleges teljesítmény legfeljebb ±1‑gyel változhat az előző körhöz képest.

## Korlátozások
- 2 ≤ surfaceN < 30
- 0 ≤ X < 7000
- 0 ≤ Y < 3000
- −500 < hSpeed, vSpeed < 500
- 0 ≤ fuel ≤ 2000
- −90 ≤ rotate ≤ 90
- 0 ≤ power ≤ 4
- Válaszidő körönként ≤ 100 ms

## Példa bemenet

```text
6                          # surfaceN — 6 pontból áll a felszín
0 1500
1000 2000
2000 500                  # sík szakasz kezdete
3500 500                  # sík szakasz vége
5000 1500
6999 1000
```

_Nincs elvárt kimenet az inicializáláskor — a sorokat be kell olvasni._

1. kör bemenete:

```text
2500 2500 0 0 500 0 0      # X Y hSpeed vSpeed fuel rotate power
```

1. kör kimenete:

```text
0 3
```

2. kör bemenete:

```text
2500 2499 0 -3 499 0 1      # X Y hSpeed vSpeed fuel rotate power
```

2. kör kimenete:

```text
0 3
```

3. kör bemenete:

```text
2500 2495 0 -4 497 0 2      # X Y hSpeed vSpeed fuel rotate power
```

3. kör kimenete:

```text
0 2
```
