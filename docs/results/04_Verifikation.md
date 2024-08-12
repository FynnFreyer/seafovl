---
title: Verifikation
---

# Verifikation

Wir werden im Folgenden die zentralen Bestandteile des implementierten Softwaresystems einer mathematischen Prüfung unterziehen.

## Grundlegende Definitionen

Rufen wir uns kurz die Definitionen grundlegender Datentypen und Funktionen in Erinnerung.

### Datentypen

Alle Berechnungen basieren in irgendeiner Art und Weise auf den zentralen Eckdaten des Alignmentproblems.
Dies sind die zu betrachtenden Sequenzen und deren Längen, die Anzahl erlaubter Gaps und das Gewicht von Substitutionen und Gaps.

Der Typ für Gewichte ist `Cost` und hat Felder für $w_\text{match}, w_\text{miss}$ und $w_\text{gap}$.

```haskell
-- | Record type for costs.
data Cost = Cost {w_match :: Int, w_miss :: Int, w_gap :: Int} deriving (Eq, Show)
```

Die Felder halten Werte in $\mathbb{Z}$.

Wir fassen alle relevanten Eckdaten, inklusive der Gewichte zu `AlnInfo` Werten zusammen, bzw. berestimmen sie im Falle der Sequenzlängen mit der `seqLengths` Funktion.

```haskell
-- | Record with key data of the alignment problem.
data AlnInfo = AlnInfo
  { g_max   :: Int
  , weights :: Cost
  , seqA    :: SeqArr
  , seqB    :: SeqArr
  } deriving (Eq, Show)

-- | Compute sequence lengths for an AlnInfo record.
seqLengths :: AlnInfo -> (Int, Int)
seqLengths AlnInfo {seqA = s1, seqB = s2} = (length s1, length s2)
```

Der `AlnInfo` Datentyp hat Felder für $\mathfrak{g}_\text{max}$, die Gewichte und die Sequenzen $s^1$ und $s^2$.

Als Hilfsfunktion um für die Sequenzen eines `AlnInfo` Wertes die Längen zu bestimmen, haben wir `seqLengths` definiert, welche das geordnete Paar $(|s^1|, |s^2|)$ produziert.

Die relevanten Datentypen im Zusammenhang mit Matrizen sind wie folgt definiert.

```haskell
-- | Matrix indices.
type MatIdx = (Int, Int)
-- | Path through a matrix.
type Path = [MatIdx]
-- | Steps are `MatIdx` tuples of the form `(origin, destination)`.
type Step = (MatIdx, MatIdx)
-- | Datatype to denote step directions.
data StepDirection = Diagonal | Horizontal | Vertical deriving Eq
-- | If defined, tuple of cell value and list of precursors.
type CellValue = Maybe (Int, [StepDirection])
-- | A Needleman-Wunsch matrix.
type NWMatrix = Matrix CellValue
```

### Grundlegende Funktionen

Betrachten wir auch ein paar grundlegende Funktionen, aus welchen wir die Hauptfunktionen des Programms komponieren.

#### Gewichte

Im Block [«weight»](#weight) haben wir Funktionen zum Umgang mit Gewichten definiert.

##### Substitutionskosten {#verification_substitution_weight}

Die Formel (eq:substitution-weight) gibt die Definition für $w_{ij}$ wie folgt.

$$
w_{ij} = \begin{cases}
    w_\text{match} & , s^1_i = s^2_j \\
    w_\text{miss} & , \text{Andernfalls} \\
\end{cases}
$$

Wir haben für Substitutionskosten die Funktion `substWeight` definiert, deren Eingaben die zu verwendenden Gewichte und die beiden Symbole $s^1_i$ und $s^2_j$ sind.

```haskell
-- | Calculate the weight of a substitution.
substWeight :: (Eq a) => Cost -> (a, a) -> Int
substWeight (Cost {w_match = match, w_miss = miss}) (s1, s2)
  | s1 == s2  = match
  | otherwise = miss
```

Wenn $s^1_i = s^2_j$, dann $w_\text{match}$ und sonst $w_\text{miss}$ entspricht genau der Definition von $w_{ij}$.

##### Schrittwerte {#verification_step_weight}

Nach (eq:naive-step-weight) ergibt sich der Wert eines Schrittes wie folgt.

$$
w(q_k) = \begin{cases}
    w_{ij}, & g \ne i \land h \ne j \\
    w_\text{gap}, & \text{Andernfalls} \\
\end{cases}
$$

Um $w(q_k)$ darzustellen, haben wir die Funktion `stepWeight` formuliert.

```haskell
-- | Calculate the weight of a step.
stepWeight :: AlnInfo -> Step -> Int
stepWeight (AlnInfo {weights = cost, seqA = s1, seqB = s2}) ((g, h), (i, j))
  | subst     = substWeight cost (s1 ! i, s2 ! j)
  | otherwise = w_gap cost
    where
      subst   =  i == g + 1
              && j == h + 1
```

Aus (eq:step-width) folgen $g \ne i \iff i = g + 1$ und $h \ne j \iff j = h + 1$.
Daher sehen wir, dass die mit $i = g + 1 \land j = h + 1$ gegebene Aussage `subst` äquivalent zu der ersten Bedingung in (eq:naive-step-weight) ist.
Wir haben außerdem [bereits gesehen](#verification_substitution_weight), dass `substWeight` eine akkurate Entsprechung für das Gewicht $w_{ij}$ einer Substitution ist.

Da wir, identisch zu $w(q_k)$, in allen sonstigen Fällen $w_\text{gap}$ zurückgeben, muss auch`stepWeight` (eq:naive-step-weight) entsprechen.

##### Schrittwertbestimmung {#verification_stepscore}

Wir arbeiten nicht direkt mit Zellwerten, sondern mit Werten von `ScoredStep`.
Um diese zu erzeugen, haben wir im [«max-helpers»](#max-helpers) Block die `stepScore` Funktion definiert.

```haskell
-- | Score a candidate step.
stepScore :: AlnInfo -> NWMatrix -> Step -> ScoredStep
stepScore info mat step@(candidate, cell) = (score, dir)
    where
      val   = getFrom mat candidate :: CellValue
      w_q   = stepWeight info step  :: Int
      score = fmap ((+w_q).fst) val :: CellScore
      dir   = fromStep step         :: StepDirection
```

Für den Kandidaten `candidate` mit Indizes $(g, h)$ binden wir den Wert $f_{gh}$ an den Namen `val`.

Als wir zuvor die Implementation von `stepWeight` [besprachen](#verification_step_weight), sahen wir, dass das Ergebnis von `stepWeight info` für den Schritt $q_k$ dem Schrittgewicht $w(q_k)$ entspricht.
Dieses binden wir an den Namen `w_q`.
Außerdem wandeln wir den übergebenen Schritt in einen `StepDirection` Wert um und benennen diesen mit `dir`.

Der Funktionswert von `stepScore` für einen Schritt $q$, entspricht dem Tupel $(w(q), \mathtt{dir})$, mit Gewicht und Richtung des Schritts.

#### Gaps

Wir müssen auch die Funktionen betrachten, welche wir nutzen um mit Lücken im Alignment umzugehen.

##### Gapzahlen

Die Gapzahl $\mathfrak{g}^x$ einer Sequenz $s^x$ ist in (eq:gapcounts) durch $\mathfrak{g}^x = \mathfrak{g}_\text{max} + (L-|s^x|)$ gegeben, wobei $L$ die Länge der längsten Sequenz bezeichnet.
Um unsere $\mathfrak{g}^x$ zu berechnen haben wir im [«type-aln-info»](#type-aln-info) Block `gapCounts` definiert.

```haskell
-- | Compute gap numbers for an AlnInfo record.
gapCounts :: AlnInfo -> (Int, Int)
gapCounts info@(AlnInfo {g_max = g})
  = let (m, n) = seqLengths info
         l     = max m n
    in  (g + (l - m), g + (l - n))
```

In der Definition von `gapCounts` binden wir die Sequenzlängen an die Namen `m` und `n` und bestimmen anschließend `l` als den größeren der beiden Werte.
Danach berechnen wir $\mathfrak{g}^1$ und $\mathfrak{g}^1$ als `g1 == g + (l - m)` bzw. `g2 == g + (l - n))`, wobei `g` unser $\mathfrak{g}_\text{max}$ bezeichnet.
Die Definitionen sind offensichtlich identisch.

##### Distanz zur Hauptdiagonalen

Betrachten wir nun die Gleichung (eq:dist-diag), mit $\mathrm{dist}_\text{diag}(i, j, \mathfrak{g}) = |i - j| \le \mathfrak{g}$.
Ihr entspricht die im [«range-hs»](#range-hs) definierte `distDiag` Funktion.

```haskell
-- | Helper function to compute whether an alignment introduces too many gaps.
-- True if distance |i-j| from main diagonal is lesser or equal to allowed gaps.
distDiag :: MatIdx -> Int -> Bool
distDiag (i, j) gaps = abs (i-j) <= gaps
```

Wir haben `distDiag (i, j) gaps = abs (i-j) <= gaps`, wobei `abs` den Absolutwert des Arguments berechnet.
Dies entspricht genau der Defintion von $\mathrm{dist}_\mathrm{diag}$.

##### Auswahlkriterium {#verification_eligibility_criterion}

Das in (eq:range) definierte Prädikat $\mathrm{range}$ sagt, wenn es auf eine Zelle mit Koordinaten $(i, j)$ angewandt wird, aus, ob der Abstand von $f_{ij}$ zur Hauptdiagonalen zu groß ist um plausibel zu sein.

$$
\mathrm{range}(i, j) = \begin{cases}
    \mathrm{dist}_\mathrm{diag}(i, j, \mathfrak{g}^1) & , i \le j \\
    \mathrm{dist}_\mathrm{diag}(i, j, \mathfrak{g}^2) & , \text{Andernfalls} \\
\end{cases}
$$

Um dieses darzustellen, haben wir im [«range-hs»](#range-hs) Block die Funktion `range` definiert.

```haskell
-- The distance criterion for candidate cell consideration.
range :: Int -> Int -> MatIdx -> Bool
range g1 g2 cell@(i, j)
  | i <= j    = distDiag cell g1
  | otherwise = distDiag cell g2
```

In $\mathrm{range}$ machen wir zunächst eine Fallunterscheidung zwischen $i \le j$ und beliebigen sonstigen Fällen.
Diese Bedingung entspricht dem ersten Pattern `i <= j` in `range`.
Wenn `i <= j`, dann nimmt `range` den Wert `distDiag cell g1`, also. $\mathrm{dist}_\mathrm{diag}(i, j, \mathfrak{g}^1)$ an.
Das zweite Pattern deckt alle sonstigen Fälle ab und produziert den Wert $\mathrm{dist}_\mathrm{diag}(i, j, \mathfrak{g}^2)$.

Da `range` dieselben Fallunterscheidungen vornimmt, und dieselben Werte produziert, ist es offensichtlich äquivalent zu $\mathrm{range}$.

### Kandidatenwahl

Wir haben in (eq:candidates) die Regel $\mathrm{candidates}(i, j) = \{c = (g, h) \in C_{ij} \mathbin{|} \mathrm{range}(c)\}$ zur Kandidatenwahl formuliert, wobei $C_{ij} = \{(i-1, j-1), (i-1, j), (i, j-1)\}$.

In [«candidates-hs»](#candidates-hs) haben wir eine entsprechende Funktion `candidates` formuliert.

```haskell
-- | Find potential candidate cells, from which f_ij may be derived.
candidates :: (Int, Int) -> MatIdx -> [MatIdx]
candidates gaps cell@(i, j) = filter valid [d, h, v]
    where
      valid = range gaps :: (MatIdx -> Bool)

      d = (i-1, j-1)
      v = (i-1, j  )
      h = (i  , j-1)
```

Die Funktion `filter` nimmt ein Prädikat und eine Liste und gibt eine Liste aller Einträge zurück, die das Prädikat erfüllen.

Betrachten wir nun die im `where` Block befindlichen Definitionen, dann zeigt sich, dass das Prädikat `valid` durch partielle Anwendung des `gaps` Arguments ($\mathfrak{g}^1$ und $\mathfrak{g}^1$) auf die `range` Funktion entsteht.
Wenn wir anschließend in `[d, v, h]` die Definitionen von `d`, `v` und `h` einsetzen, ergibt sich die Liste `[(i-1, j-1) ,(i-1, j), (i, j-1)]`, deren Elemente dieselben wie die in $C_{ij}$ sind.

Wir sehen so, dass auch die Kandidatenwahl korrekt implementiert ist.

## Maximierung {#verification_max}

Um den größten Schrittkandidaten zu finden haben wir im [«max-helpers»](#max-helpers) Block die `maxValue` Funktion definiert.

```haskell
-- | Given weighted step directions, find the optimal cell value.
maxValue :: [ScoredStep] -> CellValue
maxValue steps = max `seq` dirs `seq`  -- use seq to force strict evaluation 
  toValue max dirs
    where
      max  = maxCellScore steps
      dirs = filterSteps max steps
```

Die eigentliche Maximierung des Kandidatenwertes findet in der im selben Block definierten `maxCellScore` Funktion statt und `maxValue` dient nur dem Umgang mit den Schrittrichtungen und der Zusammenfassung des resultierenden Wertes.
Da uns bei der Maximierung nur die `Int` Komponente des Zellwerts interessiert, werden wir auch hier nur die damit involvierte `maxCellScore` Funktion untersuchten.

```haskell
-- | Find the highest candidate score.
maxCellScore :: [ScoredStep] -> CellScore
maxCellScore steps = max' Nothing steps
  where
    max' :: CellScore -> [ScoredStep] -> CellScore
    max' accum [] = accum
    max' accum ((s,_):sc)
      | s > accum = max' s sc
      | otherwise = max' accum sc
```

Die Liste `steps` ist vom Typen `steps :: [ScoredStep]`, der Typ `ScoredStep` ist als `(CellScore, StepDirection)` definiert und der Typ `CellScore` entspricht `Maybe Int`.

Wir betrachten Listen als Folgen von Werten.
Mit Länge $|\mathtt{steps}| = n$ definieren wir:

$$
\label{scored-steps}
\mathtt{steps} = (\mathtt{step}_i)_{i \in J_n}
$$

Da nur die `CellScore` Komponente Relevanz für die Frage des maximalen Zellwertes hat, definieren wir auch eine Funktion $\mathrm{score}: (f, d) \mapsto f$, welche auf diese Komponente abbildet und die Folge dieser Komponenten $\mathtt{scores}$.

$$
\label{scores}
\mathtt{s}_i = \mathrm{score}(\mathtt{step}_i)
$$

Der größte Zellwert ist dann durch $\max \{\mathtt{s}_i\}_{i \in J_n}$ gegeben.[^set_of_seqvals]

[^set_of_seqvals]: Hier bezeichnet $\{a_i\}_{i \in M}$ die Menge der Folgenglieder der Folge $(a_i)_{i \in M}$.

Die Aussage, die es zu zeigen gilt, nämlich dass das Ergebnis von `maxVal steps` dem größten Zellwert in `steps` entspricht, können wir also folgendermaßen notieren:

$$
\label{max-val-maximizes}
\mathtt{maxValue}(\mathtt{steps}) = \max \{\mathtt{s}_i\}_{i \in J_n}
$$

`maxValue steps` ist definiert als `max' Nothing steps`, wobei `max'` eine im `where` Block definierte, rekursive Funktion vom Typ `(CellScore -> [ScoredStep] -> CellScore)` ist.

Um (eq:max-val-maximizes) zu zeigen, betrachten wir also zunächst `max'`.

::: #max'-def

```haskell
max' :: CellScore -> [ScoredStep] -> CellScore
max' accum [] = accum
max' accum ((s,_):sc)
  | s > accum = max' s sc
  | otherwise = max' accum sc
```

:::

Wir sehen, dass `max'` bei nichtleeren Listen `(x:xs)` das erste Element der Liste entfernt uns sich selber wieder mit dem Rest `xs` aufruft.
Bei leeren Listen terminiert `max'`.
Da `max'` auf `steps` angewandt wird ist also offenschtlich, dass es genau $n$ Rekursionsschritte macht.

Wir definieren jetzt für beliebige Rekursionsschritte von `max' accum sc` eine Variable $\mathtt{accum}_i$ als den Wert des `accum` Arguments nach Schritt $i \in J_n$.
Sei außerdem $\mathtt{accum}_0$ das initial übergebene Argument.

Wir erhalten mit $(\mathtt{accum}_i)_{i \in J_n}$ die Folge der Funktionsargumente `accum` für *rekursive* Aufrufe von `max'`.

$$
\label{accum}
\mathtt{accum}_i = \begin{cases}
    \mathtt{s}_i & , \mathtt{s}_i > \mathtt{accum}_{i-1} \\
    \mathtt{accum}_{i-1} & , \text{Andernfalls} \\
\end{cases}
$$

::: info
An dieser Stelle sei auf die Anordnungsregeln von `Maybe` hingewiesen.

Für einen beliebigen Wert `x :: (Ord a) => a` eines anordenbaren Typs `a` gilt:

$$
\label{order-maybe-nothing}
\mathtt{Nothing} < \mathtt{Just} \ x
$$

Weiterhin gilt für zwei beliebige Werte `x` und `y` eines anordenbaren Typs `a`:

$$
\label{order-maybe-just}
\mathtt{Just} \ x < \mathtt{Just} \ y \iff x < y
$$

Der Typ `Int` ist anordenbar, also gilt auch `Nothing < Just n` für beliebige `n :: Int` und `Just m < Just n` für beliebige `m :: Int` und `n :: Int` mit `m < n`.
:::

Die Definition von $\mathtt{accum}_i$ für $i < n$ entspricht dem Fall `max' accum ((s, _):sc)` in der [Definition von `max'`](#max'-def) und wir sehen, dass $\mathtt{accum}_n$ der Wert des `accum` nach dem letzten Rekursionsschritt ist.
Aus `max' accum [] = accum` ergibt sich, dass $\mathtt{accum}_n$ dem Funktionswert von `max'` entspricht.

$$
\label{max-terminal-value}
\mathtt{max'}(\mathtt{accum}_0, \mathtt{steps}) = \mathtt{accum}_n
$$

Dementsprechend ist auch der Wert von `maxVal` durch $\mathtt{accum}_n$ gegeben und wir sehen, dass wir äquivalent zu (eq:max-val-maximizes) auch zeigen können, dass $\mathtt{accum}_n$ den größten Kandidatenwert bestimmt.

$$
\label{accum-maximizes}
\mathtt{accum}_n = \max \{\mathtt{scores}_i\}_{i \in J_n}
$$

Wir vermuten, dass `accum` nach jedem Rekursionsschritt $i \in J_n$ den größten bisher gesehenen Wert hält.

$$
\label{accum-max-after-step}
\forall i \in J_n: \mathtt{accum_i} = \max \{\mathtt{scores}_j\}_{j \in J_i}
$$

Wenn wir (eq:max-hypothesis) zeigen können, dann folgt daraus (eq:accum-maximizes) und damit widerum (eq:max-val-maximizes).

Entsprechend ergibt sich als Induktionshypothese, dass `accum` den größten der bisher geprüften Werte enthält.[^max_hyp_prereq]

[^max_hyp_prereq]: Diese Annahme können wir, wie wir später sehen, nur dann machen, wenn beim ersten Aufruf `accum == Nothing` gilt, was per Definition von `maxVal` der Fall ist.

$$
\label{max-hypothesis}
\mathtt{accum_i} = \max \{\mathtt{scores}_j\}_{j \in J_i}
$$

### Induktionsanker

Um den Induktionsanker zu formulieren, betrachten wir solche Fälle, in denen die Eingabeliste $\mathtt{steps}$ leer ist und solche in denen sie Elemente hat.

#### Leere Liste

Für leere Eingaben ergibt sich $\{\mathtt{scores}_i\}_{i \in J_n} = \emptyset$.
Das Maximum der leeren Menge ist undefiniert und wir repräsentieren $\bot$ als `Nothing`.

$$
\label{max-empty}
\max \emptyset = \bot
$$

Es ist wichtig zu beachten, dass wir durch (eq:max-empty) auf den Startwert `Nothing` für `accum` festgelegt sind.

$$
\mathtt{accum}_0 = \max \emptyset = \bot
$$

Dies ist durch die Definition von `maxVal` gegeben.

Mit `max' accum [] = accum` bekommen wir `max' Nothing [] = Nothing` und sehen, dass mit $\mathtt{accum}_0 = \bot$ (eq:max-hypothesis) für leere Eingaben gilt.

#### Nicht-leere Liste

Sei $\mathtt{s_1} = (s, d)$, dann ergibt sich für nicht leere Eingaben $\{\mathtt{scores}_1\} = \{s\}$.

$$
\label{max-singleton}
\max \{\mathtt{scores}_1\} = s
$$

Bei einer einelementigen Menge von Tupeln ist der maximale Wert der ersten Komponenten immer der Wert der ersten Komponente des einen Mengeelements.

Es gibt genau zwei Möglichkeiten für den Wert von $s$.[^equiv_choice_max_anchor]

[^equiv_choice_max_anchor]: Wir könnten in anderer Schreibweise, aber äquivalent sagen, unterscheiden $\mathrm{I}: s = \bot$ und $\mathrm{II}: s = f$.

$$
\begin{array}{ll}
    s = \mathtt{Nothing}  & , \mathrm{I} \\
    s = \mathtt{Just} \ f & , \mathrm{II} \\
\end{array}
$$

**Fall I**

Für `steps == [(Nothing, d)]` ergibt sich `max' Nothing ((Nothing, d) : [])`.
Die Bedingung `Nothing > Nothing` gilt nicht, weswegen wir in die zweite Bedingung, mit Resultat `max' accum sc`, durchfallen, welche immer wahr ist.
Wenn wir nun die Werte einsetzen, ergibt sich `max' Nothing []`, was per definitionem dem Wert `Nothing` entspricht.

$$
\mathtt{accum_1} = \bot = s
$$

Damit gilt (eq:max-singleton) in Fall $\mathrm{I}$.

**Fall II**

Für `steps == [(Just f, d)]` bekommen wir `max' Nothing ((Just f, d) : [])`.

Mit (eq:order-maybe-nothing) sehen wir, dass `Just f > Nothing` gilt, woraus sich `max' s sc` ergibt.
Setzen wir ein, bekommen wir `max' (Just f) []` und damit definitionsgemäß `Just f`.

$$
\mathtt{accum_1} = s
$$

Wir sehen, dass (eq:max-singleton) auch in Fall $\mathrm{II}$ gilt.

Da Fälle $\mathrm{I}$ und $\mathrm{II}$ halten, gilt (eq:max-hypothesis) bei nichtleeren Eingaben nach dem ersten Rekursionsschritt.

### Induktionsschritt

Zeigen wir nun, dass aus der Annahme für Schritt $i$ direkt die Annahme für $i+1$ folgt.

$$
%label{max-step}
\mathtt{accum}_i = \max \{\mathtt{score}_j\}_{j \in J_i}
\stackrel{\mathrm{I.H.}}{\implies}
\mathtt{accum}_{i+1} = \max \{\mathtt{score}_j\}_{j \in J_{i+1}}
$$

Wir haben $\mathtt{accum}_i = \max \{\mathtt{s}_j\}_{j \in J_i}$ und $\{\mathtt{s}_j\}_{j \in J_{i+1}} = \{\mathtt{s}_j\}_{j \in J_i} \cup \{\mathtt{s}_{i+1}\}$.
Es ist offensichtlich, dass für sich das Maximum einer Menge durch Hinzufügen eines kleineren Elements nicht ändert und dass ein größeres Element zum neuen Maximum wird.

$$
\label{max-equal-on-leq}
\forall m \le \max M: \max M = \max M \cup \{m\}
$$

$$
\label{max-changes-on-gt}
\forall m > \max M: m = \max M \cup \{m\}
$$

Es gibt jeweils zwei Möglichkeiten für die Werte von $\mathtt{accum}_i$ und $\mathtt{s}_{i+1}$.
Entweder handelt es sich um definierte Werte, oder nicht.

Wir unterscheiden demnach vier Fälle:

$$
\begin{array}{lrlcrl}
\mathrm{I}:   & \mathtt{accum}_i & = \bot & \land & \mathtt{s}_{i+1} & = \bot \\
\mathrm{II}:  & \mathtt{accum}_i & = \bot & \land & \mathtt{s}_{i+1} & = \mathtt{Just} \ f_{i+1} \\
\mathrm{III}: & \mathtt{accum}_i & = \mathtt{Just} \ f_\text{max} & \land & \mathtt{s}_{i+1} & = \bot \\
\mathrm{IV}:  & \mathtt{accum}_i & = \mathtt{Just} \ f_\text{max} & \land & \mathtt{s}_{i+1} & = \mathtt{Just} \ f_{i+1} \\
\end{array}
$$

**Fall I**

Für `max' Nothing ((Nothing, d):sc)` ergibt sich `max' Nothing sc`.

$$
\mathtt{accum}_{i+1} = \mathtt{accum}_i
$$

Mit (eq:max-equal-on-leq) sehen wir, dass $\mathtt{accum}_{i+1} = \max \{\mathtt{s}_j\}_{j \in J_{i+1}}$ und damit (eq:max-hypothesis) für Fall $\mathrm{I}$.

**Fall II**

Für `max' Nothing ((Just f, d):sc)` ergibt sich mit (eq:order-maybe-nothing) `max' (Just f) sc`.

$$
\mathtt{accum}_{i+1} = \mathtt{s}_{i+1}
$$

Mit (eq:max-changes-on-gt) sehen wir, dass $\mathtt{accum}_{i+1} = \max \{\mathtt{s}_j\}_{j \in J_{i+1}}$ und damit (eq:max-hypothesis) für Fall $\mathrm{II}$.

**Fall III**

Für `max' (Just f') ((Nothing, d):sc)` ergibt sich mit (eq:order-maybe-nothing) `max' (Just f') sc`.

$$
\mathtt{accum}_{i+1} = \mathtt{accum}_i
$$

Mit (eq:max-equal-on-leq) sehen wir, dass $\mathtt{accum}_{i+1} = \max \{\mathtt{s}_j\}_{j \in J_{i+1}}$ und damit (eq:max-hypothesis) für Fall $\mathrm{III}$.

**Fall IV**

Für `max' (Just f') ((Just f, d):sc)` gibt es die beiden Möglichkeiten `f <= f'` und `f > f'`.

Im Fall `f <= f` ergibt sich aus der Definition von `max'` mit (eq:order-maybe-just) `max' (Just f') sc`.

$$
\mathtt{accum}_{i+1} = \mathtt{accum}_i
$$

Mit (eq:max-equal-on-leq) sehen wir, dass $\mathtt{accum}_{i+1} = \max \{\mathtt{s}_j\}_{j \in J_{i+1}}$ und damit (eq:max-hypothesis) für Fall $\mathrm{IV}$ mit `f <= f'`.

Im Fall `f > f` ergibt sich aus der Definition von `max'` mit (eq:order-maybe-just) `max' (Just f) sc`.

$$
\mathtt{accum}_{i+1} = \mathtt{s}_{i+1}
$$

Mit (eq:max-changes-on-gt) sehen wir, dass $\mathtt{accum}_{i+1} = \max \{\mathtt{s}_j\}_{j \in J_{i+1}}$ und damit (eq:max-hypothesis) für Fall $\mathrm{IV}$ mit `f > f'`.

Damit ist (eq:accum-max-after-step) bewiesen, woraus (eq:accum-maximizes) und (eq:max-val-maximizes) folgen. $\blacksquare$

## Füllregeln

Prüfen wir jetzt, ob wir unsere Alignmentmatrix $F$ mit den korrekten Werten befüllen.

$F$ ist eine `NWMatrix` mit Werten vom Typ `Maybe (Int, [StepDirection])`.
Definierte Zellen bekommen den Wert `Just (f_ij, directions)` und undefinierte Zellen `Nothing`.
Die `[StepDirections]` Komponente interessiert uns nicht.

Die Alignmentmatrix wird mit der `fill` Funktion befüllt, welche in [«fill»](#fill) definiert wurde.

```haskell
fill :: AlnInfo -> NWMatrix
fill info = let mat = initMat info
            in mat `seq` fillFrom info (2, 2) mat
            where counts = gapCounts info
```

Diese nutzt zuerst `initMat`, um die Matrix zu initialisieren und dann `fillFrom` um die initialisierte Matrix zu befüllen.

`initMat`und `fillFrom` wiederum nutzen intern `initFillFunc`, bzw. `fillCell`.
Daher betrachten wir im Folgenden hauptsächlich `initFillFunc` und `fillCell`.

### Rekursionsanker

Bei der Anpassung des Algorithmus auf feste Alignmentlängen [haben wir festgestellt](#nw-fill-rules), dass Einträge $f_{ij}$ nur dann definiert sein können, wenn zumindest der diagonale Vorgänger $f_{i-1, j-1}$ definiert ist.
Daraufhin haben wir in (eq:recurrence-anchor) für die nullte Zeile und Spalte von $F$ die folgenden Rekursionsanker formuliert.

$$
f_{i0} = \begin{cases}
    i \cdot w_\text{gap} & , \mathrm{range}(i, 0) \\
    \bot & , \text{Andernfalls} \\
\end{cases}
\qquad
f_{0j} = \begin{cases}
    j \cdot w_\text{gap} & , \mathrm{range}(0, j) \\
    \bot & , \text{Andernfalls} \\
\end{cases} \\
$$

In [init-mat](#init-mat) haben wir als Rekursionsanker `initFillFunc` definiert.

```haskell
initFillFunc :: Cost -> (Int, Int) -> MatIdx -> CellValue
initFillFunc (Cost {w_gap = gap}) gaps cell@(i, j)
  | i == 1    = lift f_1j
  | j == 1    = lift f_i1
  | otherwise = Nothing
  where
    prv   = d1 cell            :: [StepDirection]
    valid = range gaps cell    :: Bool
    f_i1  = f1 valid gap i     :: CellScore
    f_1j  = f1 valid gap j     :: CellScore
    lift  = (flip toValue) prv :: (CellScore -> CellValue)
```

Wir wollen zeigen, dass die `f_ij` die durch unsere Rekursionsanker definiert werden den Wert `(i-1) * gap`, bzw. `(j-1) * gap`, annehmen.[^veri_nw_index_shift]

[^veri_nw_index_shift]: In unserem Code verschiebt sich die Indizierung der Matrix um 1, also wollen wir zeigen, dass für Einträge in $\mathrm{range}$ die Werte $f_{i1} = w_\text{gap} \cdot (i-1)$ bzw. $f_{1j} = w_\text{gap} \cdot (j-1)$ genutzt werden.

`initFillFunc` nimmt als Argumente $w_\text{gap}$ und bindet dieses an den Namen `gap` , die Gapzahlen $(\mathfrak{g}^1, \mathfrak{g}^2)$, welche an `gaps` gebunden werden und den Index $(i, j)$, bzw. `(i, j)`, der zu befüllenden Zelle.
Sie berechnet `f_1j = f1 valid gap j` für `i == 1` und `f_i1 = f1 valid gap i` für `j == 1` (wir können `lift` ignorieren, da es den Wert nicht beeinflusst).

Wenn wir nun die relevanten Definitionen einsetzen, ergibt sich der folgende Ausdruck.

```haskell
initFillFunc (Cost {w_gap = gap}) gaps cell@(i, j)
  | i == 1    = lift $ f1 (range gaps cell) gap j
  | j == 1    = lift $ f1 (range gaps cell) gap i
  | otherwise = Nothing
    -- ... rest ommitted ...
```

Wir bilden also bei `i == 1` auf `f1` mit `j` ab und bei `j == 1` auf `f1` mit `i` und `lift`en das Ergebnis anschließend.

Die Definition der `f1` Funktion sieht so aus:

```haskell
f1 :: Bool -> Int -> Int -> CellScore
f1 valid gap i = if valid
  then Just $ (i-1) * gap
  else Nothing
```

Wir sehen, dass `f1` für solche Einträge, die `valid` sind, `Just $ (i-1) * gap` zurückgibt.
Der Wert `valid` wiederum ist durch das Prädikat `range` festgelegt.
In sonstigen Fällen wird `Nothing` produziert.
Dies erinnert bereits stark an unseren Anker.

Setzen wir nun auch die Definition für `f1` ein, ergibt sich:

```haskell
initFillFunc (Cost {w_gap = gap}) gaps cell@(i, j)
  | i == 1    = lift $ if (range gaps cell) then (i-1) * gap else Nothing
  | j == 1    = lift $ if (range gaps cell) then (j-1) * gap else Nothing
  | otherwise = Nothing
    -- ... rest ommitted ...
```

Wir sehen, dass das erste Pattern den Fall $f_{1j}$ abdeckt und das zweite den $f_{i1}$ Fall.
Für $f_{1j}$ wird, wenn $\mathrm{range}(1, j)$ gilt, der Wert $(i-1) \cdot w_\text{gap}$ produziert und sonst $\bot$ und für $f_{i1}$ m. m. ebenso.

Dies entspricht genau unserer Definition in (eq:recurrence-anchor).

### Rekursionsbeziehung

Wir haben in (eq:recurrence-relation) die folgende angepasste Befüllungsregel  für NW mit festen Alignmentlängen formuliert.

$$
f_{ij} = \max \{f_{gh} + w((g, h), (i, j)) \mathbin{|} (g, h) \in \mathrm{candidates}(i, j)\}
$$

Dafür haben wir im [«fill-cell»](#fill-cell) Block die `fillCell` Funktion definiert.

```haskell
fillCell :: AlnInfo -> MatIdx -> NWMatrix -> NWMatrix
fillCell info cell mat = best `seq`  -- use `seq` to force strict evaluation
  setElem best cell mat
    where
      gaps   = gapCounts info          :: (Int, Int)
      idxs   = candidates gaps cell    :: [MatIdx]
      score  = stepScore info mat      :: (Step -> ScoredStep)
      toStep = (\c -> (c, cell))       :: (MatIdx -> Step)
      steps  = map (score.toStep) idxs :: [ScoredStep]
      best   = maxValue steps          :: CellValue
```

Wir bekommen die durch `candidates` bestimmten Koordinaten der Kandidatenzellen und binden diese an den Namen `idxs`.

Dann definieren wir die Funktionen `toStep` und `score`.
`toStep` nimmt einen Zellindex $o$ und bildet ihn auf den Schritt $(o, d)$ ab, wobei $d$ den Index der zu befüllenden Zelle bezeichnet.

Die `score` Funktion entsteht durch die partielle Anwendung von `info` und `mat` auf die [zuvor besprochene](#verification_stepscore) `stepScore` Funktion, wodurch diese den Typ `(Step -> ScoredStep)` annimmt, also einen Schritt $q$ nimmt und ihn auf dessen Gewicht und Richtung $(w(q), \mathrm{dir})$ abbildet.

Für die Elemente in `idxs` bestimmen wir nun mittels Komposition von `score . toStep` die jeweiligen `ScoredStep` Tupel, welche mit `maxValue` gewertet werden.

Wir [haben gezeigt](#verification_max), dass `maxValue` die übergebene Liste von `ScoredStep` Werten auf den `CellValue` mit dem  größten enthaltenen `CellScore` abbildet, welchen wir an den Namen `best` binden.

Mit `setElem best cell mat` füllen wir also die betrachtete Zelle mit dem besten Kandidatenwert, was genau der Anforderung entspricht.
