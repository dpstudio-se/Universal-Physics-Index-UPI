# Repositoryanalys

Analysdatum: **2026-09-02**. Granskad basrevision:
`8cb4e6150beaf7df1fd6aebfe4ccfb887c022aec`.

Detta dokument är en reproducerbar programvarugranskning. Det bedömer inte om
fysikaliska påståenden är experimentellt sanna. Alla kommandon nedan är
`verification_type: software_test`.

## Problem

Analysera repositoryts struktur, README-filer, agentinstruktioner och aktuella
integritet utan att blanda ihop fyra skilda lager: kanonisk DNA-data,
paketbeteende, externa kopplingar och gränssnittsrendering.

## EST — direkt observerat

### Repository och ansvar

- `AGENTS.md` anger att icke-trivial felsökning ska dokumentera observationer
  före orsak, använda UPI-status och föredra `STOP` framför gissningar.
- `README.md` beskriver `data/` på `main` som kanoniskt DNA. RNA-sajten är en
  extern explorer och förslagsyta; den är inte kanonisk.
- Paketet är Python `>=3.10`, version `1.0.0`. Källkoden ligger i `src/upi/`,
  JSON-scheman i `schemas/`, kanoniska poster i `data/` och tester i `tests/`.
- Agentflödet är styrt, inte autonomt: publika modeller får skapa en batch men
  inte sätta `EST` eller skriva direkt till `data/`. `merge-check` producerar ett
  granskningspaket som kräver mänskligt godkännande.
- Den biologiska DNA/RNA/cirkulationsmodellen är uttryckligen `SYM`. Ingen
  scheduler, beständig kö, worker-sandbox eller karantän-runtime implementeras av
  metaforen.

### Reproducerad repositoryintegritet

- 94 JSON-filer hittades under `data/`; samtliga kunde avkodas som JSON-objekt.
- Statusfördelningen vid rå inspektion var 36 `EST`, 23 `DER`, 12 `HYP`, 11
  `STOP`, 11 `SYM` och en post utan toppnivåfältet `status`. Den sista är ett
  källmanifest och inte automatiskt en vetenskaplig nod.
- Den första testkörningen gav 118 godkända och 6 underkända tester. Två
  konkreta kod-/dataproblem har korrigerats i samma ändring: den nya runiska
  noden saknade `description`, och hypotesregistret tog felaktigt med `HYP`-broar
  trots att de saknar nodadress.
- Efter korrigeringarna laddas den kanoniska grafen och hypotesregistret igen.
  Planck-postens skyddstext uppfyller också testets uttryckliga ASCII-formatkrav.
  Den fulla sviten ger nu 122 godkända och två underkända tester; båda visar att
  triage-baslinjen inte motsvarar dagens data.
- `ruff check .` passerade. `mypy src` stannade på saknade typstubbar för
  `jsonschema` och den valfria PostgreSQL-modulen `psycopg`; detta är ett
  verktygsmiljöresultat, inte bevis för korrekt runtimebeteende.

## DER — slutsatser

1. **`DERIVED_FROM` EST repositorystruktur:** projektet har en tydlig
   auktoritetsgräns. JSON i git är den enda kanoniska kunskapsytan; UI, live-DB
   och LLM-batcher är transport- eller granskningsytor.
2. **`DERIVED_FROM` EST testresultat:** README:s huvudsakliga arkitekturbild
   stämmer med implementationens kataloger och CLI, men repositoryt var inte
   grönt på basrevisionen.
3. **`DERIVED_FROM` EST triageresultat:** den sparade kända katalogen innehåller
   endast tre fynd från det avsiktligt ogiltiga exemplet, medan den aktuella
   skannern rapporterar ytterligare evidens- och hypotesgränser i broar samt ett
   oklassificerat källmanifest. Baslinjen är därför inaktuell eller datamängden
   ofullständigt migrerad; observationen avgör inte vilket.

## HYP — falsifierbara kandidater

- **HYP-1:** triage-avvikelsen uppstod när evidensgränser skärptes utan att alla
  äldre broar migrerades och utan en ny godkänd baslinjekampanj.
  **Falsifieras av:** historik som visar att dagens scanner, data och
  baslinjefiler kördes tre identiska gånger efter den senaste dataändringen.
- **HYP-2:** README-bilderna visar den externa RNA-ytans avsedda funktioner.
  **Falsifieras av:** en reproducerbar deploymentkontroll där aktuell sajt inte
  kan rendera eller utföra motsvarande flöden. Bilder ensamma är `SYM`, inte
  runtimebevis.

## STOP

- **STOP-1 — triagegodkännande.** `stop_reason`: en ny känd-fynd-katalog får
  inte skapas genom att automatiskt godkänna 32 oväntade fynd. Minsta nästa
  observation är en maintainergranskning som för varje rapporterad bro väljer
  evidens/proveniens, nedgradering eller uttryckligt baslinjegodkännande.
- **STOP-2 — RNA/connector/UI.** `stop_reason`: ingen live-deployment eller
  browserkontroll ingick i denna lokala analys. Minsta nästa observation är en
  versionsidentifierad health/API-kontroll och en skärmbild från samma deploy.

## ERR — korrigerade eller motbevisade antaganden

- Antagandet att en lyckad JSON-avkodning innebär en laddningsbar graf var
  `ERR`: en klassificerbar nod kunde fortfarande sakna ett fält som
  `node_from_json` kräver.
- Antagandet att alla `HYP`-poster har `address` var `ERR`: broar identifieras av
  `source`, `target` och `relation`. Hypotesregistret filtrerar nu nod/theory.
- En grön enhetstestsvit skulle endast verifiera programvara inom testernas
  omfattning; den skulle inte etablera fysisk ekvivalens eller experimentell
  evidens.

## Reproduktion och kontrolltest

Kör från repositoryroten:

```bash
git rev-parse HEAD
find data -name '*.json' -type f | wc -l
PYTHONPATH=src pytest -q
ruff check .
PYTHONPATH=src upi graph data
PYTHONPATH=src upi triage data --inspect \
  --known examples/ledger/baselines/known-findings.json
```

Förväntat för repositoryintegritet är att grafen laddas och att testerna
passerar. Observerat på basrevisionen var grafundantag och sex testfel.
Korrigeringarna tar bort graf-/registerfelen; triage ska fortfarande eskalera
tills de oväntade fynden är granskade.

## Rekommenderad nästa åtgärd

1. Kör hela testsuiten efter denna patch och bekräfta att Planck-kontrollen är
   löst.
2. Exportera triagerapporten som granskningsartefakt.
3. Migrera eller nedgradera broarna en i taget; maskera inte fynden genom att
   direkt skriva om baslinjen.
4. Genomför därefter den dokumenterade tre-körningskampanjen och uppdatera
   baseline-hasharna med maintainergodkännande.
