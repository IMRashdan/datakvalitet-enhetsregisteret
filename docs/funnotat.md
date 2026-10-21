# Funnotat: datakvalitet i Enhetsregisteret


## Kort oppsummering

Jeg har kjørt tolv automatiserte kvalitetskontroller på 1 177 715 enheter fra Enhetsregisterets åpne data, og sammenstilt registeret med Postens postnummerregister. Kvaliteten er svært høy: sju av tolv kontroller fant ingen avvik, og de fem andre fant avvik i under 0,2 % av de kontrollerte enhetene. Avvikene er ikke tilfeldig spredt, men følger forklarbare mønstre. Det viktigste funnet er at alle 459 avvik mellom postnummer og poststed skyldes ett og samme postnummer, og kan rettes samlet.

## Resultater

| ID | Kontroll | Avvik | Andel |
|---|---|---:|---:|
| G01 | Gyldig organisasjonsnummer (mod11) | 0 | 0,000 % |
| G02 | Postnummer har fire sifre | 0 | 0,000 % |
| G03 | Gyldig format på næringskode | 0 | 0,000 % |
| G04 | Stiftelsesdato er ikke i fremtiden | 0 | 0,000 % |
| K01 | Forretningsadresse har postnummer | 0 | 0,000 % |
| K02 | Aksjeselskap har næringskode | 672 | 0,155 % |
| S01 | Stiftet før registrering | 481 | 0,071 % |
| S02 | Antall ansatte samsvarer med registrert ansattforhold | 0 | 0,000 % |
| S03 | Postnummer finnes i Postens register | 0 | 0,000 % |
| S04 | Poststed samsvarer med postnummer | 459 | 0,041 % |
| U01 | Unikt organisasjonsnummer | 0 | 0,000 % |
| U02 | Mulige duplikater (navn + postnummer) | 811 | 0,073 % |

## Hovedfunn

### 1. Alle poststedsavvik skyldes ett postnummer

**Hva:** 459 enheter har et poststed som ikke samsvarer med Postens register. Samtlige gjelder samme kombinasjon: Enhetsregisteret oppgir RANHEIM, mens Posten oppgir CHARLOTTENLUND for det samme postnummeret.

**Mulig årsak:** Mønsteret tyder på at Posten har endret poststedet for dette postnummeret, og at endringen ikke er fanget opp i adressene i Enhetsregisteret.

**Konsekvens:** Små hver for seg, men feil poststed kan gi problemer i adressevask, sammenstillinger med andre registre og utsending av post.

**Anbefaling:** Bekreft endringen med Posten og oppdater de 459 adressene samlet. Innfør en jevnlig sammenstilling mot Postens register, slik at fremtidige endringer fanges opp automatisk.

### 2. De fleste aksjeselskaper uten næringskode er nyregistrerte

**Hva:** 672 aksjeselskaper mangler næringskode. 546 av dem (81 %) er registrert i 2026. De fleste av de øvrige er registrert i 1995–2000.

**Mulig årsak:** Tallene tyder på at næringskoden settes en tid etter registreringen, slik at nye selskaper mangler den i en overgangsperiode. Enhetene fra 1995–2000 stammer trolig fra perioden da Enhetsregisteret ble opprettet, og kan være overført fra eldre registre uten næringskode.

**Konsekvens:** Det reelle restproblemet er rundt 120 eldre enheter, ikke 672. Uten denne nyansen vil kontrollen overdrive problemet.

**Anbefaling:** Del kontrollen i to: én som følger med på hvor lang tid det tar før nye selskaper får næringskode, og én som lister eldre selskaper som fortsatt mangler den, for manuell oppfølging.

### 3. Stiftelsesdato etter registrering betyr ulike ting for ulike organisasjonsformer

**Hva:** 481 enheter har stiftelsesdato etter registreringsdatoen. For aksjeselskaper (60 enheter) er avstanden kort, med en median på rundt 94 dager. For organisasjonsformer som FLI, SAM, IKS, KF og DA er avstanden typisk seks til åtte år.

**Mulig årsak:** Et aksjeselskap skal være stiftet før det registreres, så de 60 tilfellene er trolig feilregistreringer. For de andre organisasjonsformene tyder den lange avstanden heller på at stiftelsesdatoen kan gjenspeile en senere hendelse, for eksempel en omorganisering, enn på feil. Dette er en hypotese som bør bekreftes av fagmiljøet.

**Anbefaling:** Følg opp de 60 aksjeselskapene som sannsynlige feil. Avklar hvordan stiftelsesdato skal tolkes for de øvrige organisasjonsformene, og tilpass kontrollen etter det.

### 4. De fleste mulige duplikater er legitime

**Hva:** 811 enheter deler navn og postnummer med minst én annen enhet. Mange er borettslag, lag og foreninger med vanlige navn, noe som er forventet.

**Unntak:** Det finnes også aksjeselskaper med identisk navn i samme postnummer, for eksempel «AIRON AS» og «LB BYGG AS». Siden foretaksnavn skal være unike, bør disse undersøkes nærmere.

**Anbefaling:** Avgrens kontrollen til organisasjonsformer der navnet skal være unikt, slik at den gir færre falske treff og blir mer nyttig i praksis.

## Hva som ser bra ut

Organisasjonsnummer, postnummerformat, næringskodeformat, datoer og antall ansatte har ingen avvik. Alle postnumre finnes i Postens register. Det tyder på at disse feltene valideres allerede når enhetene registreres, og at kvalitetsarbeidet bør rettes mot felt som endres over tid, som adresser, og mot felt som fylles ut etter registrering, som næringskode.

## En erfaring fra metoden

Den første kjøringen av poststedskontrollen ga over 225 000 avvik, 20 % av alle enheter. Nærmere undersøkelse viste at årsaken var feil tegnkoding i den nedlastede filen fra Posten, der æ, ø og å var erstattet. Avvikene skyldtes altså referansedataene, ikke registeret. Innlastingen stopper nå med en tydelig feilmelding hvis referansefilen inneholder ødelagte tegn. Erfaringen viser hvorfor det er viktig å kontrollere kvaliteten på referansedata før man trekker konklusjoner om dataene som kontrolleres.

## Begrensninger

- Analysen bygger kun på åpne data. Skjermede opplysninger og slettede enheter er ikke med.
- Årsakene som beskrives er hypoteser basert på mønstre i dataene. De bør bekreftes av dataeier eller fagmiljøet.
- Duplikatkontrollen gir kandidater for manuell vurdering, ikke bekreftede feil.
- Analysen er et øyeblikksbilde fra oktober 2026.

## Videre arbeid

- Kjøre kontrollene jevnlig og følge utviklingen over tid, for eksempel i et dashboard.
- Sammenstille med SSBs kodeverk for næringskoder og kommuner for å kontrollere gyldige verdier, ikke bare format.
- Utvide kontrollene til postadresse, konkurs- og avviklingsstatus og underenheter.
