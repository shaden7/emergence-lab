# Emergence Lab — Literaturbericht: Dimension, Kausalität und Ausbreitungsgrenzen

**Stand:** 9. Oktober 2026 · **Auftrag:** [Issue #6](https://github.com/shaden7/emergence-lab/issues/6) · **Typ:** kritischer Literatur- und Forschungsentscheidungsbericht, **keine** neue experimentelle Evidenz · **Status:** zur wissenschaftlichen Prüfung vorgeschlagen

> **Kurzurteil:** Weder Netzwerke noch Kontinuumsfelder, Causal Sets oder Quanteninformation besitzen heute eine etablierte Herleitung *gemeinsam* von beobachteten Raumdimensionen, relativistischer Kausalität und der universellen Lichtgeschwindigkeit aus voraussetzungslosen mikroskopischen Regeln. Sehr gut verstanden sind einzelne Teilprobleme – zum Teil in strengen Sätzen. Die größte Chance für ein kleines Team liegt nicht in der Suche nach einer schönen „3D-Welt“, sondern in **operationsdefinierten, gegen konkurrierende Repräsentationen getesteten Negativ- und Unterscheidungsresultaten**.

## 0. Quellenlage, Vorgehen und Geltungsbereich

Systematische, **narrative** Recherche anhand von Originalarbeiten, mathematischen Sätzen, fachlichen Reviews und gezielt gesuchten Veröffentlichungen bis einschließlich **09.10.2026**. Thematische Suchfelder: causal sets/order reconstruction, dimensions/spectral diffusion, Lieb–Robinson/long-range, hyperbolic PDE/analogue geometry, quantum walks/QCA, CDT, holography/tensor networks, operational theories und Lorentz constraints. Erstautoren-, Verlags- und DOI-Metadaten wurden soweit möglich mit Original-Publikationsseiten abgeglichen. Diese Arbeit ist **keine bibliometrisch erschöpfende systematische Review** mit protokollierter Datenbank-Abfrage, Volltextscreening jeder Publikation und unabhängiger Zweitbegutachtung. Vorläufige bzw. nicht peer-reviewte Arbeiten sind ausdrücklich bezeichnet. Zahlenvorgaben bei Pilotexperimenten sind **Präregistrierungs-Vorschläge**, keine Messwerte.

Projektkontext auf main: [AGENTS.md](../AGENTS.md), [OVERVIEW.md](OVERVIEW.md), [RESEARCH_STATE.md](RESEARCH_STATE.md), [RESEARCH_DIRECTOR.md](RESEARCH_DIRECTOR.md), [README](../README.md). Parallel aktiv: [Ising-Kalibrierung (PR #1, #3)](https://github.com/shaden7/emergence-lab/pulls), [Repräsentationsneutralität (PR #5)](https://github.com/shaden7/emergence-lab/pull/5). [Issue #4](https://github.com/shaden7/emergence-lab/issues/4) betrifft nur **Dimensionsschätzer-Kalibrierung**, nicht einen Nachweis emergenten Raums. **Kein Code, keine Serverjobs, keine Infrastrukturänderungen** sind Teil dieses Auftrags.

**Evidenzetiketten im Bericht:** **[S]** mathematischer Satz für benannte Annahmen; **[N]** Simulation/numerischer Befund; **[E]** Bezug auf experimentelle Daten; **[H]** falsifizierbare, noch nicht bestätigte Hypothese; **[I]** Interpretation/Analogie; **[D]** durch Definition oder Konstruktion vorgegeben. „Entsteht“ im Titel einer Publikation wird hier nicht automatisch als „ohne Geometrieannahme hergeleitet“ gewertet.

---

# 1. Executive Decision Memo

### Entscheidung

**Keine ontologische Festlegung.** Das Lab sollte zunächst ein **repräsentationsneutrales Mess- und Widerlegungsprogramm** aufbauen. Ein Graph ist ein möglicher *Datentyp* für Beziehungen, nicht der bewiesene Stoff des Universums. Die geforderten Eigenschaften sind getrennt zu prüfen:

1. **Dimension/Geometrie:** robuste Skalenbereiche für mindestens zwei voneinander unabhängige Operationalisierungen.
2. **Kausale Beeinflussbarkeit:** Antwort auf gezielte Intervention statt nur gleichzeitiger Korrelation.
3. **Ausbreitungsgrenze:** unterscheiden zwischen *striktem* Einflussverbot, einem exponentiell abgeschwächten Einfluss und bloß endlicher Gruppen-/Frontgeschwindigkeit.
4. **Relativität:** Isotropie oder eine lineare Front genügen nicht; zu prüfen sind effektive Boost-Symmetrie, universelle Grenzgeschwindigkeit unterschiedlicher Anregungen, keine bevorzugte Uhr im zugänglichen Regime, skalierungsstabiler Kontinuums-Limes.
5. **Echter Erkenntnisgewinn:** Kontrollmodelle müssen aussortiert werden können, auch wenn ihre Bildausgabe „wie Raumzeit“ aussieht.

**Zentrale Einsichten aus Primärarbeiten:**

- **[S]** Endlich-reichweitige/quasilokale Gitter-Hamiltonoperatoren erlauben Lieb–Robinson-Schranken: außerhalb einer effektiven Front werden Kommutatoren stark klein, sind aber allgemein **nicht null**. Die inverse Richtung ist für eine spezifizierte Klasse von k-Körper-Wechselwirkungen ebenfalls bewiesen. Das ist ein wichtiger Hinweis auf **welche Annahme die Front bereits enthält**, nicht die Erfindung fundamentaler Geschwindigkeit. [1–3, 15]
- **[S]** In hinreichend regulären Lorentz-Mannigfaltigkeiten kodiert die Kausalordnung die konforme Geometrie; **Volumeninformation** ist zusätzlich erforderlich, um den lokalen Skalenfaktor festzulegen. Aus einem beliebigen Poset folgt noch keine Mannigfaltigkeit. [5–7]
- **[N]** CDT zeigt in bestimmten Phasen de-Sitter-ähnliche makroskopische Profile und skalenabhängige Spektraldimension. Raumzeitdimension, Lorentzsche Simplex-Bausteine und eine kausale Folierung sind allerdings Bestandteil der Konstruktion. Neuere Arbeit zeigt zudem, dass Dualgraph- und Kontinuums-Laplace-Spektren auseinanderfallen können. [10–13]
- **[S/N]** Quantum-Cellular-Automata liefern strikte endliche Reichweite pro Zeitschritt **per Lokalitätsaxiom**; Dirac-Dynamik kann im langwelligen Limes folgen, während Lorentzkovarianz bei hohen Frequenzen verletzt wird. [16–17]
- **[I/S unter Axiomen]** Tensor-Netzwerke, AdS/CFT und Quantenfehlerkorrektur erklären interessante Zusammenhänge von Verschränkung und räumlicher Rekonstruktion **in ausgewählten Theorien oder Codes**. Sie beweisen nicht, dass gewöhnliche kosmologische Raumzeit allein aus generischer Verschränkung entsteht. [20–24]

### Priorisierung

| Priorität | Schritt | Erkenntnisgewinn | Rechenbedarf | Freigabebedingung |
|---|---|---|---|---|
| **P0** | Ising-Validierung auf eigenem Pfad abschließen; Literaturbericht prüfen und Hypothesen registrieren | schützt Messmethodik vor Fehlalarmen | **0 CPU-Jobs** | bestehende PRs fachlich/CI begutachtet |
| **P1** | **Pilot A:** gleiche Intervention, vier Dynamikklassen: PDE-Welle, Wärme, diskretlokale Updates, Quanten-Gitter-Walk | trennt strikte Kausalität von „Lichtkegel“-Optik | klein, lokal möglich | vorab festgelegte Definitionen / Exakttests |
| **P2** | **Pilot B:** Ordnungsbasierte Dimension auf Causal-Sets mit adversariellen Poset-Nullmodellen | zeigt Grenzen geometrischer Rekonstruktion | klein–mittel | Pilot-A-Metriken eingefroren |
| **P3** | **Pilot C:** Repräsentations-/Skalen-Stresstest an Graph, Fraktal und Kontinuumsdiskretisierung | prüft Invarianz und Modell-Artefakte | klein–mittel | Ising und Issue #4 sauber getrennt |

**Nicht jetzt:** allgemeine dynamische Graph-Rewrite-Theorie, vollständige Quantenfeld-/CDT-Simulation, Tensor-Netzwerk-Schwergewichte, offene Suche über Millionen Regeln. Sie bieten für 2 vCPU / 4 GB und ungeklärte Identifizierbarkeit niedrigen Informationsgewinn.

**Entscheidungsgrundsatz:** Eine neue Modellfamilie bekommt erst zusätzliche Ressourcen, wenn eine Nullhypothese verworfen, ein notwendiger Annahmenkern eingegrenzt oder ein invariant messbares Makro-Observable **über mindestens zwei unterschiedlich kodierte Beschreibungen** stabil demonstriert wurde. Negative Resultate sind vollwertige Ergebnisse.

---

# 2. Begriffliche und mathematische Grundlagen

## 2.1 Was „Dimension“ überhaupt bedeutet

**Topologische Dimension** ist eine Eigenschaft eines topologischen Raums (z. B. der üblichen Ebene: 2); ein endliches, bloßes Beziehungsobjekt hat ohne Topologie keine festgelegte topologische Raumdimension.

**Wachstums-/metrische Dimension:** Für eine Metrik $d$ und Ball $B_x(r)$ gilt bei geeigneten homogenen Skalen $\lvert B_x(r)\rvert\propto r^{d_V}$, also

$$d_V(r)=\frac{\mathrm d\log \lvert B_x(r)\rvert}{\mathrm d\log r}.$$

Bei abzählbaren Graphen nutzt man häufig kürzeste Weglänge und Knotenzahl. Dies ist nicht ohne weiteres die *Hausdorffdimension* im strengen maßtheoretischen Sinn; beide stimmen nur in geeigneten regulären Räumen/Skalen überein. Ein endlicher Ring sättigt, ein regulärer Baum wächst zunächst exponentiell – ein zwanghaftes Potenzgesetz-Fit kann Unsinn liefern.

**Spektraldimension:** Für einen wohldefinierten Diffusionsgenerator und die mittlere Rückkehrwahrscheinlichkeit $P(\sigma)$,

$$d_s(\sigma)=-2\,\frac{\mathrm d\log P(\sigma)}{\mathrm d\log \sigma}.$$

Auf euklidischem $\mathbb R^d$ ergibt die Wärmeleitung $P(\sigma)\propto\sigma^{-d/2}$. **Achtung:** $d_s$ hängt vom Diffusionsoperator, dessen Normalisierung, Randbedingungen, Laufzeitfenster und Diskretisierung ab. Ein wichtiger Gegenbeleg gegen „eine universelle Zahl“ ist das Sierpiński-Dreieck mit $d_H=\log 3/\log 2\approx1{,}585$ und $d_s=2\log 3/\log5\approx1{,}365$ für die kanonische Diffusion. [12, 30]

**Ordnungsdimension / Causal-Set-Schätzer:** Sie misst etwas anderes. Für $N$ Ereignisse in einem Alexandrov-Intervall und $R$ vergleichbare ungeordnete Paare ist $r=2R/[N(N-1)]$. Bei dichter Poisson-Streuung in ein flaches Lorentz-Intervall von **Raumzeitdimension $D$** gilt asymptotisch

$$r_D=\frac{\Gamma(D+1)\Gamma(D/2)}{2\,\Gamma(3D/2)}.$$

Daraus folgt $r_2=1/2,\ r_3=8/35\approx0{,}22857,\ r_4=1/10$. Die Inversion ist der Myrheim–Meyer-Schätzer. **Nicht verwechseln:** $D$ schließt die zeitartige Dimension ein (in 3+1 also $D=4$). Krümmung, endliche Intervalle, nicht-manifoldartige Ordnungen und Wahl der Stichprobe können die Deutung zerstören. [6, 8–9]

**Finanzielle/methodische Konsequenz:** Drei Schätzer mit „ungefähr 3“ sind kein unabhängiger Beweis, wenn alle dieselbe eingebaute Gittergeometrie ablesen. Man braucht blind getestete, operator-unabhängige und größenstabile Signaturen.

## 2.2 Operationale Lokalität, Distanz, Uhr, Kausalität

Eine **Korrelation** $\mathrm{Cov}(A_x(t),B_y(0))\neq0$ ist noch kein kausaler Signalkanal: gemeinsame Vorgeschichte und Verschränkung können sie erzeugen. Eine *kontrollierte Intervention* verändert zu Zeit $0$ nur die lokale Präparation oder ein lokales Gate $X$ und vergleicht die Verteilung späterer Messwerte $O_y$:

$$\Delta_{X\to O_y}(t)=\mathbb E[O_y(t)\mid\operatorname{do}(X=\epsilon)]-\mathbb E[O_y(t)\mid\operatorname{do}(X=0)].$$

Die Schreibweise ist operational; in einem Modell muss exakt festgelegt werden, was „lokal“, „do“ und „Messung“ heißen. Im Quantenfall kann man z. B. die Norm eines Heisenberg-Kommutators $\|[A_x(t),B_y]\|$ als **zustandsunabhängige** Schranke für Änderungen infolge lokaler Operationen verwenden (mit Normierungsannahmen). Unabhängige Präparationen statt bloßer Datensätze und exakte Kontrollzweige vermeiden Scheinkausalität.

Eine **Uhr** ist entweder das primitive Update-$t$ [D] oder ein aus periodischen/irreversiblen Prozessen rekonstruierter Zeitparameter [H]. Entfernung kann ebenfalls vorgegeben (Graphabstand, Koordinate) oder aus Reaktionszeiten/vergleichbaren Intervallen geschätzt sein. **Zirkularitätsgefahr:** Definiert man Abstand ausschließlich als $v\cdot$ Reaktionszeit, lässt sich ein konstantes $v$ nicht anschließend als Entdeckung feiern.

## 2.3 Vier unterschiedliche Aussagen über „maximale Geschwindigkeit“

**(i) Strikte Front:** $\Delta(r,t)=0$ für $r>ct$ (beziehungsweise genauer: außerhalb des Definitionsbereichs), *ohne* Messschwellenwert. Klassische hyperbolische Wellen-PDE erfüllen dies unter üblichen Voraussetzungen; endliche lokale diskrete Zeitschritte ebenfalls. Bei beiden steckt der relevante Lokalitätsmechanismus bereits in Differentialoperator/Stenzel bzw. Update-Regel. [4, 16, 26]

**(ii) Effektiver Lieb–Robinson-Kegel:** Für lokale Observablen und endliche/quasilokale Kopplung gilt schematisch

$$\|[A_x(t),B_y]\|\le C\,\|A\|\,\|B\|\,\exp[-\mu\,(d(x,y)-v_{\mathrm{LR}}\lvert t\rvert)]$$

(mögliche $C$-Abhängigkeit von Trägermengen und Modell). **Außerhalb** ist die Wirkung im Allgemeinen klein, nicht exakt null. Für zeitkontinuierliche, aber gitterlokale Quantenentwicklung sind beliebig weite, extrem schwache Tails typisch. [1–3]

**(iii) Gruppen- und Phasengeschwindigkeit:** $v_g(k)=\partial_k\omega(k)$ beschreibt Wellenpakete in ausgewählten Regimen, nicht zwingend strikt maximal mögliche Signale oder lokale Messbeeinflussung.

**(iv) Relativistische Mikrokausalität:** Lokal kommutierende Observablen bei **raumartig** getrennten Ereignissen, bezogen auf eine Lorentzgeometrie; hier ist der Lichtkegel nicht bloß ein Falloff-Fit. Diese Aussage setzt in gewöhnlicher lokaler Quantenfeldtheorie die Raumzeitstruktur in der Theorieformulierung bereits voraus. Eine bevorzugte Synchronisationsuhr eines Gitters wäre für echte Lorentzinvarianz erklärungsbedürftig.

**Langreichweitiger Gegenfall:** Bei Kopplungen $\sim r^{-\alpha}$ kann ein linearer informationsbezogener Kegel je nach $\alpha$, Dimension, Observablenklasse und Transferaufgabe bestehen oder scheitern. Exakte Schwellen für bestimmte Klassen wurden bewiesen; es gibt **nicht die eine** „Informationsgeschwindigkeit“ unabhängig von der Aufgabe. [14–15]

## 2.4 Wann ist etwas „emergent“?

Eine Eigenschaft wird **nicht** als ontologisch emergent gewertet, wenn sie schlicht gesetzt wurde. Wir unterscheiden:

- **Kinematische Rekonstruktion:** aus bereits vorgegebener kausaler/geometrischer oder topologischer Information wird ein anderes Maß gewonnen.
- **Dynamischer Grenzwert:** aus festgelegter Mikrodynamik erscheint ein robustes neues effektives Gesetz im Skalengrenzwert.
- **Axiomen-Minimierung:** man beweist, welche Annahmen hinreichen bzw. unverzichtbar sind – relativ zu einer sauber begrenzten Modellklasse.
- **Physikalische Identifikation:** überprüfbare, möglichst neue Vorhersagen stimmen mit unabhängigen Beobachtungen überein.

Das Lab sollte **(2) und (3)** verfolgen, **(1)** methodisch absichern und **(4)** langfristig als gesonderte Hürde behandeln.

---

# 3. Evidenzmatrix der Forschungsfamilien

Legende: **S** Satz, **N** numerisch, **E** Messbezug, **H** spekulativ, **D** konstruktiv eingebaut. „CPU“ ist eine qualitative Pilot-Eignung, keine Laufzeitmessung.

| Familie | Mikroskopisches Objekt, eingebaute Voraussetzungen | Erreichte Makroresultate / Evidenz | Schwere Einschränkung und Falsifikation | CPU-Pilot |
|---|---|---|---|---|
| **Graphen/Hypergraph-Rewrites, Graphity** | Knoten, (Hyper-)Kanten, Rewrite-Regeln, meist Takt und Grad-/Motiv-Energie [D] | Phasen mit geordneter/niedrigdimensionaler Topologie [N]; Graphity-Modelle formal [18–19] | Zielmotive/Knoten-Grad können Geometrie indirekt *erzwingen*; dynamische Stabilität und 3+1 relativistische Grenze offen; Shortcut-Nullmodelle | **mittel**, kleine $N$ |
| **Reguläre/zufällige geometrische Graphen, CA** | Nachbarschaft und häufig Dimension + Update-Takt [D] | exakte endliche Hop-Reichweite bei lokalen synchronen Updates [S]; Referenzdimensionen [D] | tautologische Kegel/Dimension; Graph-„Zeit“ ist nicht relativistische Eigenzeit | **sehr gut**, nur Kontrollen |
| **Quanten-Walks, QCA** | lokale Hilbert-Räume, Unitarität, Homogenität, (diskrete) Isotropie, Update [D] | Dirac-Limes für bestimmte Automata [S asymptotisch]; strikte QCA-Reichweite [S per Axiom] [16–17] | UV-Lorentzverletzungen, Fermion-Verdopplung für einschlägige lokale Gitterfermion-Ansätze; dimensionale Symmetrie vorausgesetzt [17, 27] | **gut** für 1 Teilchen |
| **Causal Sets** | lokal endliche **partielle Kausalordnung**; oft Poisson-Sprinkling in vorgegebene Lorentz-Mannigfaltigkeit [D] | Ordnung+Volumen rekonstruieren Geometrie unter Voraussetzungen [S]; Dimension, Krümmungsoperatoren [S/N] [5–9] | generische Posets nicht manifoldartig; Dynamik/realistischer Kontinuums-Limes offen; Lorentzinvarianz verhindert lokal-endliche äquivariante Graphnachbarschaft [8, 28] | **gut** bis $N\sim10^3$ |
| **Lokale Quanten-Hamiltonoperatoren / LR** | feste Interaktionslokalität auf metrischem Träger, Normbeschränkungen [D] | exponentielle Einflussgrenzen [S]; inverse Lokalitätskriterien für k-Body-Klassen [S] [1–3] | weder striktes Null außerhalb noch Vorhersage einer bevorzugungsfreien 3D-Metrik; langreichweitige Gegenfälle [14–15] | **gut** kleine freie Systeme |
| **Kontinuums-PDE / klassische Felder** | Raumkoordinaten, PDE-Typ, Zeitskala; Wellengeschwindigkeit aus Koeffizienten [D] | exakte Domäne der Abhängigkeit für hyperbolische Gleichungen [S]; effektive akustische Metriken [S unter Hydrodynamikannahmen / E in Analogsystemen] [4, 26] | fundamentale Geometrie/Lokalität nicht abgeleitet; dissipative Wärmeleitung hat instantane Tails | **sehr gut** |
| **CDT / dynamische Triangulation** | vorgegebene Simplex-Dimension, Kausalstruktur, Folierung, Kantenlängen/Regge-Aktion [D] | de-Sitter-artiger Volumenverlauf, Dimensionsfluss [N] [10–13] | UV-Fixpunkt und Beobachtungsbezug offen/umstritten; Dualgraph-Operator liefert teils andere Spektraldimension | **schlecht** für eigene 4D-Reproduktion |
| **Tensor-Netzwerk/MERA** | Tensorfaktorisierung, Bond-Dimension, vorgegebenes Verbindungs-/Skalennetz [D] | Kritikalität/RG, geometrische Kodierungen [S/N] [20–22] | Hilbert-Raum-Partition und Geometrie des Netzwerks sind gewählt; nicht eindeutig rekonstruierbare Geometrie; Bond-Dimension-Fehler | **mittel**, nur kleine Codes |
| **Holographie/AdS-CFT & QEC** | spezifizierte CFT, AdS-Randbedingungen, großer-$N$/semiklassische Regime [D] | Ryu–Takayanagi, Bulk-Rekonstruktion/QEC in definierten Modellen [theoretische Ableitungen, teils bedingt] [22–24] | kein allgemeiner Beweis für unser Universum; nicht automatisch de-Sitter, kausaler Mikrokegel oder beliebige Materie | **schlecht** für eigenen Test |
| **Operationale/GPT-/Prozesstheorien** | Vorbereitungen, Transformationen, Komposition, Wahrscheinlichkeiten; spezifische Rekonstruktionsaxiome [D] | Quantentheorie aus Axiomensets [S unter Axiomen]; Prozessmatrizen ohne globale feste Kausalordnung [S formal] [25, 29, 31] | aus Wahrscheinlichkeitsstruktur folgt weder effektive $d=3$ noch allgemeine GR-Dynamik; starke Axiome können gewünschtes Resultat enthalten | **gut** für Mini-Gegenbeispiele |

**Nicht-exklusiv:** Ein Quanten-Walk läuft auf einem Graphen; ein CDT-Dualgraph kodiert eine Mannigfaltigkeits-Triangulation; MERA kodiert Quanten-Zustände; Causal-Set-Ordnung lässt sich als gerichteter Graph speichern. Die *Computerrepräsentation* ist nicht die physikalische *Ontologie*. Gleichwertige Vorhersagen erzeugen Unterbestimmtheit: einen Träger allein anhand $d_s$ oder einer Front zu identifizieren ist grundsätzlich unmöglich.

---

# 4. Was bereits geklärt ist – und was nicht

## 4.1 Endliche Ausbreitung ist häufig eine Konsequenz vorausgesetzter Lokalität

**[S]** Lieb & Robinson (1972) zeigen unter Lokalitäts- und Normannahmen einen effektiven linearen Kegel. Nachtergaele & Sims erweitern die Theorie; Wilming & Werner (2022) liefern innerhalb spezifizierter k-Körper-Klassen eine **Umkehrrichtung**: geeignete exponentielle LR-Schranken implizieren exponentiell lokalisierte Wechselwirkungen. [1–3]

**Methodische Folgerung:** Findet ein Modell einen LR-Kegel, ist zu fragen, ob „lokal“ im Hamiltonoperator, in der Graphwahl oder der Pfadsumme schon steckt. Mathematisch ist ein inverses Strukturtheorem interessant, physikalisch ist es noch keine Erklärung von Raum und Zeit.

Für lange Reichweiten gelten differenzierte Sätze: Kuwahara & Saito (2020) liefern lineare Grenzen für $\alpha>2D+1$ in behandelten Klassen; Tran et al. (2020, 2021) unterscheiden Aufgaben/Normen und präzisieren Schranken, das PRX-Paper besitzt ein **Erratum von 2023**. Keine universelle Gleichsetzung von Frontgeschwindigkeit, Signalverbot und Lichtgeschwindigkeit. [14–15, 32]

## 4.2 Ordnung ist mächtig – aber nicht voraussetzungslos

**[S]** Malament (1977) beweist, dass kausale Information unter Kausalitäts-/Regularitätsbedingungen weitreichende topologische und konforme Struktur bestimmt. Fügt man einen Volumenmaßstab hinzu, kann man innerhalb der Klasse geeigneter Lorentz-Mannigfaltigkeiten den verbleibenden konformen Faktor fixieren. Diese Aussage wählt keine Raumzeit aus den beliebigen partiellen Ordnungen aus. [5–6]

**[S]** Bombelli, Henson & Sorkin zeigen für Poisson-Sprinklings in Minkowski-Raumzeit, dass keine messbare Lorentz-äquivariante Zuordnung einer endlichen Anzahl lokaler Nachbarn möglich ist. Das ist ein *Gegenargument* gegen eine naive Kombination „streng Lorentz-invariant + lokal endlich valenter zufälliger Raumgraph“, kein allgemeiner Ausschluss diskreter Physik. [28]

**[S]** Kleitman–Rothschild-Zählresultate: generische endliche partielle Ordnungen sind asymptotisch von nicht-manifoldartigen Drei-Schichten-Strukturen dominiert. Neuere Wirkungs-/Pfadintegral-Ansätze können bestimmte unphysikalische Klassen stark unterdrücken; die Vollständigkeit dieser Selektion ist **nicht** als bewiesen anzusehen. [8, 33–34]

**[S/N]** Benincasa–Dowker-Operatoren ermöglichen innerhalb geeigneter Kontinuumsapproximationen die Rekonstruktion von d’Alembert-Operator/Krümmung – bemerkenswert, aber der Ansatz setzt vorgegebene Lorentz-Manifoldähnlichkeit bzw. Glattheits-/Skalierungsbedingungen für die Konvergenzaussage voraus. [9]

## 4.3 Dimensionsfluss ist interessant, aber messinstrument-abhängig

**[N]** Ambjørn, Jurkiewicz & Loll (2005) berichten $d_s\simeq4$ auf großen und $d_s\simeq2$ auf kleinen Skalen für die betrachtete CDT-Phase. **Weder** ist daraus allein ein Beweis für eine vierdimensionale Wirklichkeit **noch** die universelle UV-Dimension 2 aller Quantengravitationstheorien abzuleiten. [10]

**[N, methodischer Gegentest]** Caceffo & Clemente (2023) finden, dass die Dualgraph-Spektren und Spektraldimensionen in CDT außerhalb geeigneter 2D-Sonderfälle nicht generell mit einem Finite-Elemente-Laplace–Beltrami-Operator übereinstimmen. Das ist ein konkreter Grund, nicht bloß eine Graph-Rückkehrwahrscheinlichkeit als „Messung des Raumes“ zu akzeptieren. [12]

**Forschungsstand 2026:** Ambjørn & Loll (April 2026, **Preprint**) stellen den CDT-Fortschritt und Hinweise auf einen UV-Fixpunkt positiv dar. Eine frühere peer-reviewte Arbeit derselben Forschungsrichtung (Ambjørn et al. 2020) erklärt ausdrücklich, dass damals geprüfte invariante Volumenkorrelatoren keinen UV-Fixpunkt nachwiesen. Daher sollte der genaue numerische Daten-/Observablenstand als **offen und definitionsabhängig** gelten, nicht als vollständig gelöst. [11, 13]

## 4.4 Emergent effektiv ≠ volle Lorentzinvarianz

**[S unter Modellannahmen]** Spezielle QCA mit Homogenität, Isotropie, Unitarität und Lokalität liefern im Niederenergie-/Klein-$k$-Limes die Dirac-Gleichung; die originale Arbeit berichtet selbst UV-Abweichungen von der Lorentzkovarianz. [17] Nielsen & Ninomiya (1981) beschränken unter ihren Voraussetzungen chirale Gitterfermionen; dies ist **kein** Theorem, dass alle diskreten Welten unmöglich wären. [27]

**[S unter hydrodynamischen Voraussetzungen / E für Analogsysteme]** Akustische Störungen in Medien können einer effektiven gekrümmten Lorentzmetrik folgen. Dies ist ein wichtiges **Kontinuums-Gegenbeispiel** zur These, ausschließlich Netzwerke könnten effektive Raumzeit generieren. Die zugrunde liegende Laborzeit, das Medium und sein Dispersion-/UV-Regime bleiben bestehen. Die aktualisierte Groß-Review von Barceló, Liberati & Visser (30.06.2026) ist dafür die aktuelle Referenz. [4]

**[E, modellgebundene Grenze]** LHAASO-Gamma-Ray-Burst-Daten schränken bestimmte energieabhängige Photonengeschwindigkeiten und damit spezielle Lorentzverletzungsmodelle ein. Dies falsifiziert weder sämtliche Quantengravitationsmodelle noch beweist es exakte Lorentzinvarianz auf allen Skalen. Eine im Lab gemessene energieabhängige Ausbreitung muss bei späteren physikalischen Ansprüchen daran gemessen werden. [35]

## 4.5 Verschränkung hilft, ersetzt aber die Dynamik nicht

**[S/N/Theorie]** Vidal/MERA zeigt ein vielschichtiges Renormierungsbild; Swingle ordnet der Schichtstruktur eine geometrische Interpretation zu. Die gewählte Skalenarchitektur darf nicht mit abgeleiteter physischer Zusatzdimension verwechselt werden. [20–21]

**[Theoretische Evidenz unter AdS/CFT-Annahmen]** Ryu–Takayanagi verknüpft Entropie mit Flächen im holographischen Dual; Almheiri–Dong–Harlow präzisieren Bulk-Rekonstruktion über Quantenfehlerkorrektur. Die Mathematik/physikalische Motivation ist stark, eine universelle Ableitung unserer 3+1-Dimensionalität oder Signallokalität aus reiner Entropie ist das nicht. [22–24]

**[S unter Axiomen]** Operational-probabilistische Rekonstruktionen der Quantenmechanik (Chiribella–D’Ariano–Perinotti; Masanes–Müller) zeigen, dass möglicherweise **Axiome über Operationen/Komposition** fruchtbarer sind als voreilig ausgewählte „Raumpixel“. Prozessmatrizen (Oreshkov–Costa–Brukner) zeigen, dass lokale Quantenoperationen formal auch ohne *vorgegebene globale* Kausalordnung beschrieben werden können. **Aber:** Operationalismus ist keine Herleitung von Raumdimension, und das Wort „Kausalität“ in GPT-Axiomen bedeutet nicht dasselbe wie eine relativistische Lichtkegelstruktur. [25, 29, 31]

---

# 5. Forschungslücken: präzise und für uns relevante Fragen

**Lücke L1 – gemeinsame, nicht-zirkuläre Rekonstruktion:** Welche minimale, in mehreren Theoriesprachen formulierbare Eigenschaft ermöglicht **zugleich** eine stabile Dimension $d_V/d_s$ und einen kausalen Frontbegriff, ohne den gleichen Abstand für beide einzusetzen? Offene Forschungsfrage. In vielen Beispielen werden lokale Kopplung, Metrik oder Ordnung bereits festgelegt.

**Lücke L2 – Identifizierbarkeit:** Wie groß ist die Klasse nichtäquivalenter Mikromodelle, die denselben makroskopischen $\{d_V,d_s,\Delta(r,t)\}$-Datensatz liefern? Kann ein zweites Observable (etwa Banddispersion, Fluktuationsstatistik, Deformationsempfindlichkeit) sie unterscheiden? **Pilot-fähig.**

**Lücke L3 – Operator- und Repräsentationsabhängigkeit:** Ist die geschätzte Dimension stabil gegenüber Wahl von Diffusionsgenerator, räumlicher/coarse-graining Skala und Kontinuumsapproximation? Motiviert direkt durch Caceffo–Clemente. **Pilot-fähig.**

**Lücke L4 – strikte vs. approximative Kausalität:** Welche messbaren Folgen hat der Unterschied zwischen $\Delta=0$ und $\lvert\Delta\rvert\ll1$ für endliche, verrauschte Beobachtungsfenster? Ein Fit ohne bekannte Nachweisgrenze verwechselt beide. **Pilot-fähig.**

**Lücke L5 – emergente Lorentzstruktur:** Wie erhält man Lorentzsymmetrie und universelle, artsübergreifende maximale Geschwindigkeit ohne ein verstecktes Takt-/Gitterbezugssystem? Dies erfordert langfristig Spezialphysik, sorgfältige Grenzwerte, viel mehr als einen kleinen CPU-Demonstrator. **Nicht kurzfristig lösbar.**

**Lücke L6 – Auswahl physikalischer Dynamik:** In Causal Sets und konstruierten Netzwerken existieren enorme Mengen unphysikalischer Strukturen. Mechanismen, die manifoldartige, stabile und dynamisch korrekte Phasen *ohne Zielkodierung* auswählen, sind ein hochrangiges, aber schwieriges Problem. Kleinere Nullmodelle helfen, unhaltbare Einfach-Hypothesen auszusortieren.

**Mögliche neue Mathematik:** Die Literatur zeigt, dass unterschiedliche formale Objekte dieselbe Physik kodieren können. Erfolgversprechende Forschungsrichtung **[H]**: operationalen Kompositionskalkül statt Graphen als Grundsprache verwenden; Observablen und Eingriffe als Morphismen/Prozesse, Vergleich über empirisch äquivalente Vorhersagefunktoren. Praktisch hieße das: zunächst eine **repräsentationsunabhängige Testspezifikation** und eine Familie möglicher latenter Distanz-/Einfluss-Invarianten, **nicht** ein neues axiomatisches System als Vorleistung erfinden. Ein Kandidat zählt als neuer Begriff erst, wenn er (a) ein Gegenbeispiel besser trennt, (b) eine strengere Aussage ermöglicht und (c) an Blinddaten scheitern kann. Mathematische Kategorien/GPT/Prozessmatrizen sind Werkzeuge, kein Beleg, dass „neue Mathematik nötig“ ist.

**Für Spezialisten aufbewahren:** 3+1-D-Quantengravitations-RG-Fixpunkt, chirale Eichfelder im kontrollierten Kontinuum, aus Verschränkung abgeleitete Einstein-Dynamik ohne versteckte Geometrieannahmen, mikroskopische experimentelle Quantengravitationsvorhersage.

---

# 6. Drei präregistrierbare CPU-Pilotexperimente

**Globale Regeln für alle Piloten (Vorschlag):** eigener Review-PR nach Ising-Gate; keine Cloud-Starts ohne Review. Vor Ausführung Manifest mit Git-Commit, Python-/NumPy-/SciPy-Versionen, OS, Seeds und ggf. BLAS-Version; Rohdaten + auch negative Ergebnisse aufbewahren. Gewünschte Ressourcenkappe: **max. 0,5 vCPU/1,5 GB pro Prozess, 30 Minuten Wall-Time pro Pilot**; **keine** gleichzeitigen großen Jobs auf der gemeinsam genutzten Lightsail-Maschine. Diese Budgets sind Schätzungen, keine bereits gemessenen Laufzeiten. Blind/holdout: Parameter und Schwellen anhand analytischer Referenzen/kleinem Training festlegen, Ergebnisse auf zurückgehaltenen Größen/Seeds berichten.

## Pilot A (höchste Priorität): Was ist überhaupt eine Lichtfront?

**Forschungsfrage:** Unterscheidet eine gemeinsame, interventionsbasierte Testsuite **striktes Nullsignal**, exponentiell schwache Tails und diffusive unbegrenzte Ausbreitung zuverlässig – ohne die Modelle durch eine bloße Schwelle gleichzusetzen?

**Familien:** (1) kontinuierliche 1D-Wellen-PDE, (2) kontinuierliche Wärme-PDE, (3) synchroner endlicher-Radius-CA oder linearer lokaler Update, (4) kontinuierlich evolvierender Tight-Binding-Quanten-Walk. Gleicher *dimensionsloser Vergleichsmaßstab* von Auslenkung und Zeit, **nicht** die Behauptung, alle Modelle hätten dieselben physikalischen Einheiten.

**Axiome/Input:** 1D-Koordinate oder Ring **und** gewählte Generatoren; Wellen-$c$, Wärmeleit-$\kappa$, CA-Hopzahl und Hamilton-$J$ sind gesetzt [D]. Eine effektive gemeinsame $c$ wird **nicht** emergent behauptet.

**Primäre Messgröße:** Kausalantwort $G(r,t)$ auf eine kontrollierte, kompakt unterstützte Initialstörung: Differenz zur ungestörten Präparation; für Quanten-Walk als propagierte Amplitude und separat ausgewiesene Operator-/Messantwort, **nicht** fälschlich jede Amplitude als übertragene Nachricht. Eindeutig festlegen: Störamplitude, Normierung, Zeitfenster und periodische Wrap-Around-Ausschlüsse.

**Exakte Positivkontrollen:** d’Alembert-Unterstützung der Wellenlösung (Ausgangsstörung mit kompaktem Träger), CA-Reichweiteninduktion; Tight-Binding-Lösung über Bessel-Funktionen $G_r(t)\propto i^r J_r(2Jt)$ für unendliche 1D-Kette und $v_{g,\max}=2J$ bei $a=\hbar=1$. **Negativkontrollen:** positive Wärme-Green-Funktion für alle $r$ bei $t>0$ und bewusst eingeführte all-to-all-Schwachkopplung; Nullmodell „nur Vorabkorrelation, keine Intervention“. [1–4, 14, 16, 26]

**Stichprobe/Größen:** $L=128,256,512,1024$; $t$ im Intervall vor möglichem periodischem Umlauf, z. B. $t<L/(8v_{\max})$; 12 bis 20 feste Zeitpunkte pro Größe; deterministische Modelle brauchen keine Zufalls-„CI“. Bei zufälliger Störung/rauschiger Beobachtung optional 20 Seeds mit Bootstrap auf **unabhängigen Runs**.

**Falsifikation:** Scheitert die Suite daran, bei Holdout-$L$ den strikten CA-PDE-Support von bewusst nichtverschwindenden Quanten-/Wärme-Tails zu unterscheiden, ist die vorgeschlagene „Lichtfront“-Metrik **ungeeignet**. Kein Ergebnis darf die CA-Grenze als selbstentdeckte Konstante bezeichnen. Zusätzlich prüfen, ob ein einzelner Detektionsschwellwert gegensätzliche Klassifikationen produziert.

**Unsicherheit/Fehler:** exakte Residuen gegen analytische Referenz, Gitter-Konvergenz $\Delta x,\Delta t$, Rundungsboden, unterlaufene Bessel-Tails, diskrete Ableitung, Randeffekte, thermische/Quanten-Messdefinition getrennt. Berichte Messauflösung und einen Bereich $\lvert G\rvert$ statt binärem „Signal“. **Lean 4:** Induktionssatz: synchroner lokaler Radius-$R$-Update hat nach $n$ Schritten exakt keinen Einfluss außerhalb $nR$ (auf entsprechendem definierten Einflussgraphen). **Aufwand:** Minuten auf 2 vCPU bei analytischen/1D-Numerikvergleichen; Limit 0,5 vCPU und <1 GB realistisch, vorab zu benchmarken.

**Entscheidungswert:** Sehr hoch, weil er eine frühe falsche Identifikation von Lieb–Robinson-Kegeln mit relativistischer Mikrokausalität vermeidet und representationale Vergleiche eröffnet.

## Pilot B: Dimension aus bloßer Kausalordnung – wo bricht sie?

**Forschungsfrage:** Unter welchen endlichen und adversariellen Bedingungen ist Myrheim–Meyer-Schätzung tatsächlich ein brauchbares unabhängiges Dimension-Observable und wann liefert sie eine eindrucksvolle, aber unphysikalische Zahl?

**Familien:** partielle Ordnungen/Causal Sets gegen generische und speziell konstruierte Poset-Nullmodelle (nicht Issue #4s Graph-Gitter-Fit). Poisson-Streuung **in vorgegebene** Minkowski-Alexandrov-Intervalle $D=2,3,4$ als **Kalibrierung**, keine Entstehung des $D$. $r_D$-Formel oben dient als analytischer Holdout. [6, 8]

**Kontrollen:** (i) zufällige totale Kette ($r=1$), (ii) Antikette ($r=0$), (iii) Kleitman–Rothschild-artige drei Schichten, (iv) gemischte/unverbundene Ordnungen; dazu Krümmungs-/Rand- und Poisson-Dichtevariationen in den Positivkontrollen, sofern sauber generierbar. Kein Vergleich mit Graph-Kürzestwegen, die beim Causal Set nicht dieselbe Raumdistanz darstellen.

**Design:** $N=128,256,512,1024$, pro $N,D$ mindestens 30 unabhängige Poisson-Realisationen; bei festem $N$ nur konditioniert-poissonähnliche Punktverteilung, die Unterscheidung zur unbedingten Poisson-Stichprobe explizit dokumentieren. Alle Paare $O(N^2)$ zählen (bei $N=1024$: $\sim0,5$ Mio. Paare pro Run); Vektorisierung oder blockweise Verarbeitung, Speicherlimit beachten.

**Observablen:** Ordnungsanteil $r$, geschätztes $\hat D(r)$, Bias/RMSE/Coverage über Seeds, Stabilität über Unterintervalle, unabhängig gemessene Kettenlängen-/Intervallzähl-Statistik als **zweite** Diagnostik. Die letztere sollte nicht mit demselben Datenfit justiert werden. **Falsifikation:** wenn drei-schichtige oder gemischte Nullordnungen ähnlich häufig wie positiv gestreute Causets als „D≈3/4, robust“ durchgehen, reicht der Dimensionsschätzer nicht als Geometrie-Detektor. Ein guter Erwartungswert allein besteht diesen Test **nicht**.

**Unsicherheit:** Seed-Einheiten sind komplette Causets, nicht abhängige Paarvergleiche; 95%-Bootstrap über unabhängige Realisationen; bedingte $N$-Effekte, Intervallform, Randanteil, seltene Strukturen, Nullfälle $\hat D$ undefiniert. **Lean 4:** strenger Satz über $r$ bei Kette/Antikette und Trennung von bekannten Poset-Familien; keine vorgetäuschte Formalisierung des stochastischen Kontinuumslimes. **Aufwand:** voraussichtlich wenige Minuten bis niedrige Zehnerminuten, $O(N^2)$; auf 4GB sicher nur mit Array-Batching. **Besonderheit:** $D$ ist **Raumzeitdimension**, nicht unmittelbar räumliches $d$.

**Entscheidungswert:** Hoch als Härtetest, aber erst nach Reife der Messinstrumente, **nicht** als unkontrollierte Konkurrenz zu Issue #4.

## Pilot C: Gibt es repräsentationsstabile „Dimension“ überhaupt?

**Forschungsfrage:** Kann ein gemeinsamer dimensionsartiger Makrobegriff beim Wechsel von Diffusionsoperator und Diskretisierung stabil bleiben, und erkennen unsere Filter bewusst irreführende Strukturen?

**Familien:** (i) 2D-Kontinuumsquadrat mit analytischer Wärme-Kernel-/FEM- oder Differenzenreferenz, (ii) Graphdiskretisierung desselben Gebiets, (iii) Sierpiński-Präfraktal bzw. kontinuierlich konstruierte fraktale Referenz, (iv) optional zufallsregulärer Expander als adversarieller Graph-Nullfall. Diese Referenzen geben die Dimension **vor** und dienen ausschließlich **Instrumentenkalibrierung**. Nicht mit fundamentaler Geometrogenese verwechseln. Motiviert durch Caceffo & Clemente. [10, 12, 30]

**Messgröße:** $d_s(\sigma)$ aus gemittelter Rückkehrwahrscheinlichkeit; unabhängig $d_V(r)$ mit dokumentierter Zählmaß-/Abstandsdefinition. Teste Standard-Random-Walk vs. symmetrischen/gewichteten Laplace-Operator mit bewusst wechselnden Kantenlängen/Gewichten. Im Kontinuum: Referenz $d_s\simeq2$ nur in admissiblem Zwischenbereich. Beim Fraktal müssen unterschiedliche Werte $d_H\neq d_s$ **akzeptiert** und nicht „korrigiert“ werden.

**Design:** mindestens vier Auflösungen $h$ (z. B. $32^2,64^2,128^2,256^2$ Gitterpunkte), $20$ Startpunkte/Run, $20$ Walk-Seeds bei stochastischer Implementation; unendlichen/periodischen 2D-Referenzfall von Randfall separat auswerten. Der schwerere $256^2$-Fall nutzt **sparse** Operatoren oder Zufallswege, keine dichte $N\times N$-Matrix. Keine universellen $\sigma$-Fits über Mikrogitter- und Sättigungsregime.

**Null/Adversarial:** Kanten-Shortcut im Graphen bei gleichbleibendem Knotenzahlmaß; gleicher „Geometriename“, aber falscher Laplace-Operator; Expander mit nicht-polynomiellem Ballwachstum. **Falsifikation:** signifikante Verschiebung von $d_s$ zwischen Diskretisierungen/Operatoren trotz vermeintlich gleichem Kontinuumslimes oder Klassifikation eines Expanders als stabile euklidische Dimension ohne Diagnose. Solche Ergebnisse sprechen **gegen die robuste Kennzahl**, nicht für physikalische Dimensionstransmutation.

**Unsicherheit:** Resolution-/Diffusions-Zeitfenster-Pre-Registration, logarithmische Ableitungs-Glättung, Walk-Autokorrelation, Cluster-Bootstrap nach unabhängigen Walks/Startpunkten, Fits mit Sample-Splitting und Holdout-Auflösung. **Lean 4:** endliche kombinatorische Aussagen über Ballwachstum im Ring/Hyperkubus oder Invarianz einfacher Laplace-Operator-Symmetrien; eine exakte Hausdorff/Spektral-Grenzwerttheorie ist nicht sinnvoll als erster Lean-Scope. **Aufwand:** Minuten bis <30 min bei sparse Berechnung mit bis ~65k Zuständen und begrenzter Walkzahl; zuerst lokal profilen.

**Entscheidungswert:** Mittel bis hoch als **gegenstandsneutrale Instrumentenprüfung**; nur mit klarer Trennung von Issue #4 durchführen.

---

# 7. Drei Falleffekte, die wir aktiv verhindern müssen

**Falle 1 – hartcodierte Dimension als Entdeckung:** Ein $L\times L\times L$-Gitter ergibt $d_V\approx3$, weil bereits drei Achsen eingeführt wurden. Ein CDT-Simplex hat eine vorgegebene Dimension; ein MERA-Netzwerk eine gewählte Schichtstruktur. **Gegenprobe:** gleiche Pipeline auf Expander, Fraktal und dimensionswechselndem Referenzensemble; aus Inputliste beweisen, ob die Dimension schon vorhanden ist.

**Falle 2 – hartcodierter Lichtkegel als Emergenz:** Update-Regel betrachtet nur direkte Nachbarn, also exakt höchstens ein Hop je Tick. Das zeigt einen korrekten induktiven Satz, aber keinerlei Herleitung der Naturkonstante $c$ oder der Lorentzstruktur. **Gegenprobe:** zeitkontinuierlicher Quanten-Walk und langreichweitige Kopplung; Frontbegriff mit absoluten Tails publizieren.

**Falle 3 – Korrelation oder Schwellwert wird zu Kausalität:** Eine korrelierte Fernmessung, ein gemeinsames Rauschen oder Messpräzision $10^{-6}$ produziert optisch einen Kegel. **Gegenprobe:** Intervention vs. Kontrolle, exakte analytische Null, unterschiedliche Schwellen und unabhängige Skalierungsgrößen, Operatornorm statt nur einzelner Zustandskorrelation.

---

# 8. Roadmap mit Abbruch- und Pivot-Gates

| Gate | Bedingung für Fortsetzung | Stop/Pivot |
|---|---|---|
| **G0: Governance (jetzt)** | Literaturbericht von einem Menschen überprüft; PR #5 berücksichtigt; Ising-Gate getrennt; verbindliche Definition von „Einfluss“ | bei unklarer Kausalmetrik **keine** Geometrie-Wildsuche |
| **G1: Instrument (Pilot A)** | striktes Null, exponentielle/analytische Tails und diffusive Ausbreitung in unabhängigen Holdout-Fällen getrennt; Normierungs- und Schwellenabhängigkeit dokumentiert | falls Klassifikation schwellwertgetrieben: neues Observable statt Modelloptimierung |
| **G2: Dimension (Pilot B)** | Positiv-Intervalle über $N$ sinnvoll rekonstruiert und adversarielle Posets zuverlässig als OOD erkannt | falls Nullposets falsche stabile Dimension liefern: Dimension **nicht** als Geometrogenese-Signal verwenden |
| **G3: Repräsentation (Pilot C)** | $\hat d$ in zulässigen Skalen gegenüber numerisch äquivalenten Darstellungen stabil oder Abhängigkeit gut charakterisiert; Fraktalunterschiede korrekt | wenn operatorabhängig: nur gemeinsames spektrales/operationales Observable statt „die Dimension“ behaupten |
| **G4: First discovery claim** | ein **nicht triviales**, an Holdouts stabiles struktur-/dynamikübergreifendes Invarianz- oder notwendige-Bedingung-Resultat; Literaturabgleich + Skeptikerprüfung; ggf. Lean-Satz | bei Wiederentdeckung nur Benchmark archivieren |
| **G5: Physikbezug (fern)** | klar formulierte Lorentz-/Relativitätsvorhersage mit externem Beobachtungscheck und Modellunterscheidbarkeit | ohne neue Vorhersage **keine** Behauptung fundamentaler Physik |

**Vorläufiger Arbeitsplan (nach Ising-Gate):** 1 Forschungsiteration zur Definition und Präregistrierung von Pilot A → 1–2 Iterationen zur Minimalimplementation und Exakttests → eigenständige Review der Negativkontrollen → anschließend B, danach C. Reihenfolge ist ein Vorschlag; keine Kalenderlaufzeit und keine Cloud-Nutzung wird behauptet. Ergebnisse aus B/C können Pilot-A-Priorisierung revidieren. Ein generatives Modell/LLM darf Kandidaten für neue Invarianten vorschlagen, darf jedoch nicht Evaluationskriterien nach dem Holdout rückwirkend verändern.

**Wissenschaftlicher Nullbefund als möglicher Gewinn:** Wenn zwei mikroskopisch sehr verschiedene Systeme dieselben Dimension- und Frontdaten liefern, aber durch ein drittes Observable trennbar sind, haben wir ein *operationales Identifizierbarkeitsresultat*. Wenn keine Trennung gelingt, quantifizieren wir die Unterbestimmtheit; beides ist sinnvoller als auf Basis schöner Plots ein Substrat zu postulieren.

---

# 9. Annotierte Bibliographie (Auswahl, 35 Quellen)

Alle DOI/arXiv-Identifier sind als stabile Links angegeben. **„Satz“** bezeichnet nur die präzise in der Veröffentlichung behandelte Klasse; **„numerisch“** keine empirische Validierung von Quantengravitation. Quellen [13] und [16] sind ausdrücklich Preprints.

1. **Lieb, E. H.; Robinson, D. W. (1972)**, *The finite group velocity of quantum spin systems*, Commun. Math. Phys. 28, 251–257. [DOI](https://doi.org/10.1007/BF01645779). **[S]** Originale lokale Informations-Schranke; Lokalität als Input.
2. **Nachtergaele, B.; Sims, R. (2006)**, *Lieb-Robinson bounds and the exponential clustering theorem*, Commun. Math. Phys. 265, 119–130. [DOI](https://doi.org/10.1007/s00220-006-1556-1). **[S]** Ausweitung; Verbindung von Gap und räumlichem Korrelationsabfall, nicht Mikrokausalität.
3. **Wilming, H.; Werner, A. H. (2022)**, *Lieb-Robinson bounds imply locality of interactions*, Phys. Rev. B 105, 125101. [DOI](https://doi.org/10.1103/PhysRevB.105.125101). **[S]** Wichtige inverse Richtung für definierte k-Body-Interaktionen; Annahmen genau lesen.
4. **Barceló, C.; Liberati, S.; Visser, M. (2026)**, *Analogue gravity*, Living Rev. Relativ. 29, 2 (Revision von 2011). [DOI](https://doi.org/10.1007/s41114-026-00064-9). **[Review, 2026]** breite Kontinuums- und Experimentfamilie; effektive Metrik, keine automatische fundamentale Gravitation.
5. **Malament, D. B. (1977)**, *The class of continuous timelike curves determines the topology of spacetime*, J. Math. Phys. 18, 1399–1404. [DOI](https://doi.org/10.1063/1.523436). **[S]** Kausale Rekonstruktion bei Regularitätsbedingungen; kein beliebiger Poset-Satz.
6. **Bombelli, L.; Lee, J.; Meyer, D.; Sorkin, R. D. (1987)**, *Space-time as a causal set*, Phys. Rev. Lett. 59, 521–524. [DOI](https://doi.org/10.1103/PhysRevLett.59.521). **[Theorie]** Grundlegung; vorschlagsweise diskretes Substrat, noch keine vollständige Dynamik.
7. **Hawking, S. W.; King, A. R.; McCarthy, P. J. (1976)**, *A new topology for curved space–time which incorporates the causal, differential, and conformal structures*, J. Math. Phys. 17, 174–181. [DOI](https://doi.org/10.1063/1.522874). **[S/Theorie]** Zusammenhang Topologie/Kausalität bei stark kausalen Raumzeiten.
8. **Surya, S. (2019)**, *The causal set approach to quantum gravity*, Living Rev. Relativ. 22, 5. [DOI](https://doi.org/10.1007/s41114-019-0023-1). **[Review]** maßgebliches Nachschlagewerk zu Dimension, Ordnungsrelationen, Dynamik und Kontinuumsproblemen.
9. **Reid, D. D. (2003)**, *Manifold dimension of a causal set: Tests in conformally flat spacetimes*, Phys. Rev. D 67, 024034. [DOI](https://doi.org/10.1103/PhysRevD.67.024034). **[N]** Dimensionstests, implizite Kontinuumsreferenz.
10. **Ambjørn, J.; Jurkiewicz, J.; Loll, R. (2005)**, *The spectral dimension of the universe is scale dependent*, Phys. Rev. Lett. 95, 171301. [DOI](https://doi.org/10.1103/PhysRevLett.95.171301). **[N]** prominenter Dimensionsfluss; Basisdimensionsstruktur im CDT vorgegeben.
11. **Ambjørn, J.; Gizbert-Studnicki, J.; Görlich, A.; Jurkiewicz, J.; Loll, R. (2020)**, *Renormalization in Quantum Theories of Geometry*, Front. Phys. 8, 247. [DOI](https://doi.org/10.3389/fphy.2020.00247). **[Review/N]** ausdrücklicher negativer Stand zu bestimmten UV-Fixpunkt-Observablen.
12. **Caceffo, F.; Clemente, G. (2023)**, *Spectral analysis of causal dynamical triangulations via finite element method*, Phys. Rev. D 107, 074501. [DOI](https://doi.org/10.1103/PhysRevD.107.074501). **[N/Methodik]** zentrale Warnung: Graph- und Kontinuums-Laplace-Spektren können abweichen.
13. **Ambjørn, J.; Loll, R. (2026)**, *Causal Dynamical Triangulations: New Lattice Theory of Quantum Gravity*, [arXiv:2604.05641](https://arxiv.org/abs/2604.05641). **[Preprint/Review, nicht als begutachtet verifiziert]** aktueller positiver CDT-Status; noch kein Schluss über UV-RG-Problematik.
14. **Kuwahara, T.; Saito, K. (2020)**, *Strictly Linear Light Cones in Long-Range Interacting Systems of Arbitrary Dimensions*, Phys. Rev. X 10, 031010. [DOI](https://doi.org/10.1103/PhysRevX.10.031010). **[S]** long-range-Grenzfälle, Aufgaben-/Dimensionsannahmen.
15. **Tran, M. C. et al. (2021)**, *Lieb-Robinson Light Cone for Power-Law Interactions*, Phys. Rev. Lett. 127, 160401. [DOI](https://doi.org/10.1103/PhysRevLett.127.160401). **[S]** scharfe Propagationsschranken in relevanter Regime-Klasse.
16. **Schumacher, B.; Werner, R. F. (2004)**, *Reversible quantum cellular automata*, [arXiv:quant-ph/0405174](https://arxiv.org/abs/quant-ph/0405174). **[Preprint/S innerhalb der formalen Definition]** QCA-Struktursatz; strikte endliche Geschwindigkeit bereits im Axiom.
17. **D’Ariano, G. M.; Perinotti, P. (2014)**, *Derivation of the Dirac equation from principles of information processing*, Phys. Rev. A 90, 062106. [DOI](https://doi.org/10.1103/PhysRevA.90.062106). **[S asymptotisch]** Dirac-Limes unter starker Symmetrie-/Lokalisierungsannahme, UV-Lorentzabweichung.
18. **Konopka, T.; Markopoulou, F.; Severini, S. (2008)**, *Quantum graphity: A model of emergent locality*, Phys. Rev. D 77, 104029. [DOI](https://doi.org/10.1103/PhysRevD.77.104029). **[N/H]** dynamische Graph-Geometrie, gezielte Modellenergie und nicht-physikalisch validierter Phasenübergang.
19. **Konopka, T. (2008)**, *Statistical mechanics of graphity models*, Phys. Rev. D 78, 044032. [DOI](https://doi.org/10.1103/PhysRevD.78.044032). **[N/Analyse]** Materiedynamik relevant, einfacher Graphity-Erfolg keineswegs automatisch.
20. **Vidal, G. (2007)**, *Entanglement renormalization*, Phys. Rev. Lett. 99, 220405. [DOI](https://doi.org/10.1103/PhysRevLett.99.220405). **[Methode/N]** RG/Skalen-Netzwerke; keine alleinige Geometrogenese.
21. **Swingle, B. (2012)**, *Entanglement renormalization and holography*, Phys. Rev. D 86, 065007. [DOI](https://doi.org/10.1103/PhysRevD.86.065007). **[I/Theorie]** geometrische Deutung multiskaliger Entanglement-Struktur.
22. **Ryu, S.; Takayanagi, T. (2006)**, *Holographic derivation of entanglement entropy from AdS/CFT*, Phys. Rev. Lett. 96, 181602. [DOI](https://doi.org/10.1103/PhysRevLett.96.181602). **[Theorie unter holographischen Annahmen]** geometrischer Entropiezusammenhang, kein allgemeiner Kausalersatz.
23. **Maldacena, J. (1998)**, *The large N limit of superconformal field theories and supergravity*, Adv. Theor. Math. Phys. 2, 231–252. [DOI](https://doi.org/10.4310/atmp.1998.v2.n2.a1). **[Theorie/duale Struktur]** originäres AdS/CFT-Szenario, spezialisiert.
24. **Almheiri, A.; Dong, X.; Harlow, D. (2015)**, *Bulk locality and quantum error correction in AdS/CFT*, JHEP 04, 163. [DOI](https://doi.org/10.1007/JHEP04(2015)163). **[Theorie]** präzise Bulk-QEC-Verbindung und Rekonstruktionsgrenzen.
25. **Oreshkov, O.; Costa, F.; Brukner, Č. (2012)**, *Quantum correlations with no causal order*, Nat. Commun. 3, 1092. [DOI](https://doi.org/10.1038/ncomms2076). **[S formal]** Prozessmatrix ohne feste globale Ordnung; keine spontane 3D-Entstehung.
26. **Unruh, W. G. (1981)**, *Experimental black-hole evaporation?*, Phys. Rev. Lett. 46, 1351–1353. [DOI](https://doi.org/10.1103/PhysRevLett.46.1351). **[Theoretischer Ursprung]** akustische Horizont-Analogie, keine experimentelle Bestätigung des astronomischen Hawking-Effekts.
27. **Nielsen, H. B.; Ninomiya, M. (1981)**, *A no-go theorem for regularizing chiral fermions*, Phys. Lett. B 105, 219–223. [DOI](https://doi.org/10.1016/0370-2693(81)91026-1). **[S]** eng umrissene Gitter-Chiralitätsblockade, nicht „Diskretheit unmöglich“.
28. **Bombelli, L.; Henson, J.; Sorkin, R. D. (2009)**, *Discreteness without symmetry breaking: a theorem*, Mod. Phys. Lett. A 24, 2579–2587. [DOI](https://doi.org/10.1142/S0217732309031958). **[S]** Lorentz-invariantes Poisson-Sprinkling ohne äquivariante lokal endliche Nachbarschaft.
29. **Chiribella, G.; D’Ariano, G. M.; Perinotti, P. (2011)**, *Informational derivation of quantum theory*, Phys. Rev. A 84, 012311. [DOI](https://doi.org/10.1103/PhysRevA.84.012311). **[S innerhalb der Axiome]** alternative mathematische Startpunkte.
30. **Barlow, M. T.; Perkins, E. A. (1988)**, *Brownian motion on the Sierpinski gasket*, Probab. Theory Relat. Fields 79, 543–623. [DOI](https://doi.org/10.1007/BF00318785). **[S]** Diffusion auf Fraktalen, $d_s\neq d_H$; wichtiges Schätzer-Gegenbeispiel.
31. **Masanes, L.; Müller, M. P. (2011)**, *A derivation of quantum theory from physical requirements*, New J. Phys. 13, 063001. [DOI](https://doi.org/10.1088/1367-2630/13/6/063001). **[S unter Axiomen]** Rekonstruktion/Alternativen; keine Raumzeitdynamik.
32. **Tran, M. C. et al. (2020)**, *Hierarchy of Linear Light Cones with Long-Range Interactions*, Phys. Rev. X 10, 031009, **mit Erratum 2023**. [Original](https://doi.org/10.1103/PhysRevX.10.031009), [Erratum](https://doi.org/10.1103/PhysRevX.13.029901). **[S]** Unterscheidung unterschiedlicher Aufgaben-/Normkegel.
33. **Kleitman, D. J.; Rothschild, B. L. (1975)**, *Asymptotic enumeration of partial orders on a finite set*, Trans. Amer. Math. Soc. 205, 205–220. [DOI](https://doi.org/10.2307/1997200). **[S]** Großteil endlicher Posets sind nicht manifoldartig.
34. **Carlip, S. (2024)**, *Causal sets and an emerging continuum*, Gen. Relativ. Gravit. 56, 95. [DOI](https://doi.org/10.1007/s10714-024-03281-1). **[Forschungsbericht/theoretischer Partialfortschritt]** starke Wirkungssuppression bestimmter unphysikalischer Klassen, keine allgemeine Lösung.
35. **LHAASO Collaboration (2024)**, *Stringent Tests of Lorentz Invariance Violation from LHAASO Observations of GRB 221009A*, Phys. Rev. Lett. 133, 071501. [DOI](https://doi.org/10.1103/PhysRevLett.133.071501). **[E unter Modellannahmen]** constraints gegen konkrete Photonendispersion, keine Bestätigung eines emergenten Substrats.

## 10. Fazit und konkreter Handoff

**Wissenschaftlich belastbare Entscheidung:** Das Lab soll zunächst **Messlogik, Gegenbeispiele und Invarianz** erforschen, nicht die „richtige Mikrowelt“ suchen. Ein Ergebnis, das in einer solchen kleinen CPU-Studie überzeugen kann, wäre etwa ein exakter Beweis über notwendige Lokalitätsannahmen oder ein robust replizierter Negativbefund zu einer Dimension-/Kausalschätzung. Das wäre für unseren Ressourcenrahmen ehrlich und wertvoll.

**Was heute tatsächlich geschah:** Projektdokumente und Issue #6 wurden gelesen; Literatur recherchiert, zugeordnet und kritisch bewertet; drei Pilotprotokolle erstellt. **Keine** Simulation gestartet, kein bestehender Simulationscode verändert, **keine** empirische oder neue mathematische Entdeckung beansprucht. Der wissenschaftliche Bericht benötigt unabhängige fachliche Gegenlektüre. **Nächster kleinster Schritt:** auf Issue #6/Pull Request die Definition „interventionelle Antwort vs. Operatornorm vs. Signal“ und die Präregistrierung von **Pilot A** begutachten; Ising-Kalibrierung unangetastet lassen.
