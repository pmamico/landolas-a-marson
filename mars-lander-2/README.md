# Mars Lander — 2. epizód

## Történet

Ugyanaz a helyszín, másnap. Jeffhez és Mike‑hoz csatlakoztál a Kennedy Űrközpont válságértekezletén.

„Oké, látom, érted a lényeget. Mike, mit gondolsz az új emberünkről eddig?”  
„Még hosszú az út áll előtte...”  
„Ugyan már, Mike, te mindig ilyen szkeptikus vagy!”  

Jeff acélkék szemekkel rád szegezi a tekintetét.  

„De IGAZA van! Az első teszt csak bemelegítés volt. 
Most nehezebb helyzetekkel kell megbirkóznod. 
Mindenre fel kell készülnünk — a küldetés sikere ezen múlik!”  

## Leírás

A feladatod, hogy biztonságosan leszállítsd a „Mars Lander” űrhajót, amely az Opportunity rovert szállítja. A leszállást egy program vezérli, és jelenleg a NASA szimulátorán a hibaarány elfogadhatatlan.

Ez a „Mars Lander” trilógia második szintje. A vezérlők megegyeznek az előző szinttel, de most már a dőlésszöget is irányítanod kell a sikerhez.

A szimulátor játékként működik: a Mars Lander egy korlátozott marsi légtérben mozog.

- A pálya 7000 m széles és 3000 m magas.
- A felszínen egyetlen, legalább 1000 m széles sík leszállóterület található.

Minden másodpercben, a pillanatnyi repülési paraméterek (pozíció, sebesség, üzemanyag stb.) alapján a programnak meg kell adnia az új cél dőlésszöget és a hajtómű tolóerejét.

A játék légkör nélküli szabadesést szimulál. A Mars gravitációja 3.711 m/s². X tolóerő mellett X m/s² gyorsulás keletkezik és másodpercenként X liter üzemanyagot fogyasztunk. Következésképp majdnem függőleges helyzetben a gravitáció ellensúlyozásához 4-es tolóerő szükséges.

Sikeres leszállás feltételei:
- sík talajra érkezés,
- függőleges helyzet (dőlésszög = 0°),
- korlátozott függőleges sebesség (abszolút értékben ≤ 40 m/s),
- korlátozott vízszintes sebesség (abszolút értékben ≤ 20 m/s).

Változások az 1. szinthez képest:
- a dőlésszöget aktívan szabályoznod kell, és vízszintesen is manőverezned kell a leszállózóna eléréséhez;
- a dőlésszög körönként legfeljebb ±15°‑kal, a tolóerő legfeljebb ±1‑gyel változhat.

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