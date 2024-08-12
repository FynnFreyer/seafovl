---
title: Sequenzalinierung als Optimierungsproblem
---

# Sequenzalinierung als Optimierungsproblem

In dieser Sektion entwickeln wir, basierend auf @mc_allister07, ein mathematisches Modell welches Sequenzalinierung als gemischt-ganzzahliges Optimierungsproblem (*Mixed Integer Linear Program* oder **MILP**) darstellt.

Da das Modell auf zuvor publizierter Arbeit basiert, wird auf ausführliche Beweise der Korrektheit verzichtet.
Die Berechnung der Kosten für Mismatches und Gaps wurde vereinfacht und Notation benutzt, die an die Arbeit von Althaus et al. in @althaus05 angelehnt ist.

## Templates {#1_2_3_templates}

Die zentrale Struktur, unseres Modells ist das "Template".
Das Alignment einer Menge verschiedener Sequenzen $S = \{s^1, \dots, s^{|S|}\}$ wird durch eine Templatematrix $T$, bestehend aus $|S|$ Zeilen und $K$ Spalten, angegeben.

:::{#interpretation-template-matrix}
Hierbei werden jeder Zeile $m$ des Templates Symbole aus der entsprechenden Sequenz $s^m$, oder Gaps zugewiesen.

Beim Befüllen des Templates entsteht eine Anordnung, bei der die zueinander gehörigen Symbole verschiedener Sequenzen jeweils in derselben Spalte $k$ stehen.

$$
\label{template-matrix}
(t^m_k) = T
\qquad
t^m_k = s^m_i, \text{ mit unbekanntem } i
$$

Aufgrund des Zusammenhangs zwischen Zeile $m$ und Sequenz $s^m$, stellen wir den Zeilenindex für Templatematrizen hoch und sprechen von $t^m$ als dem "Alignment der Sequenz $s^m$", oder, je nach Kontext, von $t^m_k$ oder $t_k$ als der "Position" $k$ im Alignment.
:::

**Alignmentalphabet**

Für Sequenzen über einem Alphabet $\Sigma$ werden Lücken im Alignment durch ein spezielles Symbol[^gap_symbol] $c_\text{gap} \notin \Sigma$ gekennzeichnet.
Daraus folgt, dass $\bar \Sigma = \Sigma \cup \{ c_\text{gap} \}$ das Alphabet ist, über dem Alignments definiert sind, also $T \in \bar \Sigma^{|S| \times K}$.

[^gap_symbol]: Üblicherweise $c_\text{gap} = \mathrm{-}$.

**Templatelängen** entsprechen der Anzahl von Spalten des Templates.

Damit wir die Templatelänge $K$ bestimmen können, muss eine maximale Anzahl erlaubter Gaps $\mathfrak{g}_\text{max} \in \mathbb{N}$ festgelegt sein.
Dann ergibt sich $K$ als Summe von $\mathfrak{g}_\text{max}$ und der Länge der längsten Sequenz.

$$
\label{template-length}
K = \max \big\{|s| \mathrel{\big|} s \in S \big\} + \mathfrak{g}_\text{max}
$$

::: {#template_example}
:::: example
Seien bspw. zwei Sequenzen $s^1 = \text{AGTAC}$ und $s^2 = \text{ATGC}$ über dem Alphabet $\Sigma = \{\mathrm{A}, \mathrm{C}, \mathrm{G}, \mathrm{T}\}$ gegeben, das Gapsymbol als $c_\text{gap} = \mathrm{-}$ definiert und höchstens ein Gap in der längsten Sequenz erlaubt, also $\mathfrak{g}_\text{max} = 1$.

In diesem Fall wäre das Alignmentalphabet $\bar \Sigma$ durch die Menge $\{\mathrm{A}, \mathrm{C}, \mathrm{G}, \mathrm{T}, \mathrm{-}\}$  gegeben und die Templatelänge wäre $K = \mathfrak{g}_\text{max} + |s^1| = 6$.

Ein mögliches Alignment der Sequenzen wäre das folgende:

$$
T = \begin{array}{c|c|c|c|c|c}
    \mathrm{A} & \mathrm{G} & \mathrm{T} & \mathrm{A} & \mathrm{C} & \mathrm{-} \\
    \hline
    \mathrm{A} & \mathrm{-} & \mathrm{T} & \mathrm{G} & \mathrm{C} & \mathrm{-} \\
\end{array}
$$

::::
:::

## Problemformulierung {#1_3_problem_statement}

Seien $S = \{s^1, s^2\}$ die betrachteten Sequenzen, mit $|s^1| = M, |s^2| = N$ wobei o.b.d.A. gelte, dass $M \leq N$, sei $\mathfrak{g}_\text{max}$ die erlaubte Anzahl an Gaps und sei $T$ ein Template der entsprechenden Länge $K$.
Wir möchten nun $T$ mit Sequenzsymbolen und Gaps befüllen, sodass wir ein optimales globales Alignment erhalten.

Dabei müssen wir **jedes Sequenzsymbol**, in der **richtigen Reihenfolge** und an **genau einer** Position im Template zuweisen.
Positionen, die nicht mit Sequenzsymbolen befüllt wurden, werden mit dem Gapsymbol versehen.

Entsprechend [dem üblichen Vorgehen bei der Formulierungsproblemen](#formulating-ip), formulieren wir notwendige Variablen, Beschränkungen und eine Zielfunktion für das Alignmentproblem.
Dabei versuchen wir anschaulich zusammenzufassen und zu interpretieren.

### Variablen {#1_3_1_variables}

Um ein Template zu befüllen, muss bekannt sein welchen Stellen im Template die Symbole der zu alinierenden Sequenzen zugewiesen werden sollen.
Dabei handelt es sich um eine Erweiterung des klassischen Zuordnungsproblems.[^assignment_problem]

[^assignment_problem]: Für eine allgemeine Diskussion des Zuordnungsproblems vgl. @wolsey [pp. 5-6].

#### Zuweisungen

Da es sinnlos ein Symbol "teilweise" zuzuweisen, sind Zuweisung also offensichtlich binär, d.h. die Zuweisungsvariablen liegen in $\mathbb{B}$.

Um zu kodieren, ob ein Sequenzsymbol $s^m_i$ einer bestimmten Templateposition $t^m_k$ zugewiesen wurde, müssen $m, i$ und $k$ einbezogen werden.
Wir benötigen eine Variable für jede Kombination von Sequenz, Symbol- und Templateposition.

Sei $a^m_{ij} \in \mathbb{B}$ eine Zuweisungsvariable mit folgender Bedeutung:

$$
\label{assignment-var}
a^m_{ik} = \begin{cases}
    1, & s^m_i \text{ wird } T \text{ an Position } t^m_k \text{ zugewiesen } \\
    0, & \text{Andernfalls} \\
\end{cases}
$$

Alle Zuweisungsvariablen der Sequenz $s^m$, mit Länge $M$ in ein Template der Länge $K$ können zu einer "Zuweisungsmatrix" $\mathcal{A}^m \in \mathbb{B}^{M \times K}$ zusammengefasst werden.[^no_tensor]

$$
\label{assignment-mat}
\mathcal{A}^m = (a^m_{ik})
$$

[^no_tensor]: Aufgrund der potentiell unterschiedlichen Länge der betrachteten Sequenzen ist es nicht möglich die Zuweisungsmatrizen weiter zu einem einzelnen Tensor zusammenzufassen.

::: {#interpretation-assignment-matrix}
Die Zuweisungsmatrix $\mathcal{A}^m$ bezieht sich also eindeutig auf die Sequenz $s^m$.[^assignment_mat_high_index]

[^assignment_mat_high_index]: Was den hochgestellten Index erklärt.

Dabei haben Zeilen- und Spaltenindex eine klare Interpretation.
Der Zeilenindex $i$ entspricht der Position des Symbols in der Sequenz $s^m$ und der Spaltenindex $k$ der Spalte im Template $t^m_k$.
:::

::: {#assignment_mat_example}
:::: example
Die Befüllung des zuvor gegebenen [Beispieltemplates](#template_example) $\begin{smallmatrix} \mathrm{A} & \mathrm{G} & \mathrm{T} & \mathrm{A} & \mathrm{C} & \mathrm{-} \\ \mathrm{A} & \mathrm{-} & \mathrm{T} & \mathrm{G} & \mathrm{C} & \mathrm{-} \\ \end{smallmatrix}$ mit Sequenzsymbolen wird durch die folgenden Assignmentmatrizen dargestellt:

$$
\mathcal{A}^1 = \begin{pmatrix}
   1 & 0 & 0 & 0 & 0 & 0 \\
   0 & 1 & 0 & 0 & 0 & 0 \\
   0 & 0 & 1 & 0 & 0 & 0 \\
   0 & 0 & 0 & 1 & 0 & 0 \\
   0 & 0 & 0 & 0 & 1 & 0 \\
\end{pmatrix}
\qquad
\mathcal{A}^2 = \begin{pmatrix}
   1 & 0 & 0 & 0 & 0 & 0 \\
   0 & 0 & 1 & 0 & 0 & 0 \\
   0 & 0 & 0 & 1 & 0 & 0 \\
   0 & 0 & 0 & 0 & 1 & 0 \\
\end{pmatrix}
$$

Wobei der Zusammenhang zwischen $\mathcal{A}^1, s^1$ und $t^1$ folgendermaßen interpretiert werden kann:

$$
\begin{array}{c|cccccc}
     \mathcal{A}^1 & t^1_1 & t^1_2 & t^1_3 & t^1_4 & t^1_5 & t^1_6 \\
    \hline
    s^1_1 & 1 & 0 & 0 & 0 & 0 & 0 \\
    s^1_2 & 0 & 1 & 0 & 0 & 0 & 0 \\
    s^1_3 & 0 & 0 & 1 & 0 & 0 & 0 \\
    s^1_4 & 0 & 0 & 0 & 1 & 0 & 0 \\
    s^1_5 & 0 & 0 & 0 & 0 & 1 & 0 \\
\end{array}
$$

::::
:::

#### Gaps

Ebenso wollen wir die Menge $G$ aller Lücken im Alignment bestimmen.
Die Lücken im Alignment der Sequenz $s^m$ lassen sich in Zuweisungsmatrix $(a^m_{ik}) = \mathcal{A}^m \in \mathbb{B}^{N \times K}$ an den Nullspalten ablesen.

$$
G = \left\{i \;\middle|\; \sum_{k = 1}^K a^m_{ik} = 0\right\}
$$

Auf dieser Grundlage können wir eine Hilfsvariable $g^m_k$ einführen, die aussagt, ob Sequenz $s^m$ an Templateposition $t^m_k$ eine Lücke zugewiesen wurde.

$$
\label{gap-var}
g^m_k = \left[ \sum_{i = 1}^K a^m_{ik} = 0 \right]
$$

#### Zusammenfassung

Zu jeder Sequenz $s^m$, haben wir Zuordnungsvariablen in Form einer Zuweisungsmatrix $(a^m_{ik}) = \mathcal{A}^m$ definiert.
Auf Basis der Zuweisungsmatrix bestimmen wir die Stellen $g^m_k$ im Template, denen Lücken zugewiesen werden.

### Beschränkungen {#1_3_2_constraints}

Nun wollen wir die Bedingungen festlegen, welchen Alignments genügen müssen, damit wir sie als sinnvoll erachten.
Bspw. ist es sinnlos, Symbole einer Sequenz mehrfach, oder in ungeordneter Reihenfolge, zuzuweisen.

Es ist klar, dass bestimmte Zuweisungen von Symbolen keinen Sinn ergeben.
Dies können wir als Beschränkung der Zuweisungsmatrizen $\mathcal{A}$ formulieren.

#### Nutzung der Symbole {#constraint-assignment-matrix-rows}

Wir möchten weder erlauben, dass ein Symbol mehrfach zugewiesen wird, noch dass es gar nicht zugewiesen wird.
Jedes Symbol soll also genau einmal zugewiesen werden.

Wir erinnern uns an die [Interpretation der Zuweisungsmatrix](#interpretation-assignment-matrix) $(a^m_{ik}) = \mathcal{A}^m \in \mathbb{B}^{M \times K}$ und sehen, dass die **Summe von Zeile $i$** die **Anzahl aller Zuweisungen des Symbols** $s^m_i$ beschreibt.

$$
\label{constraint-rows}
\forall i \in J_{s^m}: \sum_{k = 1}^{K} a^m_{ik} = 1
$$

Da jedes Symbol genau einmal zugewiesen werden soll, muss jede Zeilensumme genau $1$ ergeben.

#### Belegung des Templates {#constraint-assignment-matrix-cols}

Weiterhin dürfen wir jeder Stelle im Template höchstens ein Sequenzsymbol zuweisen.
Da aber möglicherweise Lücken bestehen, ist es auch zulässig, einer bestimmten Stelle im Template kein Sequenzsymbol zuzuweisen.

Anhand der [Interpretation der Zuweisungsmatrix](#interpretation-assignment-matrix) $(a^m_{ik}) = \mathcal{A}^m \in \mathbb{B}^{M \times K}$ sehen wir, dass die **Summe von Spalte $k$** der **Anzahl aller** dem Template **an dieser Position zugewiesenen Sequenzsymbole** entspricht.

$$
\label{constraint-cols}
\forall k \in J_K: \sum_{i = 1}^M a^m_{ik} \leq 1
$$

Da jeder Stelle in $T$ höchstens ein Sequenzsymbol zugewiesen werden soll, folgt, dass alle Spaltensummen kleiner oder gleich $1$ sein müssen.

#### Reihenfolge der Symbole {#constraint-symbol-order}

Die Zuweisung der Sequenzsymbole zum Template muss auch an der Reihenfolge der Symbole in der Sequenz erhalten.
D. h. ein Symbol $s^m_i$ darf dem Template nicht nach dem Symbol $s^m_j$ zugewiesen werden, wenn $i < j$, bzw. für zwei beliebige Indizes $i, j$ von $s^m$ muss gelten, dass wenn $i < j$, die Position von $s^m_i$  in $T$, gegeben durch $k$, kleiner der Position von $s^m_j$ in $T$, gegeben durch $k'$, ist.

$$
\forall i, j \in J_N: i < j \implies k < k'
$$

Wenn also $i < j$ und $a^m_{ik} = 1$, dann muss für alle $k' \le k$ gelten, dass $a^m_{jk'} = 0$.
Umgekehrt muss auch, wenn $a^m_{jk'} = 1$, gelten, dass $a^m_{ik} = 0$.
Da höchstens einer der Terme den Wert $1$ annehmen kann, muss auch die Summe beider Zuweisungen unter $1$ bleiben.

$$
\forall i, j \in J_M, k, k' \in J_K: i < j \land k' \le k \implies a^m_{ik} + a^m_{jk'}  \le 1
$$

::: {#constraint_order_example}
:::: example
Was würde eine falsche Reihenfolge in der Praxis bedeuten?

Betrachten wir wieder die Sequenzen $s^1 = \text{AGTAC}$ und $s^2 = \text{ATGC}$ aus dem [vorigen Beispiel](#template_example) und das Alignment $T = \begin{smallmatrix} \mathrm{A} & \mathrm{G} & \mathrm{T} & \mathrm{A} & \mathrm{C} & \mathrm{-} \\ \mathrm{-} & \mathrm{G} & \mathrm{T} & \mathrm{A} & \mathrm{C} & \mathrm{-} \\ \end{smallmatrix}$ indem wir die Zuordnung der Symbole $s^2_1 = \mathrm{A}$, $s^2_2 = \mathrm{T}$ und $s^2_3 = \mathrm{G}$ in der falschen Reihenfolge vorgenommen haben.[^explicit_order_constraint_is_necessary]

[^explicit_order_constraint_is_necessary]: Wir sehen, dass $T$ offensichtlich ein besseres Alignment darstellt als die [zuvor besprochene](#assignment_mat_example) korrekt angeordnete Alternative $\begin{smallmatrix} \mathrm{A} & \mathrm{G} & \mathrm{T} & \mathrm{A} & \mathrm{C} & \mathrm{-} \\ \mathrm{A} & \mathrm{-} & \mathrm{T} & \mathrm{G} & \mathrm{C} & \mathrm{-} \\ \end{smallmatrix}$.
    Diese Ordnung verletzt keines der zuvor formulierten Kriterien, weswegen es notwendig ist solche Neuanordnungen explizit auszuschließen.

Die Zuordnungen von $s^2$ zu $T$ sind durch die folgende Zuweisungsmatrix gegeben.

$$
\mathcal{A}^2 = \begin{pmatrix}
   0 & 0 & 0 & 1 & 0 & 0 \\
   0 & 0 & 1 & 0 & 0 & 0 \\
   0 & 1 & 0 & 0 & 0 & 0 \\
   0 & 0 & 0 & 0 & 1 & 0 \\
\end{pmatrix}
$$

Wir sehen, dass die führenden Spalten nicht mehr geordnet sind, wodurch  $\mathcal{A}^2$ nicht in reduzierter Zeilen-Stufen-Form vorliegt.
::::
:::

##### Beziehung zu Nachfolger

Statt beliebige Sequenzindizes $i$ und $j$ zu vergleichen, reicht es, wenn wir die Beziehung zum direktem Nachfolger betrachten.
Der führende Eintrag in Zeile $i$ von $\mathcal{A}^m$ muss auf der linken Seite des führenden Eintrags in Spalte $i+1$ stehen.

Dies ist offensichtlich, lässt sich aber durch strukturelle Induktion über $\mathcal{A}^m$ explizit zeigen.

Sei $k_i$ der Index des führenden Eintrags[^validity_of_assumption_k_i_exists] von Spalte $i$, sodass $a^m_{ik_i} = 1$ und $a^m_{jk_i} = 0$ für $j \ne i$, dann erhalten Templatezuweisungen die Ordnung der Sequenz, g.d.w. aus $i < j$ folgt, dass $k_i < k_j$.[^validity_of_assumption_j_ne_i_implies_zero]

[^validity_of_assumption_k_i_exists]: Aus der [Bedingung für Zeilensummen](#constraint-assignment-matrix-rows) ergibt sich, dass ein solches $k_i$ existieren muss.
[^validity_of_assumption_j_ne_i_implies_zero]: Aus $a^m_{ik_i} = 1$ i.V.m. der [Bedingung für Spaltensummen](#constraint-assignment-matrix-cols) ergibt sich $j \ne i \implies a^m_{jk_i} = 0$.

$$
\forall i, j \in J_M: i < j \implies k_i < k_j
$$

Dies ist äquivalent zu der Aussage, dass $(k_i)_{i \in J_M}$ streng monoton steigt.

Als Induktionsanker sehen wir, dass leere Folgen und solche mit Länge $1$ immer geordnet sind.

Nehmen wir jetzt als Induktionshypothese an, dass die Teilfolge bis Index $m$ geordnet ist.
Wenn wir einen Eintrag $k_n$ hinzufügen, der größer als $k_m$ ist, dann folgt aus der I.H. und der Transitivität von $<$, dass $k_n$ auch größer als alle $k_l$ mit $l < m$ ist und somit, dass auch die Folge bis $n$ geordnet ist. $\blacksquare$

Damit bekommen wir die folgende Bedingung.

$$
\label{constraint-order}
\forall i, i+1 \in J_M, k, k' \in J_K, k' \le k: a^m_{ik} + a^m_{i + 1, k'} \leq 1
$$

::: aside
Wir [erinnern uns](#constraint-assignment-matrix-rows), dass für $(a^m_{ik}) = \mathcal{A}^m \in \mathbb{B}^{M \times K}$ die **Summe der Zeile** $i$ der Zuweisungsmatrix der **Anzahl der Zuweisungen** des Sequenzsymbols $s^m_i$ entspricht, [und dass](#interpretation-assignment-matrix) die **Spalte** $k$ die **Position** $t^m_k$ **im Template** codiert.
Daher können wir die **Summe** der Elemente in Zeile $i$, **bis Spalte $k$ als Anzahl an Zuweisungen** von $s^m_i$ **vor der Position** $t^m_k$ interpretieren.

Da wir voraussetzen, dass jedes Sequenzsymbol genau einmal zugewiesen wird kann die Anzahl aller Zuweisungen von $s^m_{i+1}$ vor $k$ höchstens $1$ sein.
Die Summe aller solcher Zuweisungen entspricht dem Term $\sum_{k' = 1}^{k-1} a^m_{i+1, k'}$.
Wie zuvor, sehen wir, dass auch die Summe dieses Terms und $a^m_{ik}$ unter $1$ bleiben muss.

$$
\forall i, j \in J_M, k \in J_K: i < j \implies a^m_{ik} + \sum_{k' = 1}^{k-1} a^m_{i+1, k'} \le 1
$$

Dies wäre eine noch stärkere Bedingung als die zuvor formulierte.
:::

#### Zusammenfassung {#objective-function}

Wir haben verschiedene Beschränkungen für unsere Variablen formuliert.

- (eq:constraint-rows) Jedes Symbol der Sequenz $s^m$ muss zugewiesen werden.
- (eq:constraint-cols) Jeder Stelle $t_k$ im Template darf höchstens ein Symbol der Sequenz $s^m$ zugewiesen werden.
- (eq:constraint-order) Die Sequenzsymbole in $s^m$ müssen in der richtigen Reihenfolge zugewiesen werden.

Diese Beschränkungen geben unseren Daten Struktur.
Fassen wir nochmal kurz zusammen:

Die Assignmentmatrizen $\mathcal{A}^1$ und $\mathcal{A}^2$ haben pro Zeile genau einen und pro Spalte höchstens einen Eintrag ungleich Null.
Darüber hinaus haben $\mathcal{A}^1$ und $\mathcal{A}^2$ reduzierte Zeilenstufenform.

Außerdem gibt es keine Beschränkungen, die sich auf mehrere Zuweisungsmatrizen gleichzeitig beziehen, d.h. sie sind sauber voneinander separierbar.

### Zielfunktion

Um ein *optimales* globales Alignment zu berechnen, muss ein Bewertungskriterium für die Güte von Alignments existieren.

#### Kostenmodell

Zunächst wählen wir ein Kostenmodell, um anschließend eine darauf basierende Zielfunktion zu formulieren.

Im Rahmen dieser Arbeit verwenden wir eine flache Kostendarstellung, mit den drei Kostenfaktoren $w_\text{match}$, $w_\text{miss}$ und $w_\text{gap}$, welche für Matches, Mismatches und Gaps respektive gelten.

::: aside
Man kann auf Basis von $w_\text{match}$, $w_\text{miss}$ und $w_\text{gap}$ ohne großen Aufwand eine Substitutionsmatrix $W$ mit Einträgen für jedes Symbol $c_i \in \Sigma$ definieren.
In $W$ steht $w_\text{match}$ auf der Hauptdiagonale und $w_\text{miss}$ überall sonst.

$$
W = \begin{array}{c|ccccc}
        & c_\text{gap} & c_1 & c_2 & \dots & c_n \\
    \hline
    c_\text{gap} & 0 & w_\text{gap} & w_\text{gap} & \dots & w_\text{gap} \\
    c_1 & w_\text{gap} & w_\text{match} & w_\text{miss} & \dots & w_\text{miss} \\
    c_2 & w_\text{gap} & w_\text{miss} & w_\text{match} & \ddots & \vdots \\
    \vdots & \vdots & \vdots & \ddots & \ddots & w_\text{miss} \\
    c_n & w_\text{gap} & w_\text{miss} & \dots & w_\text{miss} & w_\text{match} \\
\end{array}
$$

Wir schreiben $w_{ik}$ wie in (eq:substitution-weight-mat).
:::

Für Leser mit Interesse an komplexeren Kostenmodellen sei erneut auf die Arbeit von McAllister et al. [@mc_allister07] verwiesen, die sowohl affine, als auch konkave Gapkosten im Rahmen einer MILP-Formulierung modelliert.

#### Substitutionskosten

Die totalen Substitutionskosten von $T$ entsprechen den Substitutionskosten aller Symbole  $s^1_i$ und $s^2_j$, die derselben Position $t_k$ zugewiesen wurden für alle Positionen.

Diese Zuweisungen sind durch die in (eq:assignment-var) formulierten Variablen bzw. den zusammengefassten Matrizen $\mathcal{A}^1$ und $\mathcal{A}^2$ kodiert.
Wenn sowohl $s^1_i$, als auch $s^2_j$ der Position $t_k$ zugewiesen wurden, dann gilt  $a^1_{ik} \cdot a^2_{jk} = 1$.[^algebraic_interpretation_and]

[^algebraic_interpretation_and]: Dies ist ein schönes Beispiel dafür, warum die Multiplikation die algebraische Interpretation des logischen UND ist.

Da die Multiplikation zweier Unbekannter zu einem nicht linearen Term führt, definieren wir eine Hilfsvariable $\phi_{ijk}$.[^tensor_phi]

 $$
\label{phi}
\phi_{ijk} = a^1_{ik} \cdot a^2_{jk}
$$

[^tensor_phi]: Wir könnten diese Hilfsvariable zu einem Tensor $(\phi_{ijk}) = \Phi \in \mathbb{B}^{M \times N \times K}$ zusammenfassen.

Dies ermöglicht es die Substitutionskosten als Summe über die Sequenz- und Templatepositionen darzustellen.

$$
\label{total-substitution-cost}
\sum_{i = 1}^M \sum_{j = 1}^N \sum_{k = 1}^{K} \left[ w_{ij} \cdot \phi_{ijk} \right]
$$

Wobei $w_{ij}$ wie in (eq:substitution-weight) definiert ist.

#### Gapkosten {#1_3_gapcost}

Gapkosten entstehen für alle Positionen, denen ein Gap bzw. kein Symbol zugewiesen wurde.
Diese sind durch die in (eq:gap-var) formulierte und von $\mathcal{A}^m$ abhängige Hilfsvariable $g^m_k$ gegeben.

::: {.info #motivation_gamma}
Eine naive Formulierung könnte auf der Frage aufbauen, ob das Sequenzalignment $t^1_k$ oder $t^2_k$ einen Gap an Stelle $k$ hat.
Das logische ODER kann algebraisch als $+$ dargestellt werden, was uns die Auswahl von Gaps mit $g^1_k + g^2_k$ ermöglicht.
Diese Variante würde folgendermaßen aussehen:

$$
\sum_{k = 1}^{K} w_\text{gap} \cdot (g^1_k + g^2_k)
$$

Die Formulierung ist u.a. deswegen naiv, da wir nicht über dem Feld $\mathbb{F}_2$ arbeiten und folglich $1 + 1 = 2$ anstatt $1$ ist.[^simple_count]
In diesem Ausdruck werden "beidseitige" Gaps also doppelt gezählt.

[^simple_count]: Auch ein einfaches Zählen von Doppelgaps wäre nicht perfekt, sollte bei sinnvoll gewählten Parametern für $w_\text{gap}$ und $w_\text{miss}$ allerdings nicht zu dem im Folgenden beschriebenen Fehlermodus führen.

Durch die Wahl von $\mathfrak{g}_\text{max}$, kann regelmäßig ein ungenutztes Kontingent an Gaps verbleiben, welches zu solchen beidseitigen Gaps führen kann, die aber keinen Einfluss auf das Alignment haben sollten.

In Kombination mit bestimmten Gewichten kann dies zu sinnlosen Ergebnissen führen.

:::: {#naive_gap_cost_example}
::::: example
Machen wir ein Beispiel mit $w_\text{match} = 0, w_\text{miss} = 2, w_\text{gap} = 3$.
Vergleichen wir nun $T_1 = \begin{smallmatrix} \mathrm{C} & \mathrm{-} \\ \mathrm{C} & \mathrm{-} \end{smallmatrix}$ und $T_2 = \begin{smallmatrix} \mathrm{-} & \mathrm{C} \\ \mathrm{C} & \mathrm{-} \end{smallmatrix}$.
Wir sehen intuitiv, dass $T_1$ das bessere Alignment ist, jedoch ergibt sich mit den Kosten für den doppelten Gap der Wert $6$.
Die beiden einzelnen Gaps in $T_2$ verursachen dieselben Kosten, weswegen diese naive Formulierung keinen Unterschied zwischen $T_1$ und $T_2$ machen würde.
:::::
::::
:::

Um das [beschriebene](#motivation_gamma) Problem doppelter Gapkosten zu vermeiden, führen wir die Hilfsvariable $\gamma_k$ ein.

$$
\label{gamma}
\gamma_k = |g^1_k - g^2_k|
$$

Diese entspricht einem logischen XODER (exklusives ODER) und gibt an, ob genau eine Sequenz einen Gap in Position $t_k$ besitzt.[^vector_gamma]

[^vector_gamma]: Diese können wir zu einem Vektor $\gamma \in \mathbb{B}^K$ zusammenfassen.

Die Summe der Gapkosten aller Positionen, denen genau ein Gap zugewiesen wurde ist durch folgenden Ausdruck gegeben:

$$
\label{total-gap-cost}
\sum_{k = 1}^K \left[ w_\text{gap} \cdot \gamma_k \right]
$$

#### Gesamtkosten

Man kann eine Zielfunktion $c'$ formulieren, deren Argumente die  Zuweisungsvariablen $a^1_{ik}$ und $a^2_{jk}$ darstellen.

Da diese allerdings nicht linear ist, nutzen wir stattdessen die von den Zuweisungsvariablen abgeleiteten $\phi_{ijk}$ und $\gamma_k$, um eine äquivalente[^equiv_goalfunc] Funktion $c$ zu formulieren.

[^equiv_goalfunc]: D.h. $c'(x') = c(x) \iff x' \implies x$.

Die Zielfunktion ist die Summe aller Substitutionskosten, die in (eq:total-substitution-cost) formuliert wurde und der Summe aller Gapkosten, die in (eq:total-gap-cost) formuliert wurde.

$$
\sum_{i = 1}^M \sum_{j = 1}^N \sum_{k = 1}^{K} \left[ w_{ij} \cdot \phi_{ijk} \right]
+
\sum_{k = 1}^{K} \left[ w_\text{gap} \cdot \gamma_k \right]
$$

Dies kann man äquivalent umformulieren.

$$
\label{objective}
\sum_{k = 1}^{K}
\left[
    w_\text{gap} \cdot \gamma_k +
    \left[
        \sum_{i = 1}^M \sum_{j = 1}^N w_{ij} \cdot \phi_{ijk}
    \right]
\right]
$$

### Gesamtdarstellung

Wenn (eq:objective) maximal ist, ist per Definition der Wert des durch die Eingaben kodierten Alignments maximal.

Somit können wir unser Optimierungsproblem $Z$, basierend auf den [Variablen](#1_3_1_variables), [Beschränkungen](#1_3_2_constraints) und der [Zielfunktion](#objective-function) darstellen.

$$
\label{milp-problem-equation}
Z = \max
    \sum_{k = 1}^K
    \left[
        w_\text{gap} \cdot \gamma_k
        \left[
            \sum_{i = 1}^M \sum_{j = 1}^N w_{ij} \cdot \phi_{ijk}
        \right]
    \right]
$$
