# Phase 0 — Ising-Kalibrierung: wissenschaftlicher Prüfbericht

**Stand:** 2026-10-09. **Entscheidung: NO-GO für einen uneingeschränkten Übergang zu Phase 1.**
**Status:** Prüfbericht auf einem **unintegrierten, gestapelten Arbeitsbranch**; keine der offenen Ising-PRs ist durch menschliche Reviewer freigegeben. Die folgenden numerischen Beobachtungen sind Benchmarks, **keine** Resultate zu fundamentaler Raumzeit.

## A. Ziel und Evidenzkategorien

Phase 0 soll Sampler, exakte Benchmarks, Starttransienten, Autokorrelation, unabhängige Replikate, Intervallabdeckung, Größenabhängigkeit, Nullmodelle und Reproduzierbarkeit als **Messinstrumente** prüfen. Das Quadratgitter, seine zweidimensionale Topologie, Wechselwirkung, periodische Randbedingungen und die Metropolis-/Checkerboard-Regeln werden **angenommen**. Die bekannten 2D-Ising-Gesetze sind externe Theorie, keine Entdeckung.

**Mathematische Referenzen:** Für unendliche quadratische Gitter gilt bei J=k_B=1: `T_c=2/ln(1+sqrt(2)) ≈ 2.269185`; bekannte Exponenten `ν=1`, `β=1/8`, `γ=7/4`. Für L=4 wird die endliche kanonische Verteilung unabhängig vom MC-Sampler durch Enumeration aller 65536 Konfigurationen berechnet. Diese Referenz ist eine exakte endliche Summe (mit Fließkommarundung bei der Auswertung), **keine** unendliche-Gitter-Extrapolation.

**Evidenzhierarchie:** (1) Modellannahme: Gitter/Regeln. (2) Mathematisch bekannte Theorie: Tc und Exponenten. (3) numerische Beobachtung: nachfolgende Werte mit Konfiguration und Quellartefakten. (4) Hypothese: Fehlerdiagnostik generalisiert auf Phase-1-Modelle. Diese letzte Hypothese ist **nicht belegt**.

## B. Prüfumfang und Ausgangslage (GitHub)

Stand der gestapelten Ising-Arbeiten bei Prüfung: PR [#1](https://github.com/shaden7/emergence-lab/pull/1) (Autokorrelation) → [#3](https://github.com/shaden7/emergence-lab/pull/3) (exakt L4) → [#7](https://github.com/shaden7/emergence-lab/pull/7) (Provenienz) → [#9](https://github.com/shaden7/emergence-lab/pull/9) (Coverage) → [#10](https://github.com/shaden7/emergence-lab/pull/10) (Burn-in). **Alle offen; für #1/#3/#7/#9/#10 waren keine Reviews abrufbar.** Der vorliegende Prüfbranch baut isoliert auf #10 auf; keine fremden Heads überschrieben, nichts nach main gemergt. PR [#5](https://github.com/shaden7/emergence-lab/pull/5) (repräsentationsneutrale Strategie), Draft-PR [#8](https://github.com/shaden7/emergence-lab/pull/8) (Literatur zu Issue #6) und PR #11 (Pilot-A-Präregistrierung) sind andere offene Arbeiten.

**Validierte Ausgangsartefakte:**
- [M3 / L4-Holdout, CI 37987761035](https://github.com/shaden7/emergence-lab/actions/runs/37987761035): 3 Temperaturen × 12 unabhängige Ketten; maximal 0.793 beobachtete Standardfehler Abstand zur unabhängigen Enumeration. Das war ein vorab definierter **explorativer** 3.5-SEM-Anomalietest, kein Beweis korrekter Intervallabdeckung.
- [M4-Coverage, CI 37994539424](https://github.com/shaden7/emergence-lab/actions/runs/37994539424), Artefakt **11646079121**: 3 × 24 × 6 = **432** Ketten, jeweils 400 Burn- und 800 Sampling-Sweeps, alle 5 Sweeps gemessen, Basis-Seed `2027010101`. Revision `d4169cffdb87dfd93aebefb5da2e4f27a13b292d`, Python 3.12.15 / NumPy 2.5.3.
- [M4-Burn-in, CI 37995173975](https://github.com/shaden7/emergence-lab/actions/runs/37995173975), Artefakt **11647295336**: 3 Temperaturen × 10 Gruppen × 4 Ketten × 4 Burn-in-Varianten = **480** Ketten; Burn-in 0/100/400/1600, 800 Sampling-Sweeps alle fünf, Basis-Seed `2027021001`. Ausführungsrevision `7518f095e4776b3c8a751c354ada320350d80648`, Python 3.12.15 / NumPy 2.5.3.
- **Nachprüfung ausgeführt:** Beide unverfallenen Actions-ZIPs über GitHub-Connector heruntergeladen, enthaltene JSONs/CSV gelesen; 6 M4-Aggregate, 24 Burn-in-Armzellen und 18 paarweise Vergleiche aus Einzelbatches lokal neu berechnet. Implementierung: `scripts/phase0_artifact_audit.py`; Aufruf am Ende. Keine Server- oder Lightsail-Last.

### B1. Konfidenzintervall-Abdeckung (M4, nominal 95 %)

| Temperatur | Energie: beobachtet (Wilson 95 %) | |M|: beobachtet (Wilson 95 %) |
| --- | --- | --- |
| 1.5 | 23/24 = 95.8 % (79.8–99.3 %) | 23/24 (79.8–99.3 %) |
| 2.269185 | 23/24 (79.8–99.3 %) | 24/24 (86.2–100 %) |
| 3.5 | 22/24 = 91.7 % (74.2–97.7 %) | 22/24 (74.2–97.7 %) |

Diese Intervalle sind **Wilson-Unsicherheiten der gemessenen Abdeckungsanteile**, nicht die MC-Intervalle selbst. Für sechs korrelierte Zellen liegen keine simultanen Coverage-Garantien vor. Student-t über **sechs unabhängig gestartete Kettenmittelwerte pro Batch** setzt angenäherte Normalität, ausreichend gemischte Ketten und keine gemeinsamen systematischen Startfehler voraus. Ein einzelner Holdout oder 24 Batches können die gewünschte 95-%-Abdeckung nicht beweisen. Fehlende signifikante Unterdeckung ist **kein** positiver Nachweis.

Zusätzliche Batchmittel-Biaswerte relativ zur exakten Referenz bei T=2.269185: Energie **−0.004330** (95-%-t-Intervall über 24 Batches ca. **[−0.01126, 0.00260]**), |M| **+0.001777** (ca. **[−0.00117, 0.00473]**). Keine Auffälligkeit in diesen Aggregaten, aber geringe Aussagekraft für andere L und langsamere Modi.

### B2. Burn-in: **Starttransient statt Gleichgewichtsbeweis**

Mit **0 Burn-in** und T=1.5 weicht die Energie im Mittel um **+0.00693** vom exakten Erwartungswert ab, t-95-%-Intervall über **zehn Batches**: ungefähr **[+0.00264,+0.01122]**; bei |M| **−0.00324**, ungefähr **[−0.00440,−0.00208]**. Dies ist ein Hinweis auf einen Starttransienten in der gewählten kurzen Messung, keine multiple-testkorrigierte Signifikanzfeststellung.

**Gepaarter Unterschied 100 gegenüber 0 Burn-Sweeps** bei T=1.5: Energie **−0.008594 ± 0.003583** (t-95-%-Halbbreite), |M| **+0.003887 ± 0.001109**. Bei T≈Tc Energie **−0.011250 ± 0.005737**, |M| **+0.005039 ± 0.002196**. Die 18 angezeigten Kontraste verwenden **dieselben Seeds** pro Arm, aber andere Ausschnitte/Positionen der Zufallstrajektorien; sie sind korreliert, **keine** gemeinsamen Zustände mit identischem Folge-Zufallsstrom. Das isoliert den Burn-in-Effekt kausal **nicht vollständig** von Trajektorienunterschieden. P-Werte oder einzelne 95-%-Intervalle der 18 Vergleiche dürfen nicht als familienweit bestätigte Effekte bezeichnet werden.

Coverage bei T≈Tc für Burn=0/100/400/1600: Energie **10/10, 10/10, 10/10, 8/10**, |M| **10/10, 10/10, 10/10, 8/10**. Keine monotone Verbesserung; 8/10 ist keine Widerlegung längeren Burn-ins. Eine stabilere Burn-in-Auswertung benötigt unabhängige Hot-/Cold-Starts und Vergleich einer tatsächlich stationär initialisierten L4-Referenz; für L>4 zusätzliche Multi-Chain- und Fensterdiagnostik.

### B3. Autokorrelation: analytisch kontrollierte AR(1)-Stresstests

Die derzeitige Implementierung summiert positive empirische `ρ(lag)` bis zum **ersten nichtpositiven Lag** oder `lag ≥ 5τ`. Sie meldet kurze (<20) und konstante Ketten als **undefiniert**, was richtig vorsichtig ist. Der analytische stationäre AR(1)-Prozess `X_t = φX_(t-1)+ε_t` besitzt `τ_int=(1+φ)/(2(1−φ))` (Definition `τ=.5+Σ_{k≥1}ρ_k`). Je φ: **8 feste Seeds**, Länge **12000**; reproduzierbarer Quellcode `scripts/autocorr_synthetic_audit.py`.

| φ | Analytisch τ | Median bestehende Heuristik | Median positive Lag-Paare (IPS) | Median Batch-Mittel (Block 500) |
| --- | ---: | ---: | ---: | ---: |
| 0 | 0.5 | 0.506 | 0.501 | 0.591 |
| 0.5 | 1.5 | 1.527 | 1.549 | 1.801 |
| 0.9 | 9.5 | 9.672 | 9.986 | 11.129 |
| 0.98 | 49.5 | 53.472 | 57.892 | 48.656 |
| 0.995 | 199.5 | **171.44** (Spannweite **114.91–318.50**) | **171.44** | **121.28** |

Die lange Korrelationszeit führt zu breiter Unsicherheit und teils Unterschätzung **aller** betrachteten Schätzer; die Alternativen sind selbst keineswegs automatisch konservativ. Insbesondere Block 500 deckt bei φ=0.995 nur wenige Korrelationszeiten ab. Diese stationären Kontrollen testen **nicht** initiale Äquilibrierung. Kurze nahezu konstante Serien, dynamische kritische Verlangsamung und taugliche Fensterwahl bleiben Risiken. Für Phase 1 ist eine explizite Pflicht zum Melden **unbestimmbarer ESS/τ** erforderlich, statt präziser Schein-Fehlerbalken.

### B4. Mehrere Gittergrößen und echte Negativkontrolle

**Neuer explorativer Pilot**: `src/emergence_lab/finite_size.py`, `configs/fss_pilot.json`; `L=8,16,24,32`, T=2.1/2.269185/2.45, **6 unabhängig geseedete Ketten** pro (Modell,T,L), **200 Burn + 600 Mess-Sweeps** (jede fünfte Messung). Je **72 Ising- und 72 J=0-Ketten**, im Ising-Zweig **27,648,000** versuchte Einzelspin-Änderungen; auf geraden L verwendet diese Zusatzimplementierung checkerboard Metropolis. Dieses Verfahren ist gegenüber dem ursprünglichen random-site Metropolis **ein zweiter Sampler**, keine bereits vollständige Kreuzvalidierung.

**Lokale Ausführung:** Python 3.13.5, NumPy 2.3.5, 5.31 s Wall / 5.25 s CPU, ~96 MB MaxRSS; drei lokale Finite-Size-Tests bestanden. **GitHub CI [37996248059](https://github.com/shaden7/emergence-lab/actions/runs/37996248059) erfolgreich**, Checkout **`5d54156e6407a4f61006c28f3cbdef543712cd19`**, Python 3.12.15, NumPy 2.5.3, vollständige Rohdaten [Artefakt **11646539226**](https://github.com/shaden7/emergence-lab/actions/runs/37996248059/artifacts/11646539226). **Alle 144 numerischen Kettendatensätze** des CI-JSON wurden mit der lokalen Ausführung verglichen: **identisch**. Python-/NumPy-Metadaten unterscheiden sich erwartbar. `tests/test_finite_size.py` enthält eine kleine L4-Querkontrolle gegen die exakte endliche Referenz, deterministischen J0-Test und Budget-/Parameter-Wächter. Dies ist eine kleine Rauchkontrolle, noch kein hochpräziser Sampler-Beweis.

**Beobachtete Werte bei dem extern bekannten Tc** (Schätzwert ± Halbbreite des approximativen zwischen-Ketten-t95-%-Intervalls; jeweils 6 Ketten):

| L | Ising |m| | Ising χ_abs | Ising Binder U4 | J=0 |m| | J=0 χ_abs |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 8 | 0.7821 ± 0.0327 | 1.211 ± 0.389 | 0.6140 ± 0.0142 | 0.0988 ± 0.0082 | 0.1526 ± 0.0330 |
| 16 | 0.7113 ± 0.0430 | 3.923 ± 1.572 | 0.6085 ± 0.0268 | 0.0495 ± 0.0021 | 0.1464 ± 0.0115 |
| 24 | 0.6857 ± 0.0411 | 7.903 ± 4.254 | 0.6122 ± 0.0316 | 0.0332 ± 0.0020 | 0.1643 ± 0.0212 |
| 32 | 0.6579 ± 0.0698 | 13.061 ± **11.154** | 0.6034 ± 0.0558 | 0.0253 ± 0.0023 | 0.1532 ± 0.0197 |

Energie pro Spin bei Tc, Ising L=8 → L=32 **−1.5017 → −1.4381**; J=0 identisch **0**. Bei T=2.1 zeigen Ising-Gitter starke Ordnung (|m| um 0.87), bei T=2.45 sinkt |m| von **0.6374 (L8)** auf **0.2486 (L32)**. Die Energie-, |m|-, χ- und Binder-Größen sind **numerisch beobachtet**, nicht durch die Messroutine vorgegeben; beim J=0-Modell wird die Wechselwirkung dagegen bewusst **abgeschaltet** und jeder Spin unabhängig aus der Gleichgewichtsverteilung gezogen (vorgegebene Kontrolle).

**Definitionen:** `χ_abs = N/T [⟨m²⟩−⟨|m|⟩²]` (nicht konventionelle signed-χ); `U4 = 1−⟨m⁴⟩/(3⟨m²⟩²)`; die nichtlinearen Kettenstatistiken werden pro Kette berechnet, danach deren unabhängige Replikatschätzer aggregiert. Endliche Ketten können diese Schätzer verzerren. Das J=0-Modell hat analytisch für großes N `E|m|≈sqrt(2/(πN))∝1/L`, `χ_abs→(1−2/π)/T`, `U4→0`. Das Ising-Auswerteverfahren produziert **nicht** automatisch `L^{7/4}` bei J=0.

**Nur explorative effektive log-log-Steigungen bei T=2.269185**, jeweils 3000 **chain-bootstrap**-Resamples (fester Bootstrap-Seed 20261009, 95-%-Perzentile; **keine** vollständigen Exponenten-Fits):
- Ising |m| gegen L: **−0.1224** [−0.1731, −0.0771]; erwartete asymptotische Steigung −β/ν=−0.125. Ohne L8: **−0.1111** [−0.2328, −0.0019].
- Ising χ_abs gegen L: **+1.7141** [1.2553, 2.0721]; erwartetes asymptotisches γ/ν=+1.75. Ohne L8: **+1.7349** [0.6120, 2.5549].
- J=0 |m|: **−0.9856** [−1.0402, −0.9287]; J=0 χ_abs: **+0.0267** [−0.0998, 0.1529].

Die Übereinstimmung mit Ising-Exponenten ist **ermutigende Kalibrierung**, aber kein belastbares Exponentenergebnis: wenige L, nur sechs Ketten, sehr breite χ-Unsicherheit, vorgegebene Tc-Lage, nicht quantifizierte Mischzeit und Finite-Size-Korrekturen. Ein `ν`-Wert wurde **nicht** gemessen. Ein präzises Binder-Crossing wird **nicht** behauptet. Kritische Exponenten sind in diesem Datensatz nicht im strengen Sinne validiert.

## C. Methodische Fehleranalyse / nichtunabhängige Selbstkritik

1. **Sampler:** Random-site-Metropolis (Hauptpfad) und Checkerboard-Metropolis (Pilot) sind algorithmisch unterschiedlich, teilen aber Energie/Spin-Definitionen und analytische Referenz. Die L4-Holdout-Übereinstimmung prüft einen kontrollierbaren Spezialfall; systematische Fehler bei größeren L bleiben möglich.
2. **Burn-in:** In den dokumentierten kurzen L4-Ketten tritt bei fehlendem Burn-in ein plausibler Startbias auf. Fehlende monotone Coverage-Trends erlauben keine Gleichgewichtsaussage. Paarung über gleiche Seeds ist keine Common-Random-Number-Kopplung identischer späterer Zustände.
3. **Autokorrelation / ESS:** Positive-lag-Abbruch und 5τ-Fenster können lange Tails abschneiden; nahe Tc sind für den neuen FSS-Sampler noch keine tatsächlichen τ/ESS berechnet. Die reported zwischen-Ketten-Intervalle umfassen potentiell gemeinsam auftretenden Startbias **nicht**.
4. **Student-t-CI:** Sechs Ketten bei L8–32 sind wenig; Nichtnormalität der Kettenmittel, Trajektorienkorrelationen, Paarvergleiche und Mehrfachvergleiche sind nicht ausreichend abgesichert. Ein t-Intervall kann systematisch falschen Erwartungswert präzise umschließen.
5. **Finite-size:** Gittergrößen bis L32 reichen für einen qualitativen Kontrollpilot, nicht für zuverlässige unendliche-L-Extrapolationen. Die nominalen Bootstrapintervalle erfassen **keine** Finite-Size-Korrekturen, Burn-in-Systematik oder Tc-Unsicherheit.
6. **Nullkontrolle:** J=0 unabhängige Spins sind ein brauchbarer analytischer Negativfall, aber durch Modellannahmen bewusst triviale Gleichgewichtsdynamik. Er allein beweist nicht, dass eine Pipeline beliebige Scheinkritikalität erkennt.
7. **Provenienz:** Manifest/JSON und feste Seedpläne sind vorhanden; die Original-CLI verwendet `round(T*100)` bei der Seedkonstruktion und kann bei dicht liegenden Temperaturen kollidieren. Der allgemeine CLI-Cap `MAX_EXPERIMENTS` begrenzt nur Kettenzahl, nicht CPU-Arbeit pro Kette. Die neuen Pilot-Wächter setzen zusätzlich ein Flips- und Größenlimit; Actions-Artifakte sind **nicht dauerhaft garantiert**. GitHub-Revisionsprovenienz und die beiden Quell-ZIP-Hashes sind in `docs/RESEARCH_STATE.md` nachzulesen.
8. **Prüfunabhängigkeit:** Dieser Bericht und die Implementierung wurden **nicht** unabhängig peer-reviewed. Eine softwareseitig erfolgreiche CI ist nicht gleichbedeutend mit wissenschaftlicher Akzeptanz.

**Keine** Aussage hier bestätigt, dass Raumzeit aus einem Netzwerk, Feld, Quantenmodell oder etwas anderem entsteht; das zweidimensionale Ising-Gitter besitzt Geometrie bereits per Konstruktion.

## D. Entscheidung, Kriterien und offener Restaufwand

Die acht vom Forschungsauftrag **vor** dieser Auswertung geforderten Abschlussfragen werden nicht zugunsten der Befunde abgeschwächt. Neu unten angegebene **quantitative** Schwellen sind **prospektive Kriterien für künftige Follow-ups**, keine als angeblich vorab deklarierte Auswertung des aktuellen Pilots.

| Anforderung | Stand | Urteil |
| --- | --- | --- |
| 1. Sampler gegen kontrollierbare Fälle | M3 exakte L4-Enumeration; Zusatz-L4-Checkerboard-Rauchkontrolle | **teilweise** |
| 2. Gleichgewicht + Autokorrelation | Burn-in-Bias bei T1.5 ohne Burn-in; AR1-Stress; keine Hot/Cold-/R-hat-Studie bis L32 | **offen** |
| 3. Unsicherheitsabdeckung | M4 Wilsonbreiten 16–24 Prozentpunkte; t-Annahmen ungeprüft für FSS | **offen** |
| 4. Bekannte Ising-Eigenschaften mehrere L | qualitative Abhängigkeiten und vorläufige Steigungen; kein ν, keine kontrollierte asymptotische Fits | **teilweise** |
| 5. Nullmodell diskriminiert | J=0-Energie=0, |m|~1/L, χ_abs annähernd konstant, Binder nahe 0 | **Pilot bestanden** |
| 6. Wesentliche Ergebnisse unabhängig reproduzierbar | CI-ZIPs und Script, 144/144 CI-vs-lokal identisch; Artifakt-Retention endlich, alte Ansätze ungemergt | **teilweise** |
| 7. Kritischer Bericht | vorliegender Bericht auf Reviewbranch | **erstellt, Review offen** |
| 8. Explizite Entscheidung | **NO-GO** | **erfüllt** |

**Prospektive Mindest-Gates vor GO:** (G1) unabhängige PR-Reviews und sequenzielle Integration der gestapelten Arbeiten sowie grüne Main-CI; (G2) L4-Gleichgewichtsziel aus unabhängigen Hot-/Cold-Starts, seed-disjunkter Holdout, numerisch ausgewiesener Biasgrenze; (G3) robuste τ/ESS-Fenstersensitivität und Markierung kurzer Ketten als unzureichend, inklusive AR1 φ≥0.98; (G4) Coverage auf **neuen** Seeds mit genug unabhängigen Batches, sodass pro vorab gewählter primärer Observable eine 95-%-Wilson-Halbbreite <0.05 ist (200 Batches als Planungsansatz, tatsächliche Zahl abhängig von Rate); (G5) L=8..32 oder größere Größen mit längeren Ketten, Hot-/Cold-Checks und Stabilität gegen Änderung von L_min und Fitfenster; (G6) dauerhaft auffindbare Rohartefakte mit revisionsgebundenen Manifests. Zusätzlich muss eine adversarielle Nullkontrolle falsche positive Übergangsmeldungen erkennbar machen. **Nicht** dieselben Seeds zum Regeln-Tuning und Bestätigen verwenden.

Warum **NO-GO** statt CONDITIONAL GO? Die wesentliche Unsicherheitsquelle (möglicher gemeinsam systematischer Nichtgleichgewichts-Bias und unzuverlässige τ/ESS nahe längerer Dynamik) ist für L>4 **nicht hinreichend eingegrenzt**. Außerdem sind zentrale Ergebnisse noch unmerged/unreviewed und die langfristige Artefaktablage nicht gesichert. Ein Conditional GO würde hier mehr Sicherheit suggerieren, als belegt ist. Explorative Phase-1-Protokolle/Literatur können weiter fachlich überprüft werden; **keine Phase-1-Simulation automatisch starten**.

## E. Konkret reproduzierbarer Handoff

```bash
# Repo inklusive gestapelter Ising-Änderungen / eigener Analyse-PR:
python -m pip install -e '.[test]'
pytest -q
python -m emergence_lab.finite_size --config configs/fss_pilot.json --output results/finite_size_pilot.json
python scripts/autocorr_synthetic_audit.py --output results/autocorr_synthetic.json

# Historische Rohdaten-ZIPs aus GitHub Actions:
# 37994539424 -> artifact 11646079121 (M4)
# 37995173975 -> artifact 11647295336 (Burn-in)
python scripts/phase0_artifact_audit.py \
  --m4-zip /path/to/m4.zip --burnin-zip /path/to/burnin.zip \
  --fss-json results/finite_size_pilot.json --output results/phase0_audit.json
```

**Ressourcen:** Finite-Size-Test 144 Ketten mit 27.65 Mio. vorgeschlagenen Ising-Flips, lokal ca. 5.3 s/96 MB; CI mit 5-Minuten-Schrittlimit, Einzelthread-BLAS, kein Lightsail-Deployment. Als unabhängige nächste Untersuchung: Start initialisiert aus exakter L4-Gleichgewichtsverteilung vs. Random-/Hot-/Cold-Start, danach ausgedehntes L16–32 Mixing-/Blocklängen-Protokoll mit unabhängigen Holdout-Seeds. Diese Untersuchungen sind **noch nicht implementiert oder ausgeführt**.

**Phase-1-Ausblick nur als Kandidat:** Nach dem Gate die vorgeschlagene interventionelle Ausbreitungsmessung aus Issue #6 / Draft PR #8 und der repräsentationsneutralen PR #5 gegen diskrete, kontinuierliche, kausale und quantenmechanische Baselines gemeinsam reviewen. Die Wahl des mathematischen Substrats bleibt offen.

## F. Ergänzender kontrollierter Startzustandsversuch (2026-10-09)

Nach der vorläufigen NO-GO-Entscheidung wurde ein weiterer **begrenzter, reproduzierbarer** Test durchgeführt, um den L4-Gleichgewichtseinwand gezielt zu untersuchen. Er **ändert die Entscheidung nicht rückwirkend**.

**Experiment:** `src/emergence_lab/equilibration4.py` / `configs/equilibration4_pilot.json`, Check-in `bc5bf407764f022465ed1c14e4c2366198cb4e32`. Drei Temperaturen (1.5, 2.269185, 3.5), **64 verschiedene Seeds pro Temperatur/Starttyp**, Starttypen (i) zufällig unabhängige Spins, (ii) vollständig geordnete Spins, (iii) aus der **exakten kanonischen L4-Boltzmann-Verteilung** gezogene Spins. Messungen bei Sweep 0/5/20/100/400 mit derselben random-site-Metropolis-Aktualisierung wie im ursprünglichen Sampler. **576 unabhängige Ketten, 2880 Einzel-Snapshot-Datensätze, 3,686,400 versuchte Flips**. Seed-Basis `2027040101` disjunkt von M3/M4; hard-coded Budget-Guard <5 Mio. Vorschläge. Die Boltzmann-Startzustände werden direkt aus den 2^16 exakten Zuständen mit unabhängiger RNG gezogen; damit ist die **theoretische** Stationarität bei korrekter Detailbalance ein kontrollierter Positivfall, aber der Test ersetzt keine unabhängige Analyse der Übergangswahrscheinlichkeiten.

**Tatsächlich ausgeführt:** Lokal Python 3.13.5, NumPy 2.3.5, 3 neu hinzugefügte Tests bestanden, 14.68 s Wall, 14.60 s CPU, 99 MB RSS. [GitHub Actions CI 37996892064](https://github.com/shaden7/emergence-lab/actions/runs/37996892064) **success** auf exakt diesem Commit; [Roh-JSON-Artefakt 11647700495](https://github.com/shaden7/emergence-lab/actions/runs/37996892064/artifacts/11647700495) einschließlich `equilibration4_pilot.json`. **Alle 2880 Roh-Snapshot-Datensätze** aus GitHub CI mit lokalem Lauf **exakt identisch**; 45 aggregierte Summary-Datensätze differieren ausschließlich in Fließkommarundung der unabhängig enumerierten Referenz (ca. 2.4e-14 bei Energie). Unterschiedliche Python/NumPy-Umgebungen sollten daher nur auf Rohdatenexaktheit und auf vorab definierte Zahlentoleranzen, nicht auf vollständige JSON-Textgleichheit geprüft werden.

**Beobachtete mittlere Energie-Abweichung** relativ zur exakten L4-Referenz (Bias ± deskriptive 95-%-Student-t-Halbbreite über 64 voneinander unabhängige Ketten):

| T | Initialisierung | Sweep 0 | Sweep 5 | Sweep 20 | Sweep 100 |
| --- | --- | ---: | ---: | ---: | ---: |
| 1.5 | zufällige Spins | +1.9741 ± 0.0980 | +0.3374 ± 0.1213 | −0.0376 ± 0.0240 | −0.0103 ± 0.0347 |
| 1.5 | exakt stationär | +0.0131 ± 0.0484 | −0.0181 ± 0.0313 | +0.0210 ± 0.0541 | +0.0053 ± 0.0449 |
| 2.269185 | zufällige Spins | +1.5187 ± 0.0905 | +0.1594 ± 0.1482 | −0.0437 ± 0.1270 | +0.0188 ± 0.1301 |
| 2.269185 | exakt stationär | −0.0555 ± 0.1186 | +0.0539 ± 0.1155 | +0.0305 ± 0.1355 | −0.0047 ± 0.1248 |
| 3.5 | zufällige Spins | +0.7840 ± 0.0815 | +0.0418 ± 0.1331 | −0.0832 ± 0.1402 | +0.0340 ± 0.1416 |
| 3.5 | exakt stationär | +0.0261 ± 0.1426 | −0.0090 ± 0.1535 | −0.0676 ± 0.1391 | +0.0183 ± 0.1552 |

**Interpretation:** Die sehr große Anfangsabweichung der uninitialisierten Ketten und deren schneller Rückgang nach wenigen Sweeps zeigen einen Starttransienten, besonders bei niedrigem T; die exakte kanonische Initialisierung liefert einen brauchbaren stationären Vergleich. Bei T=1.5 ist die 20-Sweep-Messung der zufälligen Starts ungewöhnlich stark geordnet (E −1.9883 vs Referenz −1.9506). Dies ist ein **deskriptiver Einzelzeitpunkt**, keine korrigierte globale Hypothesentestentscheidung. Alle **90 Temperatur×Start×Zeit×Observable** deskriptiven t-Intervalle (3×3×5×2) sind abhängig innerhalb derselben Kette; selbst der stationäre Kontrollarm zeigt einzelne scheinbare 95-%-Ausschlüsse (etwa T≈Tc, Sweep400, E-Bias +.1437 ±.1281), was bei vielen Vergleichen **nicht** überraschend ist. Insbesondere bei **geordnetem Sweep 0** ist die empirische Varianz identisch null: das formal ausgewiesene t-Intervall `[-2,-2]` (für E) ist keine vernünftige statistische Präzisionsaussage und darf **nicht** als Gleichgewichtsvergleich verwendet werden.

Dieser Test prüft ausschließlich L4-Ensemblemittelwerte an diskreten Zeitpunkten. Er belegt **keine** ausreichende Durchmischung einzelner Trajektorien, keinen streng oberen Mixing-Time-Bound, keine verlässlichen Autokorrelationszeiten für L16–32 und keine korrekte FSS-Konfidenzintervallabdeckung. Der evidenzbasierte **NO-GO bleibt bestehen**. Nächster entscheidender Kalibrierungsschritt ist eine streng gedeckelte L16/32-Startzustands-/ESS-Konvergenzstudie mit unabhängigen neuen Seeds und stabilisierten Blocklängen; keine Phase-1-Simulation.

## G. Vertiefte Größen-/Start-/Autokorrelations-Diagnostik L16 und L32

Der vorherige L4-Startzustandsversuch kann die kritische Verlangsamung größerer Gitter nicht aufklären. Deshalb wurde zusätzlich eine gezielt begrenzte **L16/L32-Diagnostik** ausgeführt: `src/emergence_lab/mixing_pilot.py`, Konfiguration `configs/mixing_pilot.json`, Branch-Commit `e8ae9eb18ced369489cbb629fcb090f8fac2295e`.

**Messplan:** L=16 und 32, T=2.1, 2.269185, 2.45; je 12 unabhängige Seeds für zufällige und vollständig geordnete Starts. Pro Kette 1800 Checkerboard-Metropolis-Sweeps (ohne verworfenes Burn-in), jede fünfte Messung; **144 Ketten, 165,888,000 versuchte Spinänderungen, 360 Messungen pro Observable und Kette = 103,680 Rohwerte** für E und |m|. Erste und zweite Hälfte (je 180 Messungen) separat auf Drift und τ/ESS untersucht. Dazu Blocklängen-20-Varianzdiagnostik, zwischen-Startgruppen-Resampling (3000 chain-bootstrap-Ziehungen mit festem Seed). Harte Grenze von 300 Mio. Vorschlägen und max. 180 Ketten; Umgebung lokal Python 3.13.5/NumPy 2.3.5, 20.79 s CPU/Wall, ~107 MB RAM.

**Beobachtete reproduzierte Messung:** [GitHub CI 37997377758](https://github.com/shaden7/emergence-lab/actions/runs/37997377758) **success**, vollständige Roh-Zeitreihen [Artefakt **11648100844**](https://github.com/shaden7/emergence-lab/actions/runs/37997377758/artifacts/11648100844), Python 3.12.15/NumPy 2.5.3. **Alle 144 × 2 × 360 = 103,680 numerischen Rohwerte** stimmen exakt mit lokalem Lauf überein. Unterschiedliche NumPy/Python-Versionen bewirken in einigen aggregierten τ/ESS-Ausgaben minimale Rundungsdifferenzen (~1e-14); numerisch nach geprüfter Toleranz äquivalent. Die bloße grüne CI ist kein Proof of Equilibration.

**τ in Einheiten von aufgezeichneten Messintervallen (5 Sweeps je Intervall); jeweils 24 Ketten je L/T und Observable:**

| T | L | Observable | Median τ letzte 180 | Median ESS letzte 180 | min. ESS | Ketten mit ESS <25 |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| 2.1 | 16 | |m| | 0.775 | 116.2 | 52.6 | 0/24 |
| 2.1 | 32 | |m| | 1.185 | 76.0 | 15.9 | 1/24 |
| 2.269185 | 16 | |m| | 1.844 | 48.8 | 20.3 | 2/24 |
| 2.269185 | 32 | |m| | **3.781** | **23.9** | **4.16** | **12/24** |
| 2.269185 | 32 | Energie | **2.216** | **40.6** | **11.78** | **4/24** |
| 2.45 | 32 | |m| | 2.516 | 35.8 | 14.0 | 3/24 |

Eine einzelne Tc/L32-Kette hatte **τ(|m|)=21.61 Messintervalle**, ESS=4.16 in 180 gespeicherten Messwerten; die Batch-Mittel-Methode mit Blöcken à 20 Messungen schätzte dagegen nur τ=7.14. Dies illustriert empirisch das Abschneiden langer Moden, ohne einen nachweislich korrekten τ-Schätzer vorauszusetzen. Ein im Voraus im Experimentcode festgelegter *konservativer Pilotfilter* verlangte zugleich (i) Bootstrap-95-%-Intervall für den Unterschied zufällig minus geordnet vollständig innerhalb ±0.12 (E) bzw. ±0.08 (|m|) und (ii) mindestens 25 effektive Stichproben **in jeder Kette** für jede Variable. **12/12 Mittelwert-Äquivalenzchecks erfüllten (i), aber 5/12 Gruppen scheiterten an (ii)**. Der Gesamtfilter war **False**. Die Entscheidungsschwelle ist ein pragmatischer Qualitätsscreen, **kein mathematisch begründeter universeller ESS-Schwellwert**. Sie wurde im lokalen Quellcode vor dessen Ausführung definiert, aber **nicht vor dem ersten lokalen Ergebnis extern preregistriert**; Resultat deshalb als explorativ zu behandeln.

**Aus den gespeicherten Originaltraces zusätzlich ermittelt:** `scripts/mixing_diagnostics.py`, getestet an synthetischen unabhängigen und absichtlich auseinanderlaufenden Normalreihen. Der **klassische nicht-rangnormalisierte Split-R-hat** bei Tc/L32 beträgt **1.0402 für |m|** und **1.0137 für Energie**, bei T2.1/L32 **1.0357 für |m|**; das sind Warnsignale, **keine** formalen Beweise von Nichtgleichgewicht. Modernes rank-normalisiertes, gefaltetes R-hat gemäß Vehtari et al. wurde **nicht** implementiert. R-hat nahe 1 kann unerkannte Langsammoden übersehen. Die Ergebnisse liefern direkte, stärker diskriminierende Evidenz dafür, dass die Phase-0-Fehlerdiagnostik für L32, insbesondere bei Tc, noch nicht ausreichend kalibriert ist.

**Folge für Finite-Size-Scaling:** Die zuvor gemeldeten scheinbar passenden Exponenten wurden nur aus **120 Messungen pro Kette** und sechs Replikaten gewonnen; die L32-Autokorrelationsproblematik ist dort nicht mit eigenen Zeitreihen untersucht und darf nicht durch die neue ESS-Zahl quantitativ ersetzt werden. Das vorläufige Exponentenergebnis bleibt **explorativ, nicht validiert**. Die NO-GO-Entscheidung wird durch neue Messdaten unterstützt, nicht nachträglich künstlich herbeigeführt.

## H. Audit der fehlersicheren Statistik- und Seed-Infrastruktur

Die Prüfung ergab zwei konkret reproduzierbare, fachlich relevante Fehler, die **nur im isolierten PR #12** behoben sind:

1. **Seed-Kollision und unlimitierte Gesamtarbeit:** Die bestehende `cli.py` erzeugt Seeds über `base + 100000 L + 1000 round(100T) + repetition`. Zwei verschiedene Temperaturen wie **2.269180/2.269190** erzeugen damit denselben Seed, ebenso bestimmte Größen-/Temperaturkombinationen; diese Fälle wären bisher ohne Warnung ausgeführt worden. Neue `plan_seeded_experiments()` validiert den kompletten Seedplan vor der ersten Simulationsdatei und verweigert Duplikate. Sie bewahrt die **historischen** Seeds der L4-Referenz unverändert. Zusätzlich begrenzt `MAX_SPIN_PROPOSALS` standardmäßig auf **100 Millionen** geplante Spinänderungen (zusätzlich zum bisherigen Kettenzähler). Die bestehende Nightly-Konfiguration benötigt ca. 61.44 Mio. und ist innerhalb dieses Limits; kein Lightsail-Deployment.
2. **Degenerierte t-Intervalle:** Wenn alle unabhängigen Kettenmittel exakt gleich waren, erzeugte `independent_chain_interval()` bislang ein scheinbar perfektes Intervall `[mean,mean]`, auch bei offensichtlich nicht gemischten Ketten. Der neue Pfad liefert in diesem Fall **undefinierte SEM- und CI-Felder**. `coverage4.py` klassifiziert derartige undefinierte Intervalle explizit als **Nichtabdeckung** und speichert `interval_defined=false`, statt sie als Treffer zu zählen oder ohne Hinweis abzubrechen. Negative Tests mit absichtlich degenerierten Kettenmittelwerten wurden ergänzt. Historische M4-Experimente und zugehörige Artefakte bleiben unverändert. Solange diese Änderungen nicht gemergt sind, ist die Korrektur **nicht** in `main`.

**CI-Validierung:** [37997530526](https://github.com/shaden7/emergence-lab/actions/runs/37997530526) (Seed-/Budget-Tests), [37997611607](https://github.com/shaden7/emergence-lab/actions/runs/37997611607) (Degenerate-CI-Tests) sowie [37997862553](https://github.com/shaden7/emergence-lab/actions/runs/37997862553) (klassischer Split-R-hat) erfolgreich. Für die numerischen Experimente sind die konfigurierten Seeds in den jeweiligen Configs fest; später wurde `GIT_SHA` als Laufzeit-Umgebungsvariable auch für alle neuen Pilotskripte eingeführt, sodass **neue** Artefakte zusätzlich ihre Checkout-Revision und Python-/NumPy-Version selbst enthalten.

### Primärliteratur und Verfahrensreferenzen

- Lars Onsager (1944), *Crystal Statistics I*, Physical Review 65, 117–149. DOI: https://doi.org/10.1103/PhysRev.65.117 — exakte freie Energie und kritisches Verhalten des 2D-Nullfeld-Ising-Modells.
- C. N. Yang (1952), *The Spontaneous Magnetization of a Two-Dimensional Ising Model*, Physical Review 85, 808. DOI: https://doi.org/10.1103/PhysRev.85.808 — spontane Magnetisierung.
- Charles J. Geyer (1992), *Practical Markov Chain Monte Carlo*, Statistical Science 7, 473–483. DOI: https://doi.org/10.1214/ss/1177011137 — Zeitreihen- und MC-Varianzmethoden (die hier implementierte Lag-Paar-Variante ist nur „Geyer-like“, **nicht** die vollständige etablierte IPS/IMS-Methode).
- Aki Vehtari et al. (2021), *Rank-Normalization, Folding, and Localization*, Bayesian Analysis 16, 667–718. DOI: https://doi.org/10.1214/20-BA1221 — Grenzen klassischer R-hat-Diagnostik und bessere Alternative. **Hier nicht implementiert.**
