# BN Beszélő szék

Ez a projekt egy látványosság része volt, mely az ELTE KCSSK kollégium Budaörsi Napok rendezvényére készült, a Bolyai Club csapata, a Kérdőjel (?) által.

Hardveres részei:
  - egy fotel
  - egy sisak (alufólia, kartonpapír és vezetékek), 3db sárga LED-el, és egy mikrokapcsoló
  - sisakot fotelhez kapcsoló vezeték (két régi billentyűzet vezetéke összetoldva)
  - Raspberry PI 3 model B
  - USB hangszórók
  - WiFi router a távirányításért

A látványosság egy fotel volt, amelyre a kollégisták leülhettek, és egy fotelhez kapcsolt sisak segítségével "meghallgathatták az igazat". A sisakban egy kapcsoló aktiválódott amikor valaki feltette, és a fotelbe épített Raspberry PI lejátszott (szintén a fotelben elrejtett hangfalak segítségével) egy előre felvett mp3 fájlt.

A sisak feltételére való reakció mellett manuálisan is "beszéltetni lehetett" a fotelt. A kód host-ol egy statikus weboltalt, melyen egy szövegdoboz és néhány gomb látható, ezekkel manuálisan triggerelhető volt egy-egy lejátszás, a szövegdoboz tartalmát pedig PyTTSx3 segítségével felolvasta.

A sisakon az érzékelő mellett LED-ek is helyezkedtek el, melyek a figyelemfelhívás érdekében villogtak.

## Használat

**Figyelem! ez a projekt nincs karbantartva**

A kódot a következő parancssal lehet elindítani:

```
python3 speaking_chair_with_web.py
```
