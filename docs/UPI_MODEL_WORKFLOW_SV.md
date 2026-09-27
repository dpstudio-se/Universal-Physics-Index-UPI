# UPI modellarbetsflöde

**Standardspråk:** Engelska.  
**Syfte:** ta in nya AI-modeller utan att modellen får skriva om UPI:s regler.

\`\`\`
KÄLLA / IDÉ
   ↓
DISCOVER
   ↓
NORMALIZE
   ↓
CALCULATE
   ↓
CHECK
   ↓
MIRROR / INVERSE
   ↓
CLASSIFY
   ↓
SCHEMA VALIDATE
   ↓
SECURITY + INTEGRITY
   ↓
HUMAN REVIEW
   ↓
MERGE
\`\`\`

Grundregeln för matematik är enkel:

**Räkna → kontrollera → godkänn beräkningen eller stoppa.**

Nya modeller ska använda samma acceptanskriterier som äldre modeller. Modellnamnet är proveniens, inte evidens.

Spärren gäller ändringen, inte modellen:

- okänt vetenskapligt schemafält → \`STOP\`
- ogiltig JSON → \`STOP\`
- försök att höja ett publikt påstående till \`EST\` → avvisa
- saknad proveniens → \`STOP\`
- misslyckad beräkning → \`STOP\`
- misslyckad inverskontroll där invers krävs → \`STOP\`
- misslyckad CI/security-check → blockera merge

Målet är inte fler lager. Målet är rätt kontroll på rätt plats.
