import math
import collections
import re

# Explicit layer E(S): actual constitutional text gathered/verified in this session
# (RF 1:1, TF purpose, YGL purpose, RF 2:19 EKMR clause, RF 10:6 EU-overlatelse clause)
text = """
All offentlig makt i Sverige utgar fran folket. Folkstyrelsen bygger pa fri asiktsbildning
och pa allman och lika rostratt. Den forverkligas genom ett representativt och parlamentariskt
statsskick och genom kommunal sjalvstyrelse. Tryckfriheten innebar ratt att framstalla och
sprida tryckta skrifter utan foregaende censur och andra hinder. Yttrandefrihetsgrundlagen
innehaller bestammelser om ratt att sprida information och om forbud mot censur. Lag eller
annan foreskrift far ej meddelas i strid med Sveriges ataganden pa grund av den europeiska
konventionen angaende skydd for de manskliga rattigheterna och de grundlaggande friheterna.
Riksdagen kan overlata beslutanderatt till Europeiska unionen sa lange som unionen har ett
fri och rattighetsskydd motsvarande det som ges i regeringsformen samt i europeiska
konventionen om skydd for de manskliga rattigheterna och de grundlaggande friheterna.
"""
text = text.lower()

words = re.findall(r"[a-zåäö]+", text)
freqs = collections.Counter(words)
n = sum(freqs.values())
probs = [c / n for c in freqs.values()]
H = -sum(p * math.log2(p) for p in probs)
H_max = math.log2(len(freqs))

print("=== Odin's Eye layer 1: EXPLICIT (E(S)) ===")
print("tokens:", n)
print("unique words:", len(freqs))
print("Shannon entropy H (bits/word):", round(H, 4))
print("Max possible entropy (uniform dist over vocab):", round(H_max, 4))
print("Normalized entropy H/Hmax:", round(H / H_max, 4))
print()
print("Top 10 most frequent words (deep-structure candidate D(S)):")
for w, c in freqs.most_common(10):
    print(f"  {w:20s} {c}")

print()
print("=== Odin's Eye layer 3: SHADOW (SH(S)) ===")
print("Omitted from this corpus (not analyzed, not proof of absence in law):")
print("  - full TF 1949:105 statutory text (only regeringen.se summary used)")
print("  - full YGL 1991:1469 statutory text")
print("  - case law / KU and JO precedent")
print("  - AI Act Swedish-language full text")
