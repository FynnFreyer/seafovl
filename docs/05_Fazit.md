---
title: Fazit
---

# Fazit

Die Arbeit stellt ein MILP-Modell für das paarweise optimale globale Sequenzalinierungsproblem vor und zeigt, dass ein eindeutiger Zusammenhang zwischen diesem Modell und dem klassischen Algorithmus zur globalen Sequenzalinierung von Needleman und Wunsch existiert.
Auf Basis von NW ist eine Lösung für dieses Modell implementiert.
Zu guter Letzt wird für deren zentrale Komponenten die Konformität mit der aus dem Ansatz resultierenden Spezifikation aufgezeigt.

## Erkenntnisse

Die dargestellten Ergebnisse erlauben die Beantwortung der zu Beginn der Arbeit formulierten Forschungsfragen.

### Sequenzalinierung als lineares, gemischt-ganzzahliges Optimierungsproblem

In Rahmen dieser Arbeit hat sich gezeigt, dass das existierende Modell von McAllister et al. in [@mc_allister07] eine solide Grundlage bildet, auf der eine Darstellung von Sequenzalinierung als MILP aufbauen kann.
Zudem stellte sich heraus, dass eine, an die Arbeit von Althaus et al. angelehnte, Anpassung der Notation eine verständlichere Darstellung des Problems erlaubt. [@althaus05]

Mithilfe dieser angepassten Darstellung war es einfach die Formulierung der Entscheidungsvariablen bündig zu Matrizen zusammenzufassen, wodurch sich die Zusammenhänge im Modell besser herausarbeiten lassen.

### Lösung des MILP-Problems

Aufgrund des ermittelten Zusammenhangs zwischen dem MILP-Modell und NW lässt sich vermuten, dass eine angepasste NW-Formulierung geeignet ist, um das vorgestellte Modell zu lösen.
Infolge der erörterten methodischen Schwächen bei der Überführung des Modells kann diese Frage allerdings mit den Mitteln dieser Arbeit nicht mit hinreichender Sicherheit beantwortet werden.

### Umsetzung in ein Computerprogramm

Die Programmiersprache Haskell wurde gewählt, da ihre syntaktische Nähe zu mathematischer Notation und die aus ihrer funktionalen Natur resultierenden Eigenschaften sie einer formalen Verifikation leicht zugänglich machen.
Diese Wahl hat sich allerdings insoweit als problematisch erwiesen, als dieselben Eigenschaften das Schreiben von effizientem Code erschweren.

Die Freiheit von Nebeneffekten und der damit notwendig werdende Umgang mit Programmzuständen mithilfe von Monaden stellt für Einsteiger in die funktionale Programmierung eine hohe Hürde dar.
Außerdem schränkt die nicht-strikte Auswertung die Nachvollziehbarkeit des Speichermanagements ein.
Bei rekursiven Aufrufen ist für Neulinge häufig nicht direkt ersichtlich, in welchen Fällen der Garbage-Collector den Heap leert, um Speicher freizumachen und wann Werte unnötig im Speicher verweilen, weil die Auswertung erst stattfindet, sobald der Rekursionsanker erreicht wurde.

Die Performanceprobleme der erdachten Implementation offenbaren daher die Notwendigkeit kompetenter und mit dem funktionalen Paradigma vertrauter Programmierer.
Die geringe Verbreitung solcher Sprachen macht es aber aufwändig, solche zu finden.

### Formale Verifikation der Implementation

Aufgrund der Wahl der Programmiersprache reichten grundlegende Techniken, um die Korrektheit zentraler Komponenten des entwickelten Programms nachzuweisen.
Anderweitige Methoden als der simple Abgleich von Definitionen und strukturelle Induktion waren nicht notwendig.

Die leichte Verifizierbarkeit funktionaler Sprachen macht diese trotz der beschriebenen Nachteile zu einer realistischen Alternative gegenüber klassisch-imperativen Sprachen, gerade bei kritischen Systemen mit klarer Spezifikation.

### Relevanz von Korrektheit im Software-Engineering

Es liegt auf der Hand, dass Korrektheit ein notwendiges Kriterium ist, um gute Software zu produzieren.
Die trotz Verifikation identifizierten Schwächen in der Implementation machen allerdings deutlich, dass Korrektheit alleine nicht ausreicht, um nutzbare und qualitativ hochwertige Software zu produzieren.

Aufgrund der fundamentalen Probleme des reinen Testens von Programmen stellen Beweise trotzdem ein nützliches Werkzeug für Softwareingenieure dar.
Gerade bei kritischen Systemen bietet es sich an, bestimmte Kernkomponenten nicht nur zu testen, sondern diese zusätzlich einer formalen Verifikation zu unterziehen.

### Vorteile einer nicht-klassische Formulierung

Da der gewählte Lösungsansatz nicht auf dem gebildeten Modell selbst, sondern auf der Überführung in NW basiert, trat die erhoffte Vereinfachung des Verifikationsprozesses nicht ein.
Aus der Tatsache, dass dieser Vorteil nicht zustande kam, folgt allerdings nicht, dass die Nutzung alternativer Modelle zur Simplifikation der mathematischen Analyse im Allgemeinen unnütz ist.

Ein klarer Vorteil, der sich aus der Formulierung des MILP ergab, ist der dadurch entstehende Perspektivgewinn.
Beide Modelle bieten verschiedene Blickwinkel, die einander ergänzen und helfen, das Alinierungsproblem besser zu verstehen.

MILP bildet eine solide mathematische Grundlage mit definierten Eingabewerten, klar formulierten Beschränkungen für diese Eingaben und einer einfach handhabbaren, geschlossenen Formel, um die Qualität eines Alignments zu bestimmen.
Dabei ist es zuweilen schwer, gut verständliche Interpretationen für die im Rahmen von MILP formulierten Sachverhalte zu finden.

Die rekursive Natur von NW und die daraus resultierende Möglichkeit der kompakten und eleganten Formulierung machen es dagegen gut geeignet für intuitive Erklärungen.
Zusammenhänge lassen sich einfach anhand nachvollziehbarer Beispiele demonstrieren.
Andererseits sind die mathematischen Hintergründe bei NW nicht direkt ersichtlich und einem Laien kann es zunächst schwerfallen zu verstehen, wie NW das Alignmentproblem auf Teilschritte zurückführt.

Aufgrund des Zusammenhangs zwischen Matrix-Dimensionen und Sequenzen in NW kann die Forderung, dass die Anordnung der Sequenzsymbole bewahrt werden muss, durch die Beschränkung der Bewegungsrichtung auf diagonal, horizontal und vertikal dargestellt werden.
Dies ist nicht nur leichter verständlich als die Darstellung mit der im MILP-Modell aufgestellten Forderung (eq:constraint-symbol-order), sondern kann dank des anschaulichen Zusammenhangs auch deutlich leichter plausibilisiert werden.
Andererseits lässt sich die Problemformulierung mit dem Vokabular, das das MILP-Modell bietet, deutlich leichter auf höhere Dimensionen verallgemeinern.
NW nutzt eine verzweigte Rekursionsbeziehung, bei der pro zusätzlicher Sequenz ein rekursives Argument hinzukommt; dies erschwert die mathematische Analyse in höheren Dimensionen.

## Ausblick

Auf der Grundlage der gewonnenen Erkenntnisse lassen sich Themen und Fragestellungen für die weitergehende Forschung identifizieren.

### Feste Alignmentlängen

Die vorgestellte Argumentation für Isomorphie von MILP und NW erscheint schlüssig.
Allerdings liefert die vorliegende Arbeit keinen angepassten Algorithmus, der die fixe Länge produzierter Alignments garantiert.

Es wäre interessant, den in der Diskussion der Limitationen vorgestellten Ansatz für ein erweitertes Abbruchkriterium und eine darauf basierende Wahlfunktion für Kandidatenschritte präzise auszuformulieren.
Wenn sich aus der Anwendung der angepassten Kandidatenfunktion eine obere Schranke für Alignmentlängen ergibt, wäre die Isomorphie von MILP und NW gezeigt.

### Performanceanalyse

Die identifizierten Performanceprobleme sprechen für die Notwendigkeit einer eingehenden Analyse und möglichen Neuimplementierung bestimmter Programmteile.

Interessante Kandidaten für die Identifikation der verantwortlichen Störquellen sind einerseits die unnötigen Kopien bei der Befüllung der Matrix, welche höchstwahrscheinlich negative Auswirkungen auf die Ausführungszeit haben und andererseits der Backtrackingalgorithmus, der sowohl Ausführungszeit als auch Speichermanagement negativ beeinflusst.

### Computergestützte Verifikation

Zu Beginn der Arbeit wurde die Machbarkeit händischer Beweise deutlich über- und deren Fehleranfälligkeit deutlich unterschätzt.

Folgearbeiten könnten erforschen, inwieweit sich das dargestellte Modell in einem Beweisassistenten formulieren lässt, sowie ob und wie diese Formulierung für eine automatische Verifikation der Implementation genutzt werden kann.

### Erweiterung des Modells

Auch die in der Diskussion erörterten Ansätze zur Erweiterung des vorgestellten Modells auf das Problem multipler Sequenzalignments oder zur Nutzung einer anderen Art von Kostenfunktion können eine fruchtbare Grundlage für Folgearbeiten darstellen.
