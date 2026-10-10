# Pilot A: Präregistrierung zu kausalen Eingriffen und Ausbreitungsgrenzen

**Emergence Lab · 09.10.2026 · Protokoll v1.0 · NICHT ausgeführt**

**Kontext:** [Forschungsauftrag #6](https://github.com/shaden7/emergence-lab/issues/6), [wissenschaftlicher Literaturbericht (Draft-PR #8)](https://github.com/shaden7/emergence-lab/pull/8), [Repräsentationsstrategie (PR #5)](https://github.com/shaden7/emergence-lab/pull/5), [AGENTS.md](../AGENTS.md), [OVERVIEW.md](OVERVIEW.md), [RESEARCH_STATE.md](RESEARCH_STATE.md), [RESEARCH_DIRECTOR.md](RESEARCH_DIRECTOR.md).

> **Status:** Dieses Dokument registriert *vor* einer Implementierung Fragestellung, Modelle, Referenzen, Daten-Split, Gegenmodelle, Akzeptanz- und Stopkriterien. Es behauptet keine neuen physikalischen Ergebnisse. **Keine Simulation, keine neue Rechenlast, keine Code-/Ising-/Deploy-Änderung.** Numerische Ausführung erst nach separatem Review-PR und geschlossenem Ising-Kalibrierungsgate oder ausdrücklich dokumentierter Ausnahme.

## 1. Problem, Hypothesen, Erkenntnisziel

**Problem:** Unter welchen operationalen Voraussetzungen darf eine Messung als *kausaler Einfluss* gelten? Und wie lässt sich der Unterschied zwischen strikter räumlicher Supportgrenze, exponentiell kleinen Fernantworten, ballistischer effektiver Front und sofortiger diffuser Ausbreitung zuverlässig bestimmen?

**H1 [vorgeschlagene Methoden-Hypothese]:** Eine vorab definierte Interventionsantwort zusammen mit unabhängigen mathematischen Referenzen klassifiziert vier Modellfamilien auf Holdout-Daten fehlerfrei als **streng begrenzte** oder **nichtstreng begrenzte** Ausbreitung, sofern der relevante Wert oberhalb des numerisch nachgewiesenen Präzisionsbodens liegt. Analytisch garantierte, aber numerisch zu kleine Werte werden als **zensiert**, nie als „genau null“, ausgewiesen.

**H2 [Test des Messinstruments]:** Ein schwellwertbasierter detektierter „Lichtkegel“ ist als Nachweis einer *strikten* Geschwindigkeitsgrenze nicht zuverlässig. Änderungen der Messschwelle, Datenauflösung oder Beobachtungszeit können eine andere scheinbare Front erzeugen, obwohl die exakte Dynamik unverändert ist.

**Erkenntnisziel:** geprüfte operationale Testspezifikation, systematische Aufdeckung irreführender Messungen und eventueller kleiner Lean-4-Satz über die **Annahmen** lokaler Updates. Es handelt sich primär um *Kalibrierung und Falsifikation*, nicht um eine Suche nach neuer Quantengravitation.

**Nicht als zu beweisen vorausgesetzt:** fundamentale diskrete Welt, natürliches Raumdimensionsergebnis, emergente Zeit, Lorentzinvarianz oder universelle Lichtgeschwindigkeit. Alle vier Basismodelle besitzen explizit eine **eingebaute eindimensionale Ortsskala** und **eingebaute Zeit**.

## 2. Operationale Definitionen (vor dem Versuch fixiert)

### 2.1 Eingriff statt Korrelation

Für jedes Modell M werden Ortsträger, Metrik d, Uhr t, Dynamik, lokale Präparation und lokale Observable *ausdrücklich als Input* spezifiziert.

Zwei Welten unterscheiden sich nur durch einen Eingriff am Ursprung zum Zeitpunkt 0. Das entfernte System, sämtliche Parameter, Rauschrealisierungen und die übrigen Anfangsbedingungen werden festgehalten. Eine rein beobachtete Korrelation ist keine gültige Quelle für eine Kausalbehauptung.

Der *vorab ausgewählte Einflusszeuge* lautet:

\[
S_M(r,t) =
\bigl|\mathbb{E}[O_r(t)\mid\mathrm{do}(I_0)]
      -\mathbb{E}[O_r(t)\mid\mathrm{do}(I_\varnothing)]\bigr|,\qquad
Q_M(r,t)=\frac{S_M(r,t)}{S_M(0,0)}.
\]

Alle gewählten Modelle haben S(0,0)=1. Die Normierung erlaubt eine *formale* Gegenüberstellung des Supports, **nicht** eine Gleichsetzung von Quanten-Nachrichtenkapazität, Felddynamik und Boolescher Bitübertragung. Im Quantenmodell ist die Observable eine **lokale Teilchenbesetzungswahrscheinlichkeit**, keine Wellenamplitude als scheinbares „Signal“.

Der Witness S ist *nicht* die maximale kausale Kommunikationsfähigkeit. Ein besserer, hier **nicht implementierter** Begriff wäre die Supremums-Totalvariation der entfernten Messstatistik über alle zulässigen lokalen Präparationen und Messungen (im Quantenfall CPTP-Operationen). Eine zufällige Nullstelle von S bei einer bestimmten Eingabe beweist deshalb niemals fehlenden kausalen Einfluss aller Eingriffe.

### 2.2 Kategorien

- **Strikte Supportgrenze [Satz]:** für *alle zulässigen* kompakten Eingriffe innerhalb Radius a ist die Wirkung außerhalb d>a+vt exakt 0, für eine endliche und **größenunabhängige** Geschwindigkeitskonstante v. Bei synchronen CA nach n Schritten entsprechend d>nR. Eine solche Aussage erfordert Beweis bzw. vollständige analytische Modellstruktur.
- **Nichtstrikter Einfluss [analytischer Gegenzeuge]:** für jedes vorgeschlagene größenunabhängige v existieren positive Zeiten und beliebig ferne Orte außerhalb seines Kegels mit echter, wenn auch kleiner Antwort S>0. Nicht aus einer Extrapolation einzelner Plotpunkte folgern.
- **Effektive Ausbreitungsfront:** Antworten *innerhalb* eines geeigneten Kegels dominieren; außerhalb kann ein nichtverschwindender, z.B. exponentiell geschwächter Tail bestehen. Dies ist keine relativistische Mikrokausalität.
- **Detektionsfront:** \(r_\eta(t)=\max\{r\text{ unter den vorgegebenen Messorten}:Q_M(r,t)\ge\eta\}\), sonst undefiniert. Dies ist ein von Messfenster, Schwelle und Rauschen abhängiger Diagnostikwert.
- **Numerisch nicht entscheidbar:** Referenz/Wert kleiner als nachgewiesene Rundungs-/Nachweisgrenze; keine Auslegung als Nullantwort.

Strikter Support, endliche Gruppen-/Phasengeschwindigkeit, Lieb–Robinson-Bound und relativistischer Lichtkegel bleiben **unterschiedliche Begriffe**.

### 2.3 Abstand und Zeit sind Input

Im PDE-Test wird x in der **vorab gegebenen** kontinuierlichen Linie verwendet; im CA und im Quantentest Ringabstand \(\min(|r|,L-|r|)\), mit vorgegebenem Tick bzw. Quanten-Evolutionsparameter. Weder Distanz noch Zeit wird aus einer beobachteten Front konstruiert. Eine Frontgeschwindigkeit darf nicht dadurch tautologisch festgelegt werden, dass der Abstand nachträglich als Reaktionszeit mal Geschwindigkeit umdefiniert wird.

## 3. Festgelegte Basismodelle und analytische Prüfsteine

### W — Kontinuierliche Wellengleichung (Positivkontrolle strikter Support)

- Gleichung \(u_{tt}=c^2 u_{xx}\) auf \(\mathbb R\), **vorgegeben** c=1.
- Eingriff: \(u(x,0)=f(x)=\mathbf 1_{[-a,a]}(x)\), \(u_t(x,0)=0\), a=0,5; Kontrolle ist Nullfeld.
- Observable O_r(t)=u(r,t).
- Analytische Referenz (d'Alembert): \(u(r,t)=\frac12[f(r-t)+f(r+t)]\).
- **Bewiesene Eigenschaft:** für \(|r|>a+t\) exakt 0. Aufgrund der stückweise unstetigen Anregung werden Orte exakt auf Wellenfronten **nicht** in relative Fehlerfits aufgenommen; Sensitivitätscheck mit glattem kompaktem Bump optional.
- **Versteckte Annahmen offenlegen:** hyperbolischer Differentialoperator und c bereits als Input. Keine emergente Geschwindigkeit.

### H — Kontinuierliche Wärmeleitung (adversarieller nichtstrikter Support)

- Gleichung \(u_t=\kappa u_{xx}\) auf \(\mathbb R\), **vorgegeben** \(\kappa=1\).
- **Derselbe** kompakte Anfangspuls f und dieselbe Null-Kontrolle; Observable u(r,t).
- Unabhängige kontinuierliche Lösung
\[
u(r,t)=\frac{1}{\sqrt{4\pi t}}\int_{-a}^{a}
       \exp[-(r-y)^2/(4t)]\,\mathrm dy .
\]
- **Bewiesene Eigenschaft:** weil der Integrand positiv ist, \(u(r,t)>0\) für jeden endlichen r und t>0; eine beliebig weit entfernte Wirkung tritt mathematisch sofort auf.
- **Wichtigster Negativtest:** lokale Euler-Finite-Differenzen-Schritte können eine künstliche harte numerische Front haben, obwohl die **Kontinuums-PDE** unbeschränkten Support hat. Darum sind analytische Kernel/eine stabil ausgewertete erfc-Differenz die **Primärreferenz**. Euler nur als explizit gekennzeichnete Artefakt-Demonstration.

### CA — Boolescher lokaler Automat (strikte Front eingebaut)

- Ring \(\mathbb Z/L\mathbb Z\), Zeit n ganzzahlig; Anfangsbit z_0(0)=1 und alle anderen 0, Kontrolle alle 0.
- Regel \(z_j(n+1)=z_{j-1}(n)\lor z_j(n)\lor z_{j+1}(n)\).
- Observable lokales z_r(n), damit S=z_r(n).
- **Induktive Referenz:** bei \(n<L/2\) gilt z_r(n)=1 genau für \(\mathrm{dist}_{\rm Ring}(0,r)\le n\), sonst exakt 0.
- **Keine emergente Lichtgeschwindigkeit:** der maximale Hop pro Takt steht explizit in der Update-Regel. Das Ergebnis kalibriert nur die Prüfung der exakten Abhängigkeit.

### Q — Zeitkontinuierlicher Quantenspaziergang (effektive Front, Tail)

- Ring aus L Orten, Hamiltonian im Einteilchensektor \(H=-J\sum_j(|j+1\rangle\langle j|+\mathrm{h.c.})\) mit J=1, kontinuierliches t.
- **Lokale physikalische Präparation:** eine einzelne Anregung am Ort 0 aus dem Vakuum gegen unverändertes Vakuum; dafür ist begrifflich ein Vakuum-plus-Einteilchen-Fockraum erforderlich, obwohl numerisch nur Einteilchendynamik nötig ist.
- Observable am Ort r ist die Teilchenzahl n_r. Für den Eingriff \(S_Q(r,t)=p_L(r,t)\); im Vakuum p=0.
- **Unabhängige Fourier-Referenz auf endlichem Ring:**
\[
p_L(r,t)=\Bigl|\frac{1}{L}\sum_{k=0}^{L-1}
 e^{2it\cos(2\pi k/L)}\,e^{2\pi i kr/L}\Bigr|^2.
\]
Für die *unendliche* Linie: \(p(r,t)=|J_r(2t)|^2\), mit Besselfunktion \(J_r\). Der endliche Ring wird numerisch **zuerst** gegen seine Fourierlösung getestet; die Besselform ist eine eigenständige unendliche-Linie-Grenzreferenz.
- **Mathematische Aussage:** eine lokale zeitkontinuierliche Quantenkopplung hat im Allgemeinen bei positiven Zeiten fernes, sehr kleines nichtverschwindendes Gewicht; für feste endliche Entfernung ist der erste nichtverschwindende Taylor-Koeffizient durch kürzeste Hopwege bestimmt. Einzelne exakte Interferenznullstellen sind möglich und widerlegen diese grundsätzliche Aussage nicht.
- **Achtung:** Maximalgeschwindigkeit \(2J\) der Gruppendispersion auf der unendlichen Kette ist *nicht* strikte Signalgeschwindigkeit, LR-Geschwindigkeit oder c des Vakuums.

### Gegenüberstellung

| Modell | Mathematischer Support | Optische Front | Was vorgegeben ist |
| --- | --- | --- | --- |
| W | strikt \(|r|\le a+t\) | scharfe Wellenfront | Kontinuumsmetrik, Hyperbolizität, c |
| H | bei t>0 überall positiv | diffuses, schwellenabhängiges Profil | Kontinuumsmetrik, parabolischer Operator, κ |
| CA | strikt d≤n | scharfer Hop-Kegel | Nachbarschaft, Tick, Radius 1 |
| Q | grundsätzlich nichtstrikt | annähernd ballistische Front plus Tails | Ring, Lokalkopplung, Hamiltonian, J |

Ein Gleichklang zweier Bilder ist **kein** physikalischer Äquivalenzbeleg.

## 4. Adversarielle Nullmodelle und Angriffe auf das Messverfahren

**N1 — Scheinkausalität durch Korrelation:** Ein globaler verborgener Zufall Z ist in zwei Beobachtungen sichtbar. Beobachtungs-Korrelation ist positiv; ein absichtlicher lokaler Eingriff am ersten Ort ändert die entfernte Z-Beobachtung bei festgehaltenem Z nicht. Vorhersage: Korrelation ≠0, dennoch interventionelles S=0. Gepaarten Hintergrund verwenden.

**N2 — Langstrecken-Shortcut:** Zum Q-Ring wird ein zusätzlicher Hop von Ort 0 zu \(r_*=L/4\) eingeführt, Kopplung \(\epsilon=0{,}05\), L=128,256,512. Die Messdistanz bleibt ausdrücklich **die ursprüngliche Ringmetrik**. Frühe Fernbesetzung durch die *eingebaute* Fernkante ist ein bewusst adversarieller Test. Eine unveränderte lokale Ring-Geschwindigkeitskonstante kann bei wachsendem L nicht beansprucht werden. Wenn die neue Kante als Abstand 1 gewertet würde, wäre **die Metrik gewechselt**; dies muss als alternatives Modell und nicht als Widerlegung derselben Geometrie gekennzeichnet werden.

**N3 — Schwellenfront als falscher Lichtkegel:** Messschwellen \(\eta\in\{10^{-3},10^{-6},10^{-9}\}\) auf Q; optional auf H; dokumentiere je Schwelle r_eta(t) und fehlende Messwerte. Positive analytische Tails unter einer Schwelle bleiben positiv. **Niemals** aus einem Schwellenfit auf strikte Kausalität schließen.

**N4 — Lokaler PDE-Solver als falsche Kontinuumsphysik:** Ein expliziter Zeit-Stencil für Wärmeleitung ist endlichreichweitig pro Rechenschritt; eine so gemessene harte Front wäre ein **Solverartefakt**, nicht eine Eigenschaft der ursprünglichen PDE. Separat und als optionalen Negativkontrolllauf etikettieren.

**N5 — Rauschen:** Optional unabhängiges additives *Messrauschen* mit \(\sigma\in\{0,10^{-6},10^{-4}\}\); es verändert nicht die physikalische Dynamik. Ob Signal entdeckt wird, kann schwellen-/rauschabhängig sein. Dies darf keinen Statuswechsel von „mathematisch nichtstrikt“ zu „strikt“ auslösen.

## 5. Daten-Split und feste Versuchsparameter

**Dimensionlose Haupteinstellungen:** a=0,5, c=κ=J=1; CA-Hopradius R=1. Ringgrößen L=128,256,512,1024. Die W/H-Gerade ist unendlich; Messung nur an ausgewählten ganzzahligen x. Kein Modellparameter wird an der Testantwort gefittet.

**Entwicklung/Kalibrierung (explizit **nicht** als unabhängiger Holdout):**
- Q und W/H Zeiten t = 0,5; 1; 2, Messorte r = 0,1,2,4,6,8,12, Ringgrößen L=128,256 (Q).
- CA Zeiten n=0,1,2,4,8, gleiche r, L=128,256.

**Unbenutzte Holdout-Konfiguration (nach Freigabe unverändert auswerten):**
- Q und W/H Zeiten t = 0,75; 1,5; 3; Messorte r=0,3,5,7,11,15; Q auf L=512,1024.
- CA Zeiten n=3,5,12; gleiche r und L=512,1024.
- Q-Endlichkeitsvergleich gegen eigenständig implementierte Fourier-Referenz; Bessel nur als zweiter Grenzwert-Check.

**Explizit registrierte analytische Fernzeugen:** Bei t=1 und r=4,6 liegen die Orte sicher außerhalb der W-Front (a+t=1,5). H und Q haben dagegen jeweils positive Antworten. Diese Referenzen werden **vor** Implementierung als erwartete Vorzeichen/Supportklassen festgehalten. Es wird keine numerisch gemessene Größe vorweggenommen.

**Größen-/Randbedingung:** CA nur n<L/2. Q-Finite-Size-Effekte nie durch theoretische Gleichsetzung von Ring und unendlicher Linie verdecken. Bei W/H keine künstlichen periodischen Randbedingungen in der Primärreferenz; Frontgleichheit bei Top-Hat gesondert behandeln.

## 6. Präregistrierte Prüf- und Stopkriterien

**A1 (Manipulation/Negativkontrolle):** Die Baseline bleibt vollständig ungestört; die gewählte Intervention ist zur Anfangszeit ausschließlich lokal. N1 zeigt remote \(\Delta=0\) trotz positiver Beobachtungskorrelation. **Scheitert dies, wird nicht weiter als kausaler Test ausgewertet.**

**A2 (strikter Support):** Bei W außerhalb \(|r|>a+t\) analytisch exakt Null, bei CA bei d>n exakt Null. Ein zugehöriger, vom numerischen Ergebnis unabhängiger mathematischer Support-Satz ist angegeben. Einzelne numerische Nullwerte sind kein Beweis.

**A3 (nichtstrikter Gegenzeuge):** H und Q bei \((t,r)=(1,4),(1,6)\) mit analytisch garantiert positivem S werden korrekt als Fernantwort erkannt. Für \(S_\mathrm{ref}\ge10^{-8}\) gilt vorab:
\[
|S_\mathrm{num}-S_\mathrm{ref}|\le
\max(10^{-11},10^{-6}S_\mathrm{ref}).
\]
Für kleinere/unterlaufene Werte wird Status **zensiert** ausgegeben, nie „genau null“. Mathematisches „nichtstrikt“ wird aus der analytischen Struktur, nicht aus bloßem Rauschen abgeleitet.

**A4 (separate Q-Referenz):** Für Q stimmen numerische Daten gegen **endlichen-Ring-Fourierwert** innerhalb A3-Toleranz überein, einschließlich Normierung \(\sum_r p_L(r,t)=1\) bis zur dokumentierten Gleitkommatoleranz. Die Differenz zum Bessel-Limes wird getrennt berichtet.

**A5 (Shortcut):** Mit N2 muss eine frühe Fernantwort an r_star nachweisbar sein und gegen unabhängige Referenz (direkte kurze-Zeit-Taylorentwicklung oder separate Diagonalisierung) überprüft werden. Diese Antwort darf nicht als „Emergenz von Nichtlokalität“ beschrieben werden: die Kopplung wurde gesetzt.

**A6 (Schwellen):** Für alle drei Schwellen r_eta(t) tabellieren oder „undefiniert“ ausgeben. Keine unzulässige Rückinterpretation der gemessenen Front als strikte Supportgrenze. Varianten mit unterschiedlichen Schwellen oder Messrauschen müssen als voneinander getrennte Beobachtungsprotokolle veröffentlicht werden.

**A7 (Holdout und Unsicherheit):** A1–A4 ohne Retuning auf Holdout bestätigen. Deterministische Systeme erhalten numerische Fehlerbudgets, keine erfundenen Konfidenzintervalle. Optionales Messrauschen: 20 **unabhängige** Realisationen pro sigma/Schwelle, deskriptive Detektionsraten plus Unsicherheit aus unabhängigen Realisationen (nicht aus abhängigem Zeit-/Raum-Sampling).

**Hauptentscheidung:** Wenn A1–A4 nicht erfüllt sind, ist die Metrik **nicht validiert**; keine physikalischen Schlussfolgerungen. Wenn A5–A7 scheitern, ist insbesondere die Modellvergleichs-/Entscheidungsfähigkeit **nicht freigegeben**; ein partieller Erfolg als Referenzkalibrierung ist zulässig, aber nur mit expliziten Grenzen. **Missverstandene „Lichtkegel“ sind ein Stop-Signal**, keine Gelegenheit zur nachträglichen Anpassung von Parametern.

**H2-Auswertung:** Bericht über Variation der Detektionsfront mit η, Rauschen und Zeitfenster, *ohne vorauszusetzen, dass eine bestimmte numerische Frontgröße auftreten muss*. Scheint das Verfahren trotz bekannter positiver Analytik-Tails eine strikte Grenze zu „messen“, wird diese Fehlklassifikation aufgezeigt; gelingt durch gute Präzision keine Fehlklassifikation, ist das ebenfalls ein valides Negativergebnis der H2-Diagnostik.

## 7. Numerische Unsicherheit und Reproduzierbarkeit

Im Bericht unbedingt getrennt ausweisen:
1. **Mathematische** Klassifikation für ein vollständig spezifiziertes Modell.
2. Numerische Gleitkomma-/Unterlaufgrenze, quadrature/Fourier-Restfehler.
3. Endliche Ringgröße, periodische Wege und Interferenznullstellen.
4. Abhängigkeit des Messverfahrens von η, x-/t-Fenster und Rauschen.
5. Unvollständigkeit eines einzigen Eingriff-Zeugen gegenüber der maximal möglichen Kommunikation.
6. Zugrunde gelegte Metrik und Zeitdefinition: beide gesetzt, nicht hergeleitet.

Jeder Datenpunkt einschließlich negativem, zensiertem und fehlerhaftem Ergebnis bleibt im Ergebnismanifest erhalten. Kein Extrapolieren von Nullmessungen zu einem universellen Geschwindigkeitssatz.

**Späteres Run-Manifest (Pflichtfelder):** Protokollversion + geprüfter Protokoll-Commit, ausführender Commit, Zeit UTC, Versions-/Betriebsumgebung, Modell, Abstandsmetrik, Zeiteinheit, Hamiltonian/PDE/Update, Anfangs-/Kontrollzustand, Observable, Kopplung, L, x-/t-Gitter, Seeds und Rauschdefinition, Schwellwerte, Referenzformel, numerische Toleranzen, Messdaten-Hash, CPU-/RAM-/Laufzeit, Kennzeichnung train/holdout, Abweichungen vom Protokoll. CSV-Spalten mindestens Modell, Phase, L, r, t, S, analytische Referenz, Fehler, precision_status, η, detektionsstatus. Auch negative Auswertungen erhalten.

**Computebudget für spätere genehmigte Iteration, nicht bereits gemessen:** pro experimentellem Job maximal 0,5 vCPU, 1,5 GiB RAM, 30 Minuten Wall-Time (Soft-Stop 25 Minuten), vorzugsweise <100 MiB Ergebnisartefakte. Auf der 4-GB/2-vCPU-Lightsail-Instanz **nicht parallel** zu beeinträchtigender Ising-/Produktionslast. Vor Cloud-Ausführung lokaler Test/Sanity-Check, Freigabe und Code-Review erforderlich.

**Spätere Implementierung, aber nicht Gegenstand dieses PR:** eigenes isoliertes Python-Modul mit vier Referenzsolvern (d'Alembert, stabilisierter Wärmekernel, CA, Quanten-Fourier/sparse) und gesonderten Nullkontrollen; pytest gegen Analytik, klarer Held-out-Prozess. Weder Ising-Sampler noch bestehende Deployment-/Cron-Dateien ändern.

## 8. Möglicher Lean-4-Satz (nur Spezifikation, NICHT bewiesen)

**Proposition:** Sei G ein endlicher Graph. Zwei Anfangszustände unterscheiden sich nur auf A. Ein synchrones Update F an Knoten v hängt ausschließlich von Zuständen in der Radius-R-Nachbarschaft von v ab. Dann können sich die Zustände nach n Updates nur in der nR-Nachbarschaft von A unterscheiden.

**Beweisidee:** Induktion über n, Dreiecksungleichung für Graphdistanz / Erweiterung der Abhängigkeitsmenge pro Schritt. Zuerst mit dem CA-Ring und R=1 als Lean-Modell formalisieren, dann gegebenenfalls abstrahieren. Ein erfolgreicher Lean-Beweis ist ein Satz **über vorausgesetzte Lokalität**, nicht über Naturkonstanten.

## 9. Grenzen, Freigabe und Handoff

- **Nicht gemessen:** Es wurden keine Daten erzeugt, keine Konfidenzintervalle berechnet und kein Lean-Beweis implementiert.
- **Bereits bekannt [mathematisch]:** W und CA haben bei genannten Voraussetzungen endlichen Support; H hat positiven Kernel; Q-Entwicklung hat Bessel-/Fourier-Referenz und schwache Fernamplituden.
- **Offen [methodisch]:** Ob die vorgeschlagene Software-/Interpretationspipeline unterschiedliche mathematische Aussagen robust auseinanderhält.
- **Nicht behauptbar:** emergente Raumdimension, universelle Lichtgeschwindigkeit, vollständige Lorentzsymmetrie, Äquivalenz der Modellontologien.
- **Ising-Deconfliction:** PRs zu Ising-Kalibrierung weiterlaufen lassen. Dieses Dokument geht ausschließlich in einen eigenen Dokumentations-PR, ohne gemeinsame Dateien mit laufenden Ising-Änderungen anzufassen. RESEARCH_STATE erst konsolidieren, wenn die parallel offenen Forschungs-/Governance-PRs reviewed und gemergt sind.
- **Nächster Freigabeschritt:** unabhängige Begutachtung des Operationalisierungs- und Quanteneingriffsbegriffs; anschließend separates kleines Code-PR und isolierte minimale Analytik-Tests **nach** Ising-Gate.

### Zentrale wissenschaftliche Quellen

- Lieb & Robinson (1972), *The finite group velocity of quantum spin systems*, [DOI](https://doi.org/10.1007/BF01645779): ursprünglicher Lokalitäts-/Bound-Satz.
- Nachtergaele & Sims (2006), *Lieb-Robinson bounds and the exponential clustering theorem*, [DOI](https://doi.org/10.1007/s00220-006-1556-1): strenge Bounds unter Annahmen.
- Wilming & Werner (2022), *Lieb-Robinson bounds imply locality of interactions*, [DOI](https://doi.org/10.1103/PhysRevB.105.125101): inverse Beziehung, keine voraussetzungsfreie Emergenz.
- Farhi & Gutmann (1998), *Quantum computation and decision trees*, [DOI](https://doi.org/10.1103/PhysRevA.58.915): kontinuierlicher Quanten-Walk.
- Gilding & Kersner (1996), *The characterization of reaction-convection-diffusion processes by travelling waves*, [DOI](https://doi.org/10.1006/jdeq.1996.0002): mathematische Unterscheidung von Diffusions-Supporttypen.
- Schumacher & Werner (2004), *Reversible quantum cellular automata*, [arXiv](https://arxiv.org/abs/quant-ph/0405174): strikte lokal definierte diskrete Kausalgrenze als Modellannahme.

Siehe [Literaturbericht PR #8](https://github.com/shaden7/emergence-lab/pull/8) für weiterführende Theorievergleiche und offene Probleme.
