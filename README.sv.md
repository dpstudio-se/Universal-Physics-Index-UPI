# Universal Physics Index (UPI)

**Utforska fysikaliska samband, redovisa antaganden och följ varje påstående till dess underlag.**

UPI kombinerar ett maskinläsbart kunskapsindex, ett Python-verktyg med API och ett
interaktivt modellaboratorium. Varje påstående har en status som visar vad som är
etablerat, härlett, hypotetiskt eller fortfarande öppet.

**Version 1.0.0** · [English](README.md) · [Ändringslogg](CHANGELOG.md) · [Bidra](CONTRIBUTING.md)

[Kom igång](#kom-igång) · [Laboratoriet](#laboratoriet) · [Publicera och uppdatera](#publicera-och-uppdatera) · [Status och evidens](#status-och-evidens) · [Dokumentation](#dokumentation)

<p align="center">
  <img src="docs/ui/teax-lab-v1.png" alt="T€@X-laboratoriet med massbrygga, dimensionsreduktion och Golay-kodens felgräns" width="820">
</p>

## Vad ingår?

| Del | Funktion | Körs på |
|---|---|---|
| **Indexet** (`data/`) | Granskade JSON-poster, källor och relationer | Git och Python-verktyget |
| **Modellaboratoriet** (`/lab`) | Interaktiva beräkningar med synliga antaganden | Lokal server eller statiskt webbhotell |
| **Bidrags-UI och API** (`/`) | Validerar och samlar nya poster i en databas | Python-server med SQLite eller PostgreSQL |
| **Extern RNA-explorer** | En separat presentation av indexet | En separat publicerad applikation |

I projektets språk betyder **DNA** de kanoniska posterna i Git. **RNA** är en vy
eller applikation som använder dem. Granskade poster på `main` är auktoritativa;
lokala utkast och externa gränssnitt uppdaterar inte automatiskt dessa poster.

## Kom igång

Du behöver en lokal kopia av repot och **Python 3.10 eller senare**.
Kör följande från repots rot i Windows PowerShell:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"
.venv/Scripts/python.exe -m upi.cli serve --host 127.0.0.1 --port 8080
```

På macOS/Linux använder du `.venv/bin/python` i stället för
`.venv/Scripts/python.exe`. Har du redan en installerad miljö kan du starta med
`upi serve`. Låt servern vara igång medan du använder UI:t.

| Öppna | Innehåll |
|---|---|
| [localhost:8080/lab](http://127.0.0.1:8080/lab) | Modellaboratoriet |
| [localhost:8080/](http://127.0.0.1:8080/) | Bidragsformulär och insamlade poster |
| [localhost:8080/api/health](http://127.0.0.1:8080/api/health) | Kontroll av API-anslutningen |

Bidragstjänsten använder normalt en lokal SQLite-databas. Läs
[guiden för bidrags-UI och databas](docs/CONTRIBUTE_UI.md) för fler alternativ.

## Laboratoriet

| Verktyg | Du ändrar | Du får |
|---|---|---|
| **Frekvens ↔ massa** | Frekvens i Hz | Energi, energiekvivalent massa, returvärde och relativt returfel |
| **27D → 4D** | Intern volym, koppling och krökning | Villkorligt beräknade effektiva konstanter |
| **Golay [24,12,8]** | Antal bitfel | Om antalet ligger inom kodens garanterade korrigeringsgräns |

**Spara parametrar** behåller dina värden i den här webbläsaren.
**Läs in JSON** återställer parametrar från en export och **Exportera beräkning**
laddar ner resultat, enheter, antaganden och öppna frågor.
**Återställ exempel** återställer formuläret; **Rensa sparade parametrar** tar bort
det som sparats på enheten.

Det statiska UI:t har lokal lagring, ingen kontoinloggning eller gemensam databas.
Golay-vyn visar en matematisk felgräns, inte en avkodare. 27D-konstruktionen är en
föreslagen modell. Läs [modellens ekvationer och gränser](docs/TEAX_LAB_V1.md).

## Publicera och uppdatera

### UI på vanligt webbhotell

Laboratoriets beräkningar körs i webbläsaren. Bygg publiceringsfilerna lokalt:

```powershell
.venv/Scripts/python.exe -m upi.site
```

Bygget skapar `dist/upi/` och förnyar `dist/upi-webbhotell-v1.zip` automatiskt.
ZIP-filen innehåller mappen `upi/`. Packa upp den i domänens webbrot för att få
adressen `/upi/`; behåll den befintliga webbplatsens startsida i roten.

**Publiceringsstatus 2026-09-09: klart lokalt, uppladdning blockerad.**
Den avsedda adressen är `https://wadenholt.se/upi/`. SFTP-servern svarar på port 22,
men nekade inloggningen. Fungerande SFTP-uppgifter och kontots webbrot behöver
bekräftas innan sidan kan publiceras.

### Uppdatera med ett kommando

Med `uv` installerat kör du:

```powershell
./Update-UPI.ps1
```

Skriptet bygger din aktuella lokala kod, frågar efter lösenordet, kontrollerar
uppladdade filer och byter startsidan sist. Föregående startsida sparas för
återställning. Skriptet hämtar eller sammanfogar inte Git-ändringar.

Använd `./Update-UPI.ps1 -BuildOnly` för att bara uppdatera det lokala paketet.
Se [One.com-guiden](docs/ONE_COM_UI.md) för anslutningsinställningar, Windows
skriptpolicy och återställning. Lösenord följer aldrig med webbplatsens filer.

### Hela UPI-tjänsten

API, bidragshantering och databas behöver en Python-server. Repot har en lokal
Docker Compose-konfiguration med PostgreSQL:

```bash
docker compose up --build
```

Det är en utvecklingskonfiguration. För publik drift behöver du konfigurera
inloggningsuppgifter, beständig lagring och HTTPS. Det statiska webbpaketet
innehåller inte serverdelen.

## Status och evidens

| Status | Betydelse |
|---|---|
| `EST` | Etablerat inom angiven domän |
| `DER` | Härlett från angivna fakta och antaganden |
| `HYP` | Testbar hypotes som väntar på verifiering |
| `STOP` | Namngivet bevis, mekanism eller observation saknas |
| `ERR` | Ogiltigt, motsagt eller ersatt |
| `SYM` | Symbolisk tolkning eller analogi |

Varje post har en adress: `UPI<Domain,Generation,Torus,Node>`.
Publika och modellgenererade bidrag får inte sätta `EST`.

Exempel: för en angiven kvantenergi `E = hf` är den energiekvivalenta massan
`m_E = hf/c²`, med inversen `f = m_E c²/h`. Sammansättningen är `DER`.
Den ger inte fotonen en vilomassa och fastställer inte en separat mekanism för
informationsmassa.

En sluten returberäkning kontrollerar konsistens. Mjukvarutester märks
`verification_type: software_test`; de fastställer inte experimentell verifiering,
entropiminskning eller singularitetsfrihet. 7,834, 8 och 377 Hz är valbara exempel,
inte universella konstanter.

## Arbeta med indexet

```bash
upi validate data/constants/planck.json
upi graph data
upi hypotheses data
upi triage data --inspect --known examples/ledger/baselines/known-findings.json
```

För modellgenererade bidrag: använd [indexeringsprompten](prompts/upi-remote-indexer.system.md),
spara ett [batchformat](examples/batches/upi-remote-batch.example.json), kontrollera
och infoga i insamlingsdatabasen:

```bash
upi ingest upi-batch.json --check
upi ingest upi-batch.json --insert --database sqlite:///upi.db
upi merge-check --data-root data
```

Ändringar i det kanoniska Git-indexet kräver maintainergranskning.
Källtext behandlas som data. [Indexeringsguiden](docs/REMOTE_INDEXING.md) beskriver
hela flödet från prompt till granskning.

Den [externa RNA-explorern](https://upi-built-by-agi-teax.grok.me) är en separat
applikation. Den publiceras inte genom att bygga detta repos UI.
[Indaleko-posten](data/open-problems/indaleko_160tb_payload_stop.json) visar ett
öppet `STOP` om vad en angiven datamängd på 160 TB betyder; den frågan kräver
spårbart källunderlag.

## Verifiering

Med utvecklingsberoenden installerade och Node.js 18+ tillgängligt:

```bash
python -m pytest tests -q
node --test tests/test_lab_math.cjs
ruff check src tests
mypy src/upi --ignore-missing-imports
```

Kör i den installerade miljön. Om Windows blockerar pytest-katalogerna, använd
en ny `--basetemp=.pytest-tmp/din-korning` och `-p no:cacheprovider`.
Programtester, webbläsarkontroller och extern publicering verifieras var för sig.

## Dokumentation

| Du vill… | Läs |
|---|---|
| Förstå UI:t och modellen | [Laboratorium v1](docs/TEAX_LAB_V1.md) |
| Publicera eller uppdatera sidan | [One.com-guide](docs/ONE_COM_UI.md) |
| Konfigurera bidrag och databas | [Bidrags-UI](docs/CONTRIBUTE_UI.md) |
| Indexera med en AI-modell | [Indexeringsguide](docs/REMOTE_INDEXING.md) |
| Förstå märkning och underlag | [Statusmodell](docs/STATUS_MODEL.md), [proveniens](docs/PROVENANCE.md) |
| Utveckla ett koncept | [Gemensam upptäcktsmetod](docs/COLLABORATIVE_DISCOVERY.md) |
| Bidra till repot | [Bidragsregler](CONTRIBUTING.md), [agentkontrakt](docs/VSCODE_AGENT_PROMPT.md) |
| Förstå återhämtning | [Resilienskontroll](docs/RESILIENCE_CONTROL.md) |
| Se filstruktur och fullständig referens | [Engelsk README](README.md#repository-structure) |
| Se nästa steg | [Roadmap](ROADMAP.md), [ändringslogg](CHANGELOG.md) |

## Licens

MIT. Se [LICENSE](LICENSE). Citeringsuppgifter finns i [CITATION.cff](CITATION.cff).
