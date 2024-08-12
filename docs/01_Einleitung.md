---
title: Einleitung
---

# Einleitung

Die vorliegende Arbeit untersucht das Problem der optimalen globalen Sequenzalinierung, Analogien zwischen verschiedenen Darstellungsformen dieses Problems und die Verifikation von Softwaresystemen.

## Hintergrund

Sequenzalinierung wird in der Biologie genutzt, um die Ähnlichkeit zwischen verschiedenen DNA- und Proteinsequenzen zu bestimmen.
Dadurch können z. B. konservierte Abschnitte identifiziert und Verwandtschaftsverhältnisse abgeschätzt werden.

### Sequenzalinierung als Optimierungsproblem

Sequenzalinierung kann als Entscheidungsproblem interpretiert werden, bei dem Symbole einer Sequenz entweder einem Symbol der anderen Sequenz oder einer Lücke zugewiesen werden.

Es existieren viele Ansätze, um Entscheidungsprobleme zu lösen.
Das Feld der mathematischen Optimierung stellt verschiedene Möglichkeiten und Verfahren zur Verfügung, um solche Probleme aufzustellen und optimale Lösungen für sie zu bestimmen.

Insbesondere ist das Problem der optimalen globalen Sequenzalinierung ein bereits seit 1970 durch den klassischen Algorithmus von Needleman und Wunsch gelöstes Problem. [@nw70]
Dieser verwendet Methoden der dynamischen Programmierung, um eine Rekursionsbeziehung zwischen Teilalignments der betrachteten Sequenzen zu formulieren, welche Optimalität garantiert.

Alternativ kann das Alinierungsproblem aber auch als Optimierungsproblem mit geschlossener Formel dargestellt werden, bei dem Sequenzsymbole einer Alignmenttabelle mit fester Größe zugewiesen werden.
Möglicherweise kann das aus einer solchen Formulierung resultierende Vokabular genutzt werden, um eine, im Vergleich zu traditionellen Ansätzen, leichtere mathematische Analyse durchzuführen.

### Korrektheit

Da Analyseergebnisse im medizinischen Bereich Therapieentscheidungen und damit indirekt den Gesundheitszustand von Patienten beeinflussen, ist die Richtigkeit der durchgeführten Analysen dort von besonderer Bedeutung.

Mithilfe von Sequenzalinierung kann bspw. das Vorhandensein bestimmter Resistenzmutationen bei einer HIV-Infektion festgestellt oder ausgeschlossen werden.
Auf Grundlage dieser Informationen entscheiden Ärzte, mit welchen Medikamenten Patienten behandelt werden.
Da diese Therapieentscheidungen direkten Einfluss auf den Therapieerfolg haben, ist es von großer Bedeutung, dass die Alinierung korrekt durchgeführt wurde.

Wenn wir in der Informatik von *Korrektheit* sprechen, meinen wir, dass ein Programm seine zugrundeliegende Spezifikation einhält und die Überprüfung der Korrektheit heißt *Verifikation*.

In der Praxis werden verschiedene Methoden genutzt, um Programme zu verifizieren.
Eine typische Herangehensweise ist das Testen von Software.

> [P]rogram testing can be a very effective way to show the presence of bugs, but is hopelessly inadequate for showing their absence.
> The only effective way to raise the confidence level of a program significantly is to give a convincing proof of its correctness.
>
>  -- Edsger W. Dijkstra [@humble_programmer]

Dieses Zitat von Dijkstra zeigt ein fundamentales Problem mit diesem Ansatz auf.

Tests können nur die Abwesenheit von unerwünschtem Verhalten nachweisen.
Aus dem Vorhandensein von Tests und dem erfolgreichen Durchlaufen dieser folgt aber nicht logisch zwingend, dass sich das Programm in allen Situationen richtig verhält.

Dijkstra erwähnt als Alternative, die dieses Problem umgeht, den Korrektheitsbeweis.
Man spricht hier auch von *formaler* Verifikation.

Bei der formalen Verifikation wird ein mathematisches Modell des Programms aufgestellt und analysiert.
Dabei soll gezeigt werden, dass durch die Ausführung eines Programms unter bestimmten Vorbedingungen die spezifizierten Nachbedingungen und Invarianten folgen müssen.

Aufgrund des Stellenwerts von Korrektheit im medizinischen Bereich im Allgemeinen und bei der Sequenzalinierung im Besonderen, kann formale Verifikation bei der Entwicklung von Software für diese Anwendungsbereiche eine wichtige Rolle spielen.

## Problemstellung

Aus dem beschriebenen Hintergrund ergeben sich die folgenden Forschungsfragen:

1. Wie lässt sich Sequenzalinierung als lineares, gemischt-ganzzahliges Optimierungsproblem darstellen?
2. Mit welchen Methoden kann das aufgestellte Modell gelöst werden?
3. Wie können diese Methoden in einem Computerprogramm umgesetzt werden?
4. Wie kann die Korrektheit eines auf Basis der identifizierten Lösungsmethoden implementierten Softwaresystems verifiziert werden?
5. Welche Relevanz hat Korrektheit beim Bau qualitativ hochwertiger Software?
6. Bietet eine nicht klassische Formulierung des Alignmentproblems Vorteile?

## Aufbau

Die Arbeit besteht aus einem Materialteil, einem Durchführungs- und Ergebnisteil, der Diskussion der Ergebnisse und einem Fazit.

Im Materialteil stellen wir die notwendigen Grundlagen vor, um die Arbeit im Durchführungsteil zu verstehen.

Der Hauptteil ist in vier Sektionen gegliedert.

1. Zunächst wird ein Modell für die Sequenzalinierung als lineares, gemischt-ganzzahliges Optimierungsproblem vorgestellt.
2. Darauf aufbauend wird ein Ansatz entwickelt, um das dargestellte Modell zu lösen.
3. Auf Grundlage des entwickelten Lösungsansatzes wird ein Softwaresystem implementiert.
4. Durch formale Verifikation wird die Korrektheit des Systems nachgewiesen.

An den Hauptteil anschließend wird die Bedeutung der erzielten Ergebnisse diskutiert und sowohl die Argumentation im Lösungsansatz als auch die Implementation auf Schwächen untersucht.
