---
title: Implementation eines verifizierbaren paarweisen Sequenzalinierers auf Basis eines gemischt-ganzzahligen Optimierungsproblems
author:
  - Fynn Freyer
date: 12.08.2024
aliases:
  - Bachelorarbeit
  - Bachelor's Thesis
tags:
  - Uni
  - Bachelorarbeit
created: 2024-08-12
include-entry: docs
lang: de-DE
abstract: |

    ```{=latex}
    \setlength{\parindent}{15pt}
    \setlength{\parskip}{1em}
    \pagenumbering{roman}
    \setcounter{page}{1}
    ```

    Die vorliegende Arbeit behandelt das paarweise optimale globale Sequenzalinierungsproblem im Allgemeinen und die folgenden Fragen im Speziellen:
    
    1. Wie lässt sich Sequenzalinierung als lineares, gemischt-ganzzahliges Optimierungsproblem darstellen?
    2. Mit welchen Methoden kann das aufgestellte Modell gelöst werden?
    3. Wie können diese Methoden in einem Computerprogramm umgesetzt werden?
    4. Wie kann die Korrektheit eines auf Basis des gewählten Ansatzes implementierten  
       Softwaresystems verifiziert werden?
    
    Die Beantwortung dieser Fragen zielt darauf ab, anhand eines praktischen Beispiels zu erforschen, wie qualitativ hochwertige Software gebaut werden kann.
    Insbesondere, inwiefern die Wahl einer nicht klassischen Formulierung bereits gelöster Probleme bei der Modellierung sinnvoll ist und welche Relevanz Korrektheit für das Software-Engineering hat bzw. ob es möglich ist, nachweislich fehlerfreie Programme zu schreiben und wie nützlich dieser Anspruch ist.
    
    Dazu wurde zunächst ein Modell vorgestellt, welches Sequenzalinierung als mathematisches Optimierungsproblem formuliert.
    Daraufhin wurde ein Ansatz entwickelt, um dieses Modell zu lösen und die Lösung in der Programmiersprache Haskell zu implementieren.
    Zuletzt wurde die Korrektheit der Implementierung verifiziert.
    
    Bei der Betrachtung möglicher Lösungsansätze weist die Arbeit einen Zusammenhang zwischen dem vorgestellten Modell und dem klassischen Algorithmus zur globalen Sequenzalinierung von Needleman und Wunsch nach.
    Da die Überführung des Optimierungsproblems in den Needleman-Wunsch-Algorithmus eine methodische Schwäche aufweist, lässt sich die Isomorphie beider Vorgehensarten jedoch nicht eindeutig nachweisen.
    In der Diskussion wurde daraufhin ein Ansatz entwickelt, um die identifizierte Komplikation zu beheben.
    
    Dass das implementierte Programm, trotz nachgewiesener Korrektheit, signifikante Probleme aufweist, lässt darauf schließen, dass Korrektheitsbeweise zwar ein nützliches Werkzeug für Programmierer darstellen, aber ausführliche Tests und andere Praktiken der analytischen Qualitätssicherung nicht ersetzen können.
    
    Korrektheit ist nur *eine* der notwendigen Voraussetzungen, um nutzbare und qualitativ hochwertige Software zu produzieren.
    
    Der im Zusammenhang mit der Beweisführung aufgetretene Aufwand legt darüber hinaus den Schluss nahe, dass es vernünftig ist, Beweise auf klar abgrenzbare Systemkomponenten mit kritischer Funktionalität und klarer Spezifikation zu beschränken.

    ```{=latex}
    \newpage

    \makebox[\textwidth][c]{\hspace*{-8em}\textbf{Danksagung}}
    \vspace*{0.05\textheight}

    \setlength{\parindent}{0pt}
    \setlength{\parskip}{2em}
    ```

    Gott sei Dank, dass es endlich vorbei ist.
    
    Außerdem gilt mein Dank allen Dozenten, von denen ich interessante Dinge lernen durfte, allen Autoren die gute Bücher geschrieben haben, allen Kommilitonen die mir nicht auf den Nerv gegangen sind und allen Verwandten, Freunden und Bekannten die mich unterstützt haben.

    \vspace*{0.05\textheight}

    > Most people are fools, most authority is malignant, God does not exist, and everything is wrong.
    > 
    > -- Ted Nelson

---

```{=latex}
\listoffigures

\newpage
\pagenumbering{arabic}
\setcounter{page}{1}
```

!include 01_Einleitung.md

!include 02_Material_und_Methoden.md

!include 03_Durchfuehrung_und_Ergebnisse.md

!include 04_Diskussion.md

!include 05_Fazit.md

# Quellen

::: {#refs}

:::

```{=latex}
\newpage
\thispagestyle{affidavit}
\vspace*{0.2\textheight}
```

Hiermit versichere ich an Eides statt durch meine Unterschrift, dass

\vspace{3cm}

- ich die vorliegende wissenschaftliche Arbeit selbständig und ohne unerlaubte Hilfe angefertigt habe,
- ich andere als die angegebenen Quellen und Hilfsmittel nicht benutzt habe,
- ich die den benutzten Quellen wörtlich oder inhaltlich entnommenen Stellen als solche kenntlich gemacht habe und dass
- die Arbeit in gleicher oder ähnlicher Form noch keiner anderen Prüfbehörde vorgelegen hat.

```{=latex}
\vspace{3cm}

Berlin, den 12.08.2024
\vspace{1ex}
\hfill
\begin{minipage}{6cm}
    \mbox{\includegraphics[height=1.4cm]{signature}}%
    \vspace{-5pt}
    \hrule
    \begin{flushleft}
        \vspace{5pt}
        Fynn Freyer \\
    \end{flushleft}
\end{minipage}
``` 
