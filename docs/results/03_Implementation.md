---
title: Implementation
---

# Implementation eines Sequenzalinierers {#03_implementation}

In dieser Sektion widmen wir uns der Implementation einer Lösung für das Problem der paarweisen Sequenzalinierung, welche auf der Arbeit im vorigen Kapitel aufbaut.

Dafür definieren wir zuerst entsprechende Datentypen, um das Problem darzustellen und im Anschluss Funktionen, um es zu lösen.

::: info
Dieses Kapitel beinhaltet viele Codeblöcke und beispielhafte Ein- und Ausgaben.
Näheres zu den Hintergründen findet sich im Kapitel [Methoden](#00b_material_and_methods).

**Codeblöcke**

Die Codeblöcke sind im Text eingebunden und mit einer ID versehen.
Die Block-ID steht am rechten Rand über dem Block und ist mit "[Block-ID:]{.smallcaps}" gekennzeichnet.
Beispielsweise hat der folgende Block die ID "example":

``` {.haskell #example}
foo :: String
foo = "bar"
```

Anhand der Block-ID kann ein Block später in anderen Codeblöcken referenziert werden.
Block-IDs sind ggf. Pfade zu Dateien.
In diesem Fall wird der Inhalt des Blocks in die referenzierte Datei geschrieben.

Der folgende Block referenziert den "example" Block und schreibt das Ergebnis nach `src/example.hs`{.bare}:

``` {.haskell file=src/example.hs}
module Example where
import Data.List
<<example>>
```

An der Position des Strings `<<example>>`{.bare} werden die Inhalte des referenzierten Blocks eingefügt.
:::

Für die Implementation nutzen wir die funktionale Sprache Haskell.
Haskell nutzt Module, um Code zu strukturieren.
Diese beginnen mit `module <name> where`, gefolgt von Imports `import Module (func1, func2, …)`, welche am Anfang des Moduls durchgeführt werden müssen und anschließend den Funktionsdeklarationen.

## Naive Implementation

Die einfachste Variante ein optimales Alignment zu finden ist es, alle Möglichkeiten auszuprobieren.
Wir haben bereits im letzten Kapitel festgestellt, dass dies keine gute Idee ist, aber implementieren diese Variante als Fingerübung um uns mit Haskells Syntax und dem typischen Vorgehen vertraut zu machen.

### Datentypen

Haskell arbeitet mit algebraischen Datentypen.
Neue Datentypen können mit `data` oder `newtype` definiert werden und Typenaliasse mit `type`.

::: info
Wir haben drei Möglichkeiten, um in Haskell neue Datentypen anzulegen.
Dafür nutzen wir die Keywords `type`, `newtype` und `data`.

Mit `type` wird ein Typenalias angelegt.
Z.b. kann man mit `type Point = (Float, Float)` Tupel von Gleitkommazahlen als `Point` referenzieren.
Wenn jetzt eine Funktion `norm :: Point -> Float` angelegt, dann nimmt diese ein solches Tupel.

Mit `newtype` wird ein neuer Typ angelegt, der Isomorph zu einem existierenden Typen ist.
Würde man also `newtype Point = Point (Float, Float)` definieren, verhielte sich `Point` identisch zu Tupeln von Gleitkommazahlen, wäre aber selber kein solches Tupel.
Legen wir jetzt wieder `norm :: Point -> Float` an, dann nimmt diese nur eingaben vom Typ `Point`, nicht aber einfache Tupel von Zahlen.

Mit `data` wird ein neuer Datentyp angelegt.
Dieser kann eine beliebige Struktur haben, die nicht auf anderen Typen basieren muss.
:::

Wir brauchen Typen für:

- Das Alphabet $\Sigma$,
- Sequenzen, als Folgen von Symbolen aus $\Sigma$,
- Gaps, bzw. das Gapsymbol $c_\text{gap}$,
- das Alignmentalphabet $\overline \Sigma$,
- alinierte Sequenzen, als Folgen über $\overline \Sigma$,
- Kosten für Matches, Missmatches und Gaps und
- Alignments, als geordnete Paare alinierter Sequenzen.

Zunächst definieren wir einen Datentypen für unser Alphabet $\Sigma$, bestehend aus den Nukleobasen $\{A, C, G, T\}$.

``` {.haskell #base}
-- | Datatype for nucleotides
data Base = A | C | G | T deriving (Eq, Show, Read)
```

Jetzt können wir die Buchstaben `A`, `C`, `G` und `T` als Konstruktoren für Basen verwenden.

::: info
Typenklassen, wie `Eq`, `Show` und `Read`, ermöglichen die Nutzung bestimmter Operationen mit unseren Datentypen.

Die `Eq` Klasse ermöglicht es beispielsweise Elemente miteinander auf Gleichheit zu prüfen.
Die `Show` und `Read` Klassen erlauben die Umwandlung zu und von Strings.

Mittels der `deriving` Statements leiten wir automatisch von bestimmten Typenklassen ab, aber nicht jede Typenklasse ist automatisch ableitbar.
Um einen Datentypen manuell zu einer Typenklasse hinzuzufügen, nutzen wir das `instance` Keyword und implementieren die notwendigen Funktionen.

Typenklassen sind also ungefähr vergleichbar mit Interfaces in objektorientierten Sprachen, da sie nur definieren, was mit einem Datentypen gemacht werden kann, nicht aber unbedingt wie es gemacht wird.
:::

Darüber hinaus wollen wir Sequenzen von Buchstaben nutzen können.

``` {.haskell #naive-seq}
-- | Datatype for sequences
newtype Seq a = Seq [a] deriving (Eq)
```

Also legen wir mithilfe des `newtype` Keywords, den polymorphen `Seq` Konstruktor an.
Mit diesem können wir Sequenzen aus Listen eines bestimmten Typs, z.B. von Basen, definieren.

Wenn wir `Seq` von `Show` und `Read` ableiten ließen, sähe die String-Darstellung der Sequenz "ACGT" so aus: `Seq [A,C,G,T]`.
Wir wollen allerdings eine flache String-Darstellung.
Dafür definieren wir eine Hilfsfunktion und fügen den Datentypen `Seq a` der Typenklasse `Show` manuell hinzu.

Weiterhin wollen wir Sequenzen wie Listen von Basen behandeln können, weswegen wir `Functor` und `Foldable` implementieren müssen, um über Elemente zu mappen.

::: info
Das Mappen einer Funktion `f` über die Liste `xs` entspricht der Anwendung von `f` auf jedes Listenelement.

Die Definition von `map` gleicht dem Folgenden Code.

```haskell
map :: (a -> b) -> [a] -> [b]
map f [] = []
map f (x:xs) = f x : map f xs
```

`map` nimmt eine Funktion `f :: a -> b` und eine Liste von `a` Werten und produziert eine Liste von `b` Werten.
Sie ist ein Sonderfall der allgemeineren `fmap` Funktion.

Die `fmap` Funktion hat die Signatur[^instance_sig_extension] `fmap :: (Functor f) => (a -> b) -> f a -> f b` und wendet eine Funktion auf einen Funktorkontext an.

[^instance_sig_extension]: Da wir, der Anschaulichkeit wegen, Funktionssignaturen auch in `instance` Deklarationen nutzen möchten, müssen wir auch die `{-# LANGUAGE InstanceSigs #-}` Spracherweiterung aktivieren.

Der Begriff Funktor stammt aus der Kategorientheorie und bezeichnet dort eine Abbildung $F: \mathcal{C} \to \mathcal{D}$, die Objekte und Morphismen[^morphism] in der Kategorie $\mathcal{C}$ auf Objekte und Morphismen in der Kategorie $\mathcal{D}$ abbildet und dabei die Identitätsmorphismen erhält.[^identity_morphism]

[^morphism]: Strukturbewahrende Abbildungen innerhalb einer Kategorie.
[^identity_morphism]: Für jedes Objekt $X$ in $\mathcal{C}$ existiert ein Identitätsmorphismus $\mathrm{id}_X: X \to X$, welcher $X$ auf sich selber abbildet.
    Wenn $F$ den Morphismus $f: X \to Y$ in $\mathcal{C}$, auf den Morphismus $F(f): F(X) \to F(Y)$ abbildet, dann muss also gelten, dass $F(\mathrm{id}_X) = \mathrm{id}_{F(X)}$.

Aus diesem Grund muss für `fmap` gelten, dass `fmap id == id`.
:::

``` {.haskell #naive-seq-classes}
-- | Helper for implementing flat readable types.
readFlatList :: Read a => String -> [a]
readFlatList str = read' str
  where
    wrap' :: String -> [String]
    wrap' str = [[toUpper ch] | ch <- str]

    read' :: Read a => String -> [a]
    read' = map (read :: Read a => String -> a).wrap'

-- | Make sequences display as flat strings.
instance Show a => Show (Seq a) where
  show (Seq symbols) = concatMap show symbols

-- | Enable reading sequences from flat strings.
instance Read a => Read (Seq a) where
  readsPrec _ chars = [(Seq $ readFlatList chars, "")]

-- | Make Seq a Functor, so we can apply functions to its contents.
instance Functor Seq where
  fmap = fmapDefault

-- | Make Seq Foldable, so we can use functions to summarize its contents.
instance Foldable Seq where
  foldMap = foldMapDefault

-- | Make Seq Traversable, so we can apply functions to its contents, while preserving the structure.
instance Traversable Seq where
  -- sequenceA :: Applicative f => Seq (f a) -> f (Seq a)
  traverse :: Applicative f => (a -> f b) -> Seq a -> f (Seq b)
  traverse g (Seq xs) = Seq <$> traverse g xs
```

Jetzt sieht die Darstellung von `Seq [A, C, G, T]` so aus: `ACGT` und wir können Strings von Basensymbolen einlesen und einfach Funktionen auf Sequenzen anwenden.

Um zwei Sequenzen zu alinieren, müssen wir die Möglichkeit haben Gaps einzubauen.
Also brauchen wir einen Datentypen für das Alphabet $\overline \Sigma = \Sigma \cup \{c_\text{gap}\}$, für welchen es natürlich auch eine ansprechende Repräsentation geben sollte.

``` {.haskell #aln-char}
-- | Define an alignment alphabet with gaps, based on another alphabet type
data AlnChar a = Symbol a | Gap deriving (Eq)

-- gap chars that are allowed for reading
gapChar = '-'
gapSynonyms = "_."
gapChars = gapChar : gapSynonyms

-- | Make the alignment alphabet display properly.
instance Show a => Show (AlnChar a) where
  show (Symbol s) = show s
  show Gap = show gapChar

-- | Allow function application to the AlnChar contents.
instance Functor AlnChar where
  fmap :: (a -> b) -> AlnChar a -> AlnChar b
  fmap f (Symbol s) = Symbol (f s)
  fmap f Gap = Gap
```

Mit dem `AlnChar` Typkonstruktor können wir für ein beliebiges Alphabet $\Sigma$, bzw. `a`, ein entsprechendes Alignmentalphabet $\overline \Sigma$, bzw. `AlnChar a`, definieren, dessen Buchstaben entweder Symbole aus $\Sigma$ (`Symbol a`), oder Gaps (`Gaps`) sind.

Zusätzlich zu $\overline \Sigma$ müssen wir auch Sequenzen über $\overline \Sigma$ darstellen und repräsentieren.

``` {.haskell #aln-seq}
-- | Type for aligned sequences, i.e., those potentially containing gaps.
newtype AlnSeq a = AlnSeq [AlnChar a] deriving (Eq)

-- | Make aligned sequences display properly.
instance Show a => Show (AlnSeq a) where
  show (AlnSeq symbols) = concatMap show symbols

-- | Enable reading aligned sequences from flat strings.
-- instance Read a => Read (AlnSeq a) where
--   readsPrec _ chars = [(AlnSeq $ readFlatList chars, "")]

-- | Allow function application to the AlnSeq contents.
instance Functor AlnSeq where
  fmap :: (a -> b) -> AlnSeq a -> AlnSeq b
  fmap f (AlnSeq seq) = AlnSeq $ map (fmap f) seq

-- | Allow summarizing AlnSeq contents.
instance Foldable AlnSeq where
  foldr :: (a -> b -> b) -> b -> AlnSeq a -> b
  foldr f z (AlnSeq (Gap:syms)) = foldr f z (AlnSeq syms)
  foldr f z (AlnSeq ((Symbol s):syms)) = f s $ foldr f z (AlnSeq syms)
```

Mithilfe von `AlnChar` definieren wir also den Typkonstruktor `AlnSeq` für alinierte Sequenzen von Symbolen in $\Sigma$, bzw. `a`.
Dementsprechend repräsentiert `AlnSeq` Sequenzen über $\overline \Sigma$.

Nun überlegen wir uns, wie Alignments, bzw. Templates dargestellt werden sollten.

``` {.haskell #naive-aln}
-- | Define alignments as tuples of alignment sequences
newtype Aln a = Aln (AlnSeq a,  AlnSeq a) deriving (Eq, Show)
```

Da wir nur paarweise Alignments betrachten, sind unsere Templates Matrizen der Form $2 \times k$.
Der Einfachheit halber definieren wir Templates daher als Tupel alinierter Sequenzen.

Zuletzt definieren wir einen Typen für die Gewichte, die unsere Zielfunktion zum Bewerten der Alignments braucht und ein Alias, welches diese und $\mathfrak{g}_\text{max}$ bündelt.

::: info
**Beispiele**

Ein- und Ausgaben werden im interaktiven Haskell REPL `ghci`{.bare} werden folgenden Stil wiedergegeben:

```ghci
ghci> func arg arg
<result>
```

Um diese selber auszuprobieren, kann die Arbeit geladen werden.
Der Demo-Code fürden naiven Ansatz befindet sich in `src/Align/Naive/Demo.hs`{.bare} und der für die DP-Lösung in `src/Align/Demo.hs`{.bare}.
Um diesen zu laden muss zunächst in das `src/`{.bare} Verzeichnis gewechselt werden.

Wenn es sich um Shell-Befehle außerhalb von `ghci`{.bare} handelt, wird diese ein `$`{.bare} vorangestellt.
Bspw. wird mit dem folgenden Befehl der Demo-Code für den NW-Aligner in `ghci`{.bare} geladen:

```terminal
$ cd src/
$ ghci Align.hs
```

:::

``` {.haskell #type-cost}
-- | Record type for costs.
data Cost = Cost {w_match :: Int, w_miss :: Int, w_gap :: Int} deriving (Eq, Show)
```

::: example
Bei `Cost` handelt es sich um einen sog. "Record Type", in dem verschiedene Werte gebündelt werden können.
Dabei werden Felder mit bestimmten Datentypen deklariert, welche bei der Instanziierung gefüllt werden müssen.
In diesem Falle gibt es die Felder `w_match`, `w_miss` und `w_gap`, welche Werte mit dem Typ `Int` halten und unseren Gewichten $w_\text{match}, w_\text{miss}$ und $w_\text{gap}$ entsprechen.

Die Übergabe der Argumente beim Definieren eines Wertes kann der Reihenfolge nach geschehen, oder die Argumente werden namentlich benannt.

```ghci
ghci> Cost 9 12 (-3)
Cost {w_match = 9, w_miss = 12, w_gap = -3}
ghci> Cost {w_match = 1, w_gap = -2, w_miss = 3}
Cost {w_match = 1, w_miss = 3, w_gap = -2}
```

Um auf Feldwerte zuzugreifen, gibt es unterschiedliche Möglichkeiten.

Die Namen der Felder definieren automatisch Funktionen, welche für den Zugriff genutzt werden können.

```ghci
ghci> let c = Cost 1 (-1) (-2)
ghci> w_gap c
-2
```

In Funktionsdefinitionen und `let` Bindungen kann auch sog. strukturelles Patternmatching genutzt werden.
Dies funktioniert so wie die Instanziierung mit benannten Argumenten.
Dabei werden die Feldwerte eines Funktionsargumentes direkt an Namen gebunden, unter denen sie in der Funktion verfügbar sein sollen.

```
total :: Cost -> Int
total cost@(Cost {w_match = match, w_miss = miss, w_gap = gap})
  = match + miss + gap
```

In diesem Beispiel binden wir `w_match`, `w_miss` und `w_gap` an die Namen `match`, `miss` und `gap` und bestimmen dann die Summe der Werte.
Mit dem `@` geben wir dem gesamten Eintrag den Namen `cost`.
:::

### Logik

Zunächst definieren wir Kombinationen als Listen ganzer Zahlen und eine Hilfsfunktion für die erste $k$-Kombination $(1, 2, \dots, k)$.

``` {.haskell #combination}
-- | Encodes an ordered list of indices.
type Combination = [Int]

-- | Compute the first combination of length k.
firstCombination :: Int -> Combination
firstCombination k = [1..k]
```

Bisher ist der Code trivial.

Versuchen wir nun eine Funktion $\mathrm{succ}: C^n_k \to C^n_k$ zu definieren, welche für eine Kombination $c_i$  den Nachfolger $c_{i+1}$ findet.

``` {.haskell #successor}
-- | We chop off the last indices
-- fst gives number of chopped positions,
-- snd gives remaining indices
type TrimmedCombination = (Int, Combination)

-- | Compute the successor of a combination of indices for a list of length n.
successor :: Int -> Combination -> Maybe Combination
successor _ [] = Nothing
successor n comb = succ' comb
  where
    -- | Length of the combination.
    k :: Int
    k = length comb

    -- | Determine the first index, that can be incremented,
    -- and discard everything before.
    -- i: number of chopped indices, revComb: reversed combination
    incr :: Int -> Combination -> Maybe TrimmedCombination
    incr _ [] = Nothing
    incr i revComb@(x:xs)
      -- let i' := (k-i) be an index in a non-reversed combination
      -- then we have n-k+i' == n-k-(k-i) == n-i
      | x < (n-i) = Just (i, (x+1):xs)
      | x == (n-i) = incr (i+1) xs
      -- if x > (n-k+i') we're in illegal territory already
      | otherwise = Nothing

    -- | Fill the discarded bits of an incremented combination with the lowest possible subsequence.
    fill :: TrimmedCombination -> Combination
    fill (0, revComb) = let comb = reverse revComb in comb
    fill (i, x:xs) = fill (i-1, (x+1):x:xs)

    succ' :: Combination -> Maybe Combination
    succ' = (fmap fill).(incr 0).reverse
```

Das Vorgehen, um den Nachfolger einer Kombination $c$ zu finden, funktioniert analog zur Beschreibung im vorigen Kapitel.

1. Zuerst finden wir mit `incr` den letzten Index $i$, mit $c_i < n-k+i$, inkrementieren diesen und schmeißen die höheren Stellen weg,
2. dann füllen wir in `fill` die entfernten Stellen mit der kleinsten Subkombination $(c_i + 1, c_i + 2, \dots, c_i + (k-i))$ wieder auf Länge $k$ auf,
3. um anschließend beide Funktionen in `succ'` zu komponieren.

```ghci
ghci> successor 4 [1, 4]
Just [2, 3]
ghci> successor 4 [3, 4]
Nothing
```

Der Wert `Nothing` signalisiert, dass es keinen validen Nachfolger gibt.

::: info
Da $C^n_k$ endlich ist, wissen wir, dass es eine letzte Kombination $c_{\binom{n}{k}} = (n-k, \dots, n)$, ohne Nachfolger gibt.

Um mit solchen Definitionslücken umzugehen, bietet Haskell die `Maybe` Monade an.
`Maybe a` ist so definiert,^[ `data Maybe a = Just a | Nothing`] dass es entweder einen Wert `Just a` oder `Nothing`, also keinen Wert, hat.
:::

Mithilfe der Nachfolgefunktion `successor` können wir die Menge $C^n_k$ aller $\binom{n}{k}$ möglichen Kombinationen berechnen.

``` {.haskell #combinations}
-- | Compute all n choose k combinations.
combinations :: Int -> Int -> [Combination]
combinations n k
  -- TODO errors could be [] instead
  | n < k = error "k may not exceed n"
  | n < 0 = error "n may not be negative"
  | otherwise = cont start $ successor n start
    where
      start :: Combination
      start = firstCombination k

      cont :: Combination -> Maybe Combination -> [Combination]
      cont last Nothing = [last]
      cont last (Just next) = last : (cont next $ successor n next)
```

Wir starten mit der ersten Kombination der Länge $k$ und fügen so lange den Nachfolger hinzu, wie dieser definiert ist.

```ghci
ghci> combinations 4 3
[[1,2,3],[1,2,4],[1,3,4],[2,3,4]]
```

Da wir mit `combinations` alle validen Gapbelegungen erzeugen können, befüllen wir jetzt unsere Sequenzen mit diesen Gaps.
Das bedeutet, dass wir von `Seq` in `AlnSeq` umwandeln.
So können wir dann alle möglichen Alignments zweier Sequenzen generieren.

``` {.haskell #alignments}
-- | Compute an aligned sequence from a sequence and a combination of gap positions.
alignSeq :: Seq a -> Combination -> AlnSeq a
alignSeq seq gaps = AlnSeq $ alignSeq' 1 seq gaps
  where
    alignSeq' :: Int -> Seq a -> Combination -> [AlnChar a]
    alignSeq' _ (Seq []) gaps = [Gap | g <- gaps]
    alignSeq' _ (Seq seq) [] = [Symbol sym | sym <- seq]
    alignSeq' pos seq@(Seq (b:bs)) comb@(gap:gaps)
      | gap == pos = Gap : alignSeq' (pos + 1) seq gaps
      | otherwise = (Symbol b) : alignSeq' (pos + 1) (Seq bs) comb

-- | Compute all possible alignments of two sequences with a given number of allowed gaps.
alignments :: Int -> Seq a -> Seq a -> [Aln a]
alignments g_max seq1 seq2 = 
  [Aln (alignSeq seq1 comb1, alignSeq seq2 comb2)
        | comb1 <- combinations k (k - m)
        , comb2 <- combinations k (k - n)]
  where
    m = length seq1
    n = length seq2
    k = g_max + max m n
```

Um die Alignments der Sequenzen $s^1$ und $s^2$, mit Längen $M$, bzw. $N$ und Templatelänge $K = \max \{M, N\} + \mathfrak{g}_\text{max}$ zu bestimmen, generieren wir die Menge $C^K_M \times C^K_N$ und nutzen `alignSeq` um die Sequenzen entsprechend der jeweiligen Kombination zu alinieren.

Nun können wir durch alle Möglichen Alignments iterieren.
Was uns jetzt noch fehlt, ist eine Möglichkeit die Alignments zu bewerten.

In (eq:objective) haben wir die Zielfunktion folgendermaßen definiert:

$$
\sum_{k = 1}^{K}
\left[
    w_\text{gap} \cdot \gamma_k
    \left[
        \sum_{i = 1}^{M} \sum_{j = 1}^{N} w_{i, j} \cdot \phi_{i, j, k}
    \right]
\right]
$$

``` {.haskell #naive-align-helpers}
score :: Eq a => Cost -> Aln a -> Int
score _ (Aln (AlnSeq [], AlnSeq [])) = 0
score cost (Aln (AlnSeq (x:xs), AlnSeq (y:ys))) =
  score' x y + score cost (Aln (AlnSeq xs, AlnSeq ys))
  where
    score' :: Eq a => AlnChar a -> AlnChar a -> Int
    score' Gap Gap = 0
    score' Gap _ = w_gap cost
    score' _ Gap = w_gap cost
    score' x y
      | x == y = w_match cost
      | otherwise = w_miss cost

type ScoredAln a = (Int, Aln a)

maximize :: Eq a => Cost -> [Aln a] -> ScoredAln a
maximize _ [] = error "Nö"
maximize cost (aln:alns) = max (sc, aln) alns
  where
    sc :: Int
    sc = score cost aln

    max :: Eq a => ScoredAln a -> [Aln a] -> ScoredAln a
    max scoredAln@(sc, best) [] = (sc, best)
    max scoredAln@(sc, best) (aln:alns)
      | sc <= nxtSc = max (nxtSc, aln) alns
      | otherwise = max scoredAln alns
        where
          nxtSc :: Int
          nxtSc = score cost aln
```

Jetzt können wir unsere naive Alignmentfunktion implementieren.

``` {.haskell #naive-align}
align :: Eq a => Seq a -> Seq a -> Cost -> Int -> ScoredAln a
align seq1 seq2 cost g_max = maximize cost $ alignments g_max seq1 seq2
```

Gegeben zwei Sequenzen `seq1`  und `seq2`, Kosten und die Anzahl an zulässigen Gaps, berechnen wir das optimale Alignment, indem wir aus allen möglichen Alignments, gegeben durch `alignments g_max seq1 seq2`, dieses wählen, welches mit den gegebenen Kosten den maximalen Wert produziert.

Damit können wir das optimale Alignment für unsere [Beispielsequenzen]() berechnen.

```ghci
ghci> let cost = Cost 1 (-1) (-2)
ghci> let seq1 = read "agtac" :: Seq Base
ghci> let seq2 = read "atgc" :: Seq Base
ghci> align seq1 seq2 cost 1
(0,Aln (AGTAC-,A-TGC-))
```

## Needleman-Wunsch Implementation

Eine bessere Variante unser Problem zu lösen ist die Alinierung mittels Needleman-Wunsch.

### Datentypen

Auch hier betrachten wir zunächst, welche Daten wir brauchen um das Problem darzustellen, bzw. zu lösen und definieren sinnvolle Datentypen.

Um unser Optimierungsproblem mit NW zu lösen, brauchen wir zumindest die folgenden Informationen:

- Anzahl erlaubter Gaps $\mathfrak{g}_\text{max}$,
- Kosten $w_\text{match}, w_\text{miss}$ und $w_\text{gap}$,
- Sequenzen $s^1, s^2$,

Wir können $\mathfrak{g}_\text{max}$ einfach als `Int` darstellen und für die Kosten haben wir bereits den `Cost` Record-Typen definiert.
Wir definieren allerdings den `Seq` Typen neu, als schlichtes Alias für `String`.
Dies erleichtert unsere Arbeit im weiteren Verlauf, erfordert aber auch, dass wir abhängige Typen wie z.B. `AlnChar` entsprechend anpassen.

``` {.haskell #type-seq}
-- | We model sequences as plain strings, i.e., lists of chars.
type Seq = String

-- | Alignment characters consist of either symbols or gaps.
data AlnChar = Symbol Char | Gap deriving (Eq)

-- | Alignments are list of AlnChar tuples.
type Aln = [(AlnChar, AlnChar)]
```

Da die Laufzeit für die Wahl eines Listenelements mittels Index in der Klasse $\mathcal{O}(n)$ liegt, benutzen wir im Folgenden Arrays um Sequenzen zu speichern.
Dadurch ist mit $\mathcal{O}(1)$ konstante Laufzeit für Zugriffe gewährleistet.

Um mit dem Typen `Array` zu arbeiten müssen wir diesen importieren.
Wir importieren außerdem den `(!)` Operator, der Indexzugriff auf Arrayelemente erlaubt und die `listArray` und `elems` Funktionen, welche Arrays aus Listen erzeugen, bzw. in diese umwandeln.

``` {.haskell #align-imports}
import Data.Array (Array, (!), listArray, elems)
```

Jetzt definieren wir den `SeqArray` Typen als Alias für `Array Int Char`, also mit `Int` indizierte Arrays von `Char` Werten, und eine Hilfsfunktion `mkArr` um Sequenzen in korrekt indizierte Arrays umzuwandeln.

``` {.haskell #type-seq-arr}
-- | We use arrays for constant time access.
type SeqArr = Array Int Char

-- | Create sequence arrays from sequence strings.
-- Arrays allow constant time lookups.
-- Indexing is shifted by one, so we index from 2 through m+1.
mkArr :: Seq -> SeqArr

mkArr xs = let m = length xs
           in listArray (2, m+1) xs
```

Aus den Sequenzen ergeben sich die Längen $M, N$ und mit $\mathfrak{g}_\text{max}$ die erlaubten Gaps pro Sequenz $\mathfrak{g}^1,\mathfrak{g}^2$.

Um all diese Informationen einfach zugreifbar zu haben, definieren wir einen entsprechenden Record-Typen `AlnInfo`, Funktionen um Längen, bzw. Gapzahlen zu bestimmen und einen Helfer um solche Records aus normalen Sequenzen und flachen Werten für Kosten und Gaps anzulegen.

``` {.haskell #type-aln-info}
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

-- | Compute gap numbers for an AlnInfo record.
gapCounts :: AlnInfo -> (Int, Int)
gapCounts info@(AlnInfo {g_max = g})
  = let (m, n) = seqLengths info
        l      = max m n
    in  (g + (l - m), g + (l - n))

-- | Convenience constructor to create AlnInfo records from loose weights and lists.
mkInfo :: Int -> Int -> Int -> Int -> Seq -> Seq -> AlnInfo
mkInfo g_max w_match w_miss w_gap seqA seqB
  = AlnInfo g_max (Cost w_match w_miss w_gap) (mkArr seqA) (mkArr seqB)
```

Jetzt können wir die notwendigen Informationen, um das Alignmentproblem zu lösen als `AlnInfo` Einträge zusammenfassen und mit `seqLengths` und `gapCounts` die Sequenzlängen, bzw. Gapzahlen bestimmen.

```ghci
ghci> let info = mkInfo 1 1 (-1) (-2) "AGTAC" "ATGC"
ghci> info
AlnInfo {g_max = 1, weights = Cost {w_match = 1, w_miss = -1, w_gap = -2}, seqA = array (2,6) [(2,'A'),(3,'G'),(4,'T'),(5,'A'),(6,'C')], seqB = array (2,5) [(2,'A'),(3,'T'),(4,'G'),(5,'C')]}
ghci> seqLengths info
(5,4)
ghci> gapCounts info
(1,2)
```

NW findet das optimale Alignment als maximalen Pfad durch eine Matrix, wobei der (Teil-) Pfad zu einer Zelle rekursiv aus den maximalen Schritten zu dieser Zelle aufgebaut wird.
Pfade sind Folgen von Indizes und Schritte sind Paare von Indizes.

Da wir uns für viele Unterscheidungen dafür interessieren aus welcher Richtung wir kamen und nicht aus welcher spezifischen Zelle, definieren wir zusätzlich den Datentyp `StepDirection` und einen Helfer `fromStep` zur Umwandlung von `Step` in `StepDirection`.

``` {.haskell #type-mat-parts}
-- | Matrix indices.
type MatIdx = (Int, Int)

-- | Path through a matrix.
type Path = [MatIdx]

-- | Steps are `MatIdx` tuples of the form `(origin, destination)`.
type Step = (MatIdx, MatIdx)

-- | Datatype to denote step directions.
data StepDirection = Diagonal | Horizontal | Vertical deriving Eq

-- | Calculate a StepDirection from a Step.
fromStep :: Step -> StepDirection
fromStep (orig@(g, h), dest@(i, j))
  | i == g+1 && j == h+1 = Diagonal
  | i == g   && j == h+1 = Horizontal
  | i == g+1 && j == h   = Vertical
  | otherwise = error "illegal step"
```

Um einen Typen für unsere Matrix zu formulieren, müssen wir noch wissen, welche Art von Werten darin enthalten sind.

::: info
Damit wir überhaupt mit Matrizen arbeiten können, importieren wir zunächst den `Matrix` Typen und einige Hilfsfunktionen aus dem, durch das `matrix` Paket bereitgestellten, `Data.Matrix` Modul.

``` {.haskell #align-imports}
import Data.Matrix (Matrix, matrix, nrows, ncols, getElem, setElem)
```

Die `matrix` Funktion nimmt als Eingabe zwei Integer-Argumente, welche die Anzahl von Zeilen und Spalten darstellen und eine Füllfunktion `f :: Int -> Int -> a`, welcher die Zellindizes `i` und `j` übergeben werden und erstellt damit eine `Matrix a`.
Die `nrows` und `ncols` Funktionen berechnen die Anzahl von Zeilen, bzw. Spalten einer Matrix und `getElem` und `setElem` werden genutzt um Werte von Zellen zu lesen, bzw. zu schreiben.
:::

Offensichtlich müssen wir den Wert $f_{ij}$ der Zelle speichern.
Dieser ergibt sich aus den Kosten und kann als `Int` dargestellt werden.
Zusätzlich dazu, wollen wir noch wissen, aufgrund welcher vorherigen Zellen der Wert zustande kam.
Dazu nutzen wir den `StepDirection` Typen und da es potentiell mehr als einen Vorgänger geben kann, speichern wir eine Liste von Vorgängern.
Wir können Werte in Zellen also als Tupel `(Int, [StepDirection])` darstellen.

Da wir am Anfang nicht definierte Einträge haben und auch beim anschließenden Befüllen nicht zwangsläufig alle Zellen berechnen, nutzen wir wieder die `Maybe` Monade und kennzeichnen undefinierte Zellen mit `Nothing`.

Wir arbeiten also über einer Matrix mit Zellwerten vom Typ `Maybe (Int, [StepDirection])`.

``` {.haskell #type-nw-matrix}
-- | What goes into the matrix? If a cell is defined,
-- we have just a value f_ij, and a list of one or more
-- precursors, otherwise nothing.
type CellValue = Maybe (Int, [StepDirection])

-- | A Needleman-Wunsch matrix.
type NWMatrix = Matrix CellValue

-- | Helper that changes the order of arguments for getElem.
getFrom :: NWMatrix -> (Int, Int) -> CellValue
getFrom mat (i, j) = getElem i j mat
```

Damit wir die Richtungen potentieller Kandidatenschritte leicht anhand der dazugehörigen Werte vergleichen können, wäre es nützlich einen Typen für Tupel der Form `(Maybe Int, StepDirection)` mit Wert und Richtung eines Kandidaten festzulegen.

``` {.haskell #type-scores}
type CellScore = Maybe Int
type ScoredStep = (CellScore, StepDirection)
```

Wie strukturieren wir nun unsere Ergebnisse?

Offensichtlich brauchen wir die errechneten Alignments[^maybe_multiple_alns] und deren Wert.
Weiterhin ist es sinnvoll, die ursprünglichen Eingabe für das Problem zu speichern, also brauchen wir ein `AlnInfo` Feld.

[^maybe_multiple_alns]: Da eine Zelle mehr als einen Vorgänger haben kann, kann es auch mehr als einen Pfad durch die Matrix geben.

Wir speichern auch die errechnete `NWMatrix`, obwohl wir sie nicht unbedingt brauchen, da die Daten so leichter inspiziert werden können.
Um aber die Übersichtlichkeit zu waren, wird sie später von der Stringrepräsentation ausgeschlossen.

``` {.haskell #type-aln-result}
data AlnResult = AlnResult
  { alnInfo  :: AlnInfo
  , nwMat    :: NWMatrix
  , optAlns  :: [Aln]
  , optScore :: Int
  } deriving Eq
```

Mit diesen Datentypen sind wir in der Lage Alignmentprobleme und deren Lösungen zu formulieren.

### Logik

Nachdem wir in der letzten Sektion die notwendigen Datentypen formuliert haben, können wir jetzt die eigentliche Programmlogik implementieren mithilfe derer wir Sequenzen alinieren.
Betrachten wir zunächst eine grobe Übersicht der Schritte, die wir unternehmen müssen um unser Alignmentproblem zu lösen:

1. Wir initialisieren die Matrix $F$ mit Rekursionsankern,
2. befüllen dann die restlichen Zellen von $F$ und
3. berechnen aus dem befüllten $F$ das optimale Alignment.

#### Initialisieren

Bevor wir die Matrix $F$ initialisieren, definieren wir einige Hilfsfunktionen um uns in Matrizen zu orientieren, darunter die $\mathrm{dist}_\mathrm{diag}$ Funktion und das davon abgeleitete Kriterium $\mathrm{range}$.

``` {.haskell #range-hs}
-- | Helper function to compute whether an alignment introduces too many gaps.
-- True if distance |i-j| from main diagonal is lesser or equal to allowed gaps.
distDiag :: MatIdx -> Int -> Bool
distDiag (i, j) gaps = abs (i-j) <= gaps

-- The distance criterion for candidate cell consideration.
range :: (Int, Int) -> MatIdx -> Bool
range (g1, g2) cell@(i, j)
  | i <= j    = distDiag cell g1
  | otherwise = distDiag cell g2
```

Mithilfe dieser Funktionen können wir die Befüllungsregeln für $f_{0j}$ und $f_{i0}$ festzulegen.

Zum Initialisieren benötigen wir die Rekursionsanker $f_{i0} = w_\text{gap} \cdot i$ und $f_{i0} = w_\text{gap} \cdot i$.[^haskell_one_based_idx]

[^haskell_one_based_idx]: Das `matrix` Paket indiziert Matrizen ab $1$ und nicht ab $0$, weswegen sich alle $i, j$ entsprechend verschieben.

``` {.haskell #init-mat}
d1 :: MatIdx -> [StepDirection]
d1 (i, j)
  | i == 1 && j == 1 = []
  | i == 1           = [Horizontal]
  | j == 1           = [Vertical]
  | otherwise        = []

f1 :: Bool -> Int -> Int -> CellScore
f1 valid gap i = if valid
  then Just $ (i-1) * gap
  else Nothing

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

initMat :: AlnInfo -> NWMatrix
initMat info@(AlnInfo {weights = cost}) = matrix (m+1) (n+1) init
    where
      (m, n) = seqLengths info
      init   = initFillFunc cost (gapCounts info)
```

Mit `initFillFunc` haben wir den Rekursionsanker definiert, um $F$ zu initialisieren und mit `initMat` können wir ein initialisiertes $F$ berechnen.

```ghci
ghci> initMat info
┌                                                                       ┐
│   Just (0,[]) Just (-2,[←])       Nothing       Nothing       Nothing │
│ Just (-2,[↑])       Nothing       Nothing       Nothing       Nothing │
│ Just (-4,[↑])       Nothing       Nothing       Nothing       Nothing │
│       Nothing       Nothing       Nothing       Nothing       Nothing │
│       Nothing       Nothing       Nothing       Nothing       Nothing │
│       Nothing       Nothing       Nothing       Nothing       Nothing │
└                                                                       ┘
```

#### Berechnen

Um $F$ zu befüllen müssen wir u.a. in der Lage sein die Kandidatenschritte für eine bestimmte Zelle $f_{ij}$ zu bestimmen.
Dafür können wir mithilfe `range` testen, welche der potentiellen Vorgänger aus $C_{ij}$ für die Zelle $f_{ij}$ infrage kommen.

``` {.haskell #candidates-hs}
-- | Find potential candidate cells, from which f_ij may be derived.
candidates :: (Int, Int) -> MatIdx -> [MatIdx]
candidates gaps cell@(i, j) = filter valid [d, h, v]
    where
      valid = range gaps :: (MatIdx -> Bool)

      d = (i-1, j-1)
      v = (i-1, j  )
      h = (i  , j-1)
```

Für bekannte Gapzahlen können wir uns nun die indizes potentiell valider Vorgänger ausgeben lassen.

```ghci
ghci> let gaps = (1, 2)
ghci> candidates gaps (4, 3)
[(3,2),(4,2),(3,3)]
ghci> candidates gaps (2, 3)
[(1,2),(2,2)]
ghci> candidates gaps (3, 7)
[]
```

Auch wenn wir jetzt mit `candidates` die Kandidaten für eine Zelle finden können, erlaubt uns dies alleine noch nicht Zellen in $F$ zu befüllen.

Dafür müssen wir den besten Kandidaten bestimmen.
Um den besten Kandidaten zu wählen, brauchen wir zunächst das Gewicht $w_{ij}$, bzw. $w_\text{gap}$ für einen Schritt $q_k$.

``` {.haskell #weight}
-- | Calculate the weight of a substitution.
substWeight :: (Eq a) => Cost -> (a, a) -> Int
substWeight (Cost {w_match = match, w_miss = miss}) (s1, s2)
  | s1 == s2  = match
  | otherwise = miss

-- | Calculate the weight of a step.
stepWeight :: AlnInfo -> Step -> Int
stepWeight (AlnInfo {weights = cost, seqA = s1, seqB = s2}) ((g, h), (i, j))
  | subst     = substWeight cost (s1 ! i, s2 ! j)
  | otherwise = w_gap cost
    where
      subst   =  i == g + 1
              && j == h + 1
```

Die Substitutionskosten sind ziemlich trivial.

```ghci
ghci> let cost = weights info
ghci> substWeight cost ('a', 'a')
1
ghci> substWeight cost ('x', 'y')
-1
```

Die `stepWeight` Funktion erlaubt es uns allerdings bereits Schrittgewichte zu bestimmen.

```ghci
ghci> let diagA = ((3, 2), (4, 3))
ghci> let diagB = ((2, 2), (3, 3))
ghci> let vert  = ((2, 2), (2, 3))
ghci> let hori  = ((2, 2), (3, 2))
ghci> stepWeight info diagA
1
ghci> stepWeight info diagB
-1
ghci> stepWeight info vert
-2
ghci> stepWeight info hori
-2
```

Anhand der Schrittgewichte können wir nun versuchen die besten Kandidaten zu finden und daraus die Zellwerte bestimmen.

Dafür definieren wir weitere Helfer zum Umgang mit unseren Daten.

``` {.haskell #max-helpers}
-- | Score a candidate step.
stepScore :: AlnInfo -> NWMatrix -> Step -> ScoredStep
stepScore info mat step@(candidate, cell) = (score, dir)
    where
      val   = getFrom mat candidate :: CellValue
      w_q   = stepWeight info step  :: Int
      score = fmap ((+w_q).fst) val :: CellScore
      dir   = fromStep step         :: StepDirection

-- | Find the highest candidate score.
maxCellScore :: [ScoredStep] -> CellScore
maxCellScore steps = max' Nothing steps
  where
    max' :: CellScore -> [ScoredStep] -> CellScore
    max' accum [] = accum
    max' accum ((s,_):sc)
      | s > accum = max' s sc
      | otherwise = max' accum sc

-- | Collect candidate steps with a specific candidate score.
filterSteps :: Maybe Int -> [ScoredStep] -> [StepDirection]
filterSteps _ [] = []
filterSteps m ((s, d):sc)
  | s == m    = d : filterSteps m sc
  | otherwise =     filterSteps m sc

-- | Helper to create a cell value from a candidate score
-- and a list of steps, by "lifting" the steps into the Maybe.
toValue :: CellScore -> [StepDirection] -> CellValue
toValue  Nothing  _ = Nothing
toValue (Just v) ds = Just (v, ds)
```

1. `stepScore` bildet die `ScoredStep` Tupel für unsere Kandidaten,
2. `maxCellScore` bestimmt aus diesen Tupeln den höchsten Kandidatenwert,
3. `filterSteps` bildet Liste aller `StepDirections` aus den Kandidatentupeln, die den mit `maxCellScore` gefundenen Wert haben und
4. `toValue` baut uns aus diesen beiden Teilen einen Zellwert zusammen, den wir in eine `NWMatrix` Schreiben können.

Jetzt können wir diese Arbeitsschritte zu einer `maxValue` Funktion zusammensetzen.

``` {.haskell #max-val}
-- | Given weighted step directions, find the optimal cell value.
maxValue :: [ScoredStep] -> CellValue
maxValue steps = max `seq` dirs `seq`  -- use seq to force strict evaluation 
  toValue max dirs
    where
      max  = maxCellScore steps
      dirs = filterSteps max steps
```

Jetzt, wo wir in der Lage sind, den optimalen Zellwert aus einer Liste von Kandidaten zu bestimmen, können wir auch damit beginnen die Matrix zu befüllen.

Dazu bilden wir, mithilfe der `stepScore` Funktion, die Liste von `(Maybe Int, StepDirection)` Tupeln aller Kandidaten und bestimmen mit `maxValDirs` den Zellwert.

``` {.haskell #fill-cell}
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

Um $F$ zu befüllen, gehen wir nun von links nach rechts und von oben nach unten durch die Matrix und füllen die einzelnen Zellen.

Um den Index der nächsten legalen Zelle zu finden, definieren wir die Funktion `nextCell`.
Da eine Rückgabe optional und sogar sinnlos ist, wenn wir z.B. in der letzten Zelle angekommen sind, nutzen wir auch hier wieder die `Maybe` Monade.
Die Funktion sollte einen `MatIdx` nehmen und dafür ggf. einen Nachfolger berechnen, also `Maybe MatIdx` zurückgeben.

``` {.haskell #next-cell}
-- | Compute the index of the next cell to calculate.
nextCell :: AlnInfo -> MatIdx -> Maybe MatIdx
nextCell info cell@(i, j)
  | incCol    = Just nxcol
  | incRow    = Just nxrow
  | otherwise = Nothing
    where
      (m, n)   = seqLengths info
      (g1, g2) = (gapCounts info)
      valid    = range (g1, g2)

      nxcol    = (i  , j+1)
      nxrow    = (i+1, max 2 (i+1 - g2))  -- max 2 (i+1 - g2) clamps the col idx
      incCol   = j < n+1 && valid nxcol
      incRow   = i < m+1 && valid nxrow
```

`nextCell` implementiert [Reihenfolge der Berechnungen]({#nw_order_of_calculations_partial), die wir zuvor schon graphisch dargestellt hatten.

Wenn wir den Rand der Matrix erreichen, oder zu einer Zelle kommen, welche aufgrund zu vieler notwendiger Gaps illegal wäre, springen wir zur ersten legalen Zelle der nächsten Zeile.
Falls wir uns in der letzten Zeile befinden, sind wir fertig und müssen keinen weiteren Index zurückgeben.

::: aside

Auf dieser Basis ließe sich leicht eine Funktion `iterMat` definieren, welche eine Liste der Matrixindizes in der Reihenfolge der Berechnung zurückgibt.

``` 
iterMat :: AlnInfo -> MatIdx -> [MatIdx]
iterMat info cell =
  case nextCell info cell of
    Just next -> cell : iterMat info next
    Nothing   -> [cell]
```

Wir bekommen als Reihenfolge ab $f_{43}$:

```ghci
ghci> iterMat info (4, 3)
[(4,3),(4,4),(4,5),(5,3),(5,4),(5,5),(6,4),(6,5)]
```

Nun ließen sich leicht Funktionen für alle Zellindizes ausführen indem man über das Ergebnis von `iterMat`  mappt, oder faltet, was konzeptionell[^theory_v_practice] ungefähr so aussehen könnte:

[^theory_v_practice]: Der gezeigte Code produziert noch kein korrektes Ergebnis und soll nur zur Veranschaulichung der Idee dienen.

```haskell
fill' info = foldr (fillCell info) mat idxs
  where
    mat  = initMat info
    idxs = iterMat info (2, 2)
```

Wir werden diesen Weg allerdings nicht gehen, sondern simple Rekursion nutzen.
:::

Jetzt befüllen wir die restlichen Einträge in $F$, indem wir bei einer Zelle, mit initialisierten Vorgängerkandidaten, starten, diese befüllen und solange es eine nächste valide Zelle gibt mit dieser weitermachen.
Wenn es keine Zellen mehr gibt, die wir befüllen müssen, sind wir fertig.

``` {.haskell #fill-from}
-- | Given AlnInfo, a matrix index and an NWMatrix with the
-- previous indices filled, fill the rest of the matrix,
-- beginning at the given index.
fillFrom :: AlnInfo -> MatIdx -> NWMatrix -> NWMatrix
fillFrom info cell mat  = next `seq` m `seq` -- use `seq` to force strict evaluation
  case next of
    Nothing    -> m                     -- last cell  -> fill cell and return
    Just next  -> fillFrom info next m  -- cells left -> fill cell and continue
  where
    next = nextCell info cell
    m    = fillCell info cell mat
```

Wir können nun eine `NWMatrix` mit `initMat` initialisieren und diese dann mit `fillFrom` befüllen.

Damit können wir $F$ auf Basis eines `AlnInfo` Records berechnen, indem wir die initialisierte Matrix ab $(2, 2)$[^nw_index_shift]  befüllen.

[^nw_index_shift]: Wir erinnern uns, dass wir eine Indexverschiebung, aufgrund der eins-basierten Indizierung von Matrizen, haben.

``` {.haskell #fill}
fill :: AlnInfo -> NWMatrix
fill info = let mat = initMat info
            in mat `seq` fillFrom info (2, 2) mat
            where counts = gapCounts info
```

Mit der `fill` Funktion können wir nun die Matrix befüllen.

```ghci
ghci> let mat = fill info
ghci> mat
┌                                                                                 ┐
│     Just (0,[])   Just (-2,[←])         Nothing         Nothing         Nothing │
│   Just (-2,[↑])    Just (1,[↖])   Just (-1,[←])         Nothing         Nothing │
│   Just (-4,[↑])   Just (-1,[↑])    Just (0,[↖])    Just (0,[↖])         Nothing │
│         Nothing   Just (-3,[↑])    Just (0,[↖])   Just (-1,[↖])   Just (-1,[↖]) │
│         Nothing         Nothing   Just (-2,[↑])   Just (-1,[↖])   Just (-2,[↖]) │
│         Nothing         Nothing         Nothing Just (-3,[↖,↑])    Just (0,[↖]) │
└                                                                                 ┘
```

Das Ergebnis entspricht [unseren Erwartungen](#nw_fig_partial).

#### Backtracken

Jetzt müssen wir aus der Matrix die Liste der Pfade von $(1, 1)$ nach $(M+1, N+1)$ extrahieren.
Dieser Prozess wird als "Backtracken" bezeichnet.
Aus diesen Pfaden ergeben sich die optimalen Alignments unserer Sequenzen.

Dazu definieren wir zunächst geeignete Funktionen, um Indizes und `StepDirection` Werte in die, durch die Richtungen bezeichneten, Vorgängerindizes zu überführen.

```{.haskell #origs}
-- | Calculate the origin of a StepDirection from a particular position.
getOrig :: MatIdx -> StepDirection -> MatIdx
getOrig dest@(i, j) Diagonal   = (i-1, j-1)
getOrig dest@(i, j) Horizontal = (i  , j-1)
getOrig dest@(i, j) Vertical   = (i-1, j  )

origs :: MatIdx -> CellValue -> [MatIdx]
origs cell@(i, j) elem =
  case elem of
    Nothing        -> []
    Just (_, dirs) -> map (getOrig cell) dirs
```

Jetzt können wir Backtracken.
Dafür bilden wir die Pfade von $(M+1, N+1)$ zum Ursprung $(1, 1)$, wobei wir rekursiv vorgehen.

Wenn wir die Menge der Pfade vom Ursprung zu sich selbst betrachten, dann sehen wir, dass diese nur den Pfad der Länge $1$, beinhaltet, der aus dem Ursprung selbst besteht.
Die Pfade von einer beliebigen Zelle zum Ursprung ergeben sich, indem wir die betrachtete Zelle an die Pfade ihrer Vorgänger anfügen.
Wegen des Aufbaus der Matrix müssen alle Pfade irgendwann im Ursprung enden.

Aufgrund der Performancecharakteristika[^list_prepend_append] von Listen in Haskell berechnen wir die Pfade von hinten nach vorne.

[^list_prepend_append]: Vorne Anfügen hat Laufzeit $\mathcal{O}(1)$, aber hinten Anfügen hat Laufzeit $\mathcal{O}(n)$.

``` {.haskell #find-rev-paths}
-- | Helper for backtracking, that determines the
-- (reverse) matrix paths for a given index.
findRevPaths :: NWMatrix -> MatIdx -> [Path]
findRevPaths _ (1, 1) = [[(1, 1)]]
findRevPaths mat cell@(i, j) = (prepend.collect.continue) cellOrigs
  where
    elem :: CellValue
    elem = getFrom mat cell

    cellOrigs = origs cell elem
    continue = map (findRevPaths mat)
    collect = concat
    prepend = map (cell:)
```

::: warning
Die Implementation des Backtrackings ist durch die genutzte Rekursion zwar elegant gelöst, aber nicht sehr performant.

Mehr dazu findet sich im [Diskussionsteil](#space_analysis).
:::

Versuchen wir bspw. den Pfeilen aus Zelle `(4, 2)`, mit Wert `Just (-3,[↑])`, zum Ursprung zu folgen.

```ghci
ghci> mat
┌                                                                                 ┐
│     Just (0,[])   Just (-2,[←])         Nothing         Nothing         Nothing │
│   Just (-2,[↑])    Just (1,[↖])   Just (-1,[←])         Nothing         Nothing │
│   Just (-4,[↑])   Just (-1,[↑])    Just (0,[↖])    Just (0,[↖])         Nothing │
│         Nothing   Just (-3,[↑])    Just (0,[↖])   Just (-1,[↖])   Just (-1,[↖]) │
│         Nothing         Nothing   Just (-2,[↑])   Just (-1,[↖])   Just (-2,[↖]) │
│         Nothing         Nothing         Nothing Just (-3,[↖,↑])    Just (0,[↖]) │
└                                                                                 ┘
ghci> let revpaths = findRevPaths mat (4, 2)
ghci> revpaths
[[(4,2),(3,2),(2,2),(1,1)]]
```

Wie erwartet finden wir ein Alignment, mit zwei Schritten nach oben gefolgt von einem Schritt in der Diagonalen.

Aus den Pfaden ergeben sich die eigentlichen Alignments.
Um einen Pfad in ein Alignment umzuwandeln, müssen wir für jeden Index $(i, j)$ im Pfad, die relevanten Symbole $s^1_i$ und $s^2_j$ bestimmen und dann anhand der Schrittrichtung bestimmen, wo wir die Symbole, bzw. Gaps einbauen.

``` {.haskell #convert-path}
-- | Compute the alignment of two sequences from a matrix path.
convertPath :: SeqArr -> SeqArr -> Path -> Aln
convertPath _ _ [] = []
convertPath _ _ [p] = []
convertPath s1 s2 (p@(g, h):p'@(i, j):ps) =
  case dir of
    Diagonal   -> (sym1, sym2) : rest
    Horizontal -> (Gap , sym2) : rest
    Vertical   -> (sym1, Gap ) : rest
  where
    dir  = fromStep (p, p')
    sym1 = Symbol (s1 ! i)
    sym2 = Symbol (s2 ! j)
    rest = convertPath s1 s2 (p':ps)
```

Damit sind wir in der Lage die Pfade aus einer Matrix zu bestimmen und diese in Alignments umzuwandeln.
Den zuvor bestimmten Pfad müssen wir natürlich vorher noch umdrehen.

```ghci
ghci> let path = (reverse.head) revpaths
ghci> let AlnInfo {seqA = s1, seqB = s2} = info
ghci> convertPath s1 s2 path
[('A','A'),('G','-'),('T','-')]
```

Mithilfe dieser Bausteine können wir eine `backtrack` Funktion definieren, welche aus einer gefüllten NW-Matrix für zwei Sequenzen die optimalen Alignments bestimmt.

``` {.haskell #backtrack}
-- | Given a filled in NWMatrix for two sequences,
-- determine the optimal alignments.
backtrack :: NWMatrix -> SeqArr -> SeqArr -> [Aln]
backtrack mat s1 s2 = map (convertPath s1 s2) paths
  where
    revpaths = findRevPaths mat (nrows mat, ncols mat)
    paths = map reverse revpaths
```

Für die Beispielsequenzen bekommen wir die üblichen Ergebnisse.
Versuchen wir also zusätzlich ein Beispiel mit mehreren gleichwertigen Alignments.
Dafür nehmen wir die Sequenzen $\mathrm{AGTG}$ und $\mathrm{AAGTCC}$, mit denselben Kosten und derselben Gapzahl.

```ghci
ghci> backtrack mat s1 s2
[[('A','A'),('G','-'),('T','T'),('A','G'),('C','C')]]
```

#### Kombinieren

Wenn wir zuerst die Matrix $F$ befüllen und dann aus dem befüllten $F$ die Alignments bestimmen haben wir das Alignmentproblem lösen.

Dazu definieren wir eine entsprechende `align` Funktion.

``` {.haskell #align}
align :: AlnInfo -> AlnResult
align info@(AlnInfo {seqA = s1, seqB = s2}) =
  case maybeScore of
    Just (score, _)  -> AlnResult info mat alns score
    Nothing -> error "global alignment is undefined"
  where
    mat = fill info
    alns = backtrack mat s1 s2
    maybeScore = getFrom mat (nrows mat, ncols mat)
```

Jetzt können wir mit `align` den gesamten Prozess laufen lassen und bekommen einen `AlnResult` Wert zurück.

```ghci
ghci> let res = align info
ghci> res
AlnResult { alnInfo = AlnInfo {g_max = 1, weights = Cost {w_match = 1, w_miss = -1, w_gap = -2}, seqA = array (2,6) [(2,'A'),(3,'G'),(4,'T'),(5,'A'),(6,'C')], seqB = array (2,5) [(2,'A'),(3,'T'),(4,'G'),(5,'C')]}, optAlns = [[('A','A'),('G','-'),('T','T'),('A','G'),('C','C')]], optScore = 0 }
```

Das Problem mag zwar gelöst sein, aber die Übersichtlichkeit lässt noch zu wünschen übrig.

### Repräsentation

Wir können durch das Anhängen von `deriving Show` an Datentypdefinitionen durch Haskell automatisch Repräsentationsfunktionen generieren lassen.
Die so generierte Darstellung ist allerdings nicht gut für den menschlichen Genuss geeignet.

Stattdessen wollen wir ein paar eigene Repräsentationsfunktionen zur textuellen Darstellung definieren.
Z.b. `showResult`, um `AlnResult` Werte menschenlesbar zu formatieren.

```ghci
ghci> putStrLn $ showResult res
Given a pairwise alignment problem with the following key data:

  g_max   = 1
  w_match = 1
  w_miss  = -1
  w_gap   = -2
  seqA    = "AGTAC"
  seqB    = "ATGC"


The problem is optimally solved by the following 1 global alignment(s),
with score 0:

AGTAC
|-|.|
A-TGC
```

Wie machen wir das?

#### Alignment Info

Beginnen wir mit den grundlegendsten Werten, nämlich dem `AlnInfo` Datentyp.
Da wir am Ende auch die Eckdaten des gelösten Problems zusammenfassen wollen, ergibt eine ansprechendere Darstellung hier Sinn.

``` {.haskell #show-aln-info}
showInfo info@(AlnInfo {g_max = g_max', weights = cost, seqA = s1, seqB = s2})
    =  "  g_max   = " ++ show g_max'          ++ "\n"
    ++ "  w_match = " ++ (show.w_match) cost  ++ "\n"
    ++ "  w_miss  = " ++ (show.w_miss) cost   ++ "\n"
    ++ "  w_gap   = " ++ (show.w_gap) cost    ++ "\n"
    ++ "  seqA    = " ++ showSeq s1           ++ "\n"
    ++ "  seqB    = " ++ showSeq s2           ++ "\n"
    where
      showSeq = show.elems
```

Wir beschränken uns auf eine zeilenweise Ausgabe der Daten, wobei wir die einzelnen Gewichte für die Darstellung extrahieren.

```ghci
ghci> putStrLn $ showInfo info
  g_max   = 1
  w_match = 1
  w_miss  = -1
  w_gap   = -2
  seqA    = "AGTAC"
  seqB    = "ATGC"
```

#### Schritte

Für `StepDirection` Werte nutzen wir einfach Pfeilsymbole.

``` {.haskell #show-steps}
-- | Use arrow symbols to display step directions.
instance Show StepDirection where
  show Diagonal = "↖"
  show Horizontal = "←"
  show Vertical = "↑"
```

#### Alignments

Für Alignments (`type Aln = [(AlnChar, AlnChar)]`) wollen wir eine ähnliche Darstellung wählen, wie die vom Biopython-Projekt [@biopython] genutzte Darstellung paarweiser Sequenzalignments.

Dabei werden die Buchstaben des Alignments getrennt durch ein Symbol untereinander geschrieben.
Welches Symbol verwendet wird hängt davon ab, ob es sich um Match, Missmatch oder Gap handelt.[^aln_repr_symbol]

[^aln_repr_symbol]: Bei Match `|`, bei Missmatch `.` und bei Gap `-`.

##### Alignment Symbole

`AlnChar` Werte werden, im Falle von Symbolen einfach so dargestellt wie die Buchstaben selbst, bzw. bei Gaps als `-`.

``` {.haskell #show-aln-char}
toChar :: AlnChar -> Char
toChar Gap        = '-'
toChar (Symbol c) = c

instance Show (AlnChar) where
  show = show.toChar
  showList xs ys = showList (map toChar xs) ys
```

Mit `toChar` können wir `AlnChar` Werte wieder zu Buchstaben machen.
Dies nutzen wir um unsere Anzeigelogik einfach von der `show` Funktion für `Char` abzuleiten.

::: info
Die `showList` Funktion ermöglicht die besondere Formatierung von Listendarstellungen.
Z.b. sind Strings als Listen von Chars definiert, also `type String = [Char]`, werden aber nicht als solche dargestellt.

Die Standardrepräsentation für Listen nutzt eckige Klammern.
Daher sähe die Liste von Buchstaben die dem String "hello world!" entsprechen normalerweise so aus:

```haskell
['h','e','l','l','o',' ','w','o','r','l','d','!']
```

Aber, da `Char`s Typenklassen-Instanz für `Show`  die `showList` Funktion definiert, wird dieser String als `"hello world!"` dargestellt.
:::

##### Formatierung

Jetzt wo wir `AlnChar` Werte darstellen können definieren wir Hilfsfunktionen um  Match- Missmatch- und Gapsymbole zu generieren und mit Zeilenumbrüchen fertig zu werden.

``` {.haskell #show-aln}
-- | Produce the proper signifier for two aligned symbols.
-- I.e., '-' for gaps, '|' for matches, and '.' for missmatches.
tag :: (AlnChar, AlnChar) -> Char
tag (Gap, Gap) = '-'
tag (  _, Gap) = '-'
tag (Gap,   _) = '-'
tag (x, y)
  | x == y     = '|'
  | otherwise  = '.'

-- | Helper for calculating lines in the string representation of an Aln.
breakAlnLines :: Int -> [String] -> [String]
breakAlnLines _     []      = []
breakAlnLines width strings = partlines : breakAlnLines width rest
  where
    (parts, rests) = unzip $ map (splitAt width) strings
    rest           = filter (not.null) rests
    break          = concat.(intersperse "\n")
    end            = if null rest then "" else "\n\n"
    partlines      = break parts ++ end
```

Mit `tag` können wir die korrekten Symbole für die Alignmentpositionen bestimmen und `breakAlnLines` bricht diese sauber in Zeilen um.

::: info
Die `intersperse` Funktion nimmt einen Wert und eine Liste von Werten desselben Typs und fügt den übergebenen Wert zwischen den Listenelementen ein.
Da `intersperse` kein Teil des `Prelude`, dem automatisch importierten Teil der Standardbibliothek, ist, müssen wir diese noch importieren.

``` {.haskell #align-imports}
import Data.List (intersperse)
```

Mit diesen Helfern können wir geeignete Repräsentationsfunktionen schreiben.
:::

#### Alignmentdarstellung

Nun können wir die `tag` und `breakAln` Funktionen zusammensetzen um eine Darstellung für Alignments zu generieren.
Dabei möchten wir, dass Alignments nach 80 Zeichen[^terminal_width] umbrechen.

[^terminal_width]: Die Standardbreite für Terminals beträgt, auch heute noch, 80 Spalten, da die Lochkarten von IBM 12x80 Format hatten.

``` {.haskell #show-aln-helpers}
-- | Pretty print an alignment. This does not take terminal width into account,
-- but simply wraps after 80 symbols.
showAln :: Aln -> String
showAln aln = (concat.breakAlnLines 80) [r1, syms, r2]
    where
      syms     = map tag aln
      (s1, s2) = unzip aln
      [r1, r2] = map (map toChar) [s1, s2]

-- | Pretty print a list of alignments. Wraps the same way as showAln does.
showAlns :: [Aln] -> String
showAlns = concat.(intersperse "\n\n\n").(map showAln)
```

Mit `showAlns` stellen wir Alignments nun in menschenlesbarer Form dar.

```ghci
ghci> let aln = (head.optAlns) res
ghci> showAln aln
"AGTAC\\n|-|.|\\nA-TGC"
ghci> let longaln = ((take 120).cycle) aln
ghci> putStrLn $ showAln longaln
AGTACAGTACAGTACAGTACAGTACAGTACAGTACAGTACAGTACAGTACAGTACAGTACAGTACAGTACAGTACAGTAC
|-|.||-|.||-|.||-|.||-|.||-|.||-|.||-|.||-|.||-|.||-|.||-|.||-|.||-|.||-|.||-|.|
A-TGCA-TGCA-TGCA-TGCA-TGCA-TGCA-TGCA-TGCA-TGCA-TGCA-TGCA-TGCA-TGCA-TGCA-TGCA-TGC

AGTACAGTACAGTACAGTACAGTACAGTACAGTACAGTAC
|-|.||-|.||-|.||-|.||-|.||-|.||-|.||-|.|
A-TGCA-TGCA-TGCA-TGCA-TGCA-TGCA-TGCA-TGC
```

Wir sehen, dass bei einem Alignment mit 120 Zeichen nach der 80. Spalte ein Umbruch eingebaut wird.

#### Alignment Ergebnisse

Jetzt da wir Alignments sauber darstellen können beschäftigen wir uns mit der Repräsentation des Gesamtergebnisses.
Dafür definieren wir die Funktion `showResult`, welche uns eine gut menschenlesbare Textdarstellung generieren soll.

Wir haben außerdem in `AlnResult` die errechnete `NWMatrix` gespeichert.
Dies würde, besonders bei größeren Matrizen, zu einer wenig übersichtlichen Darstellung führen, weswegen wir das `nwMat` Feld aus der Standarddarstellung ausschließen.

``` {.haskell #show-aln-result}
showResult :: AlnResult -> String
showResult (AlnResult {alnInfo = info, nwMat = mat, optAlns = alns, optScore = score})
    = "Given a pairwise alignment problem with the following key data:\n\n"
    ++ showInfo info ++ "\n\n"
    ++ "The problem is optimally solved by the following "
    ++ (show.length) alns ++ " global alignment(s),\n"
    ++ "with score " ++ show score ++ ":\n\n"
    ++ showAlns alns

-- | Exclude the nwMat field from the show representation.
instance Show AlnResult where
  show (AlnResult {alnInfo = info, optAlns = alns, optScore = score})
    = "AlnResult { "
    ++   "alnInfo = "  ++ show info
    ++ ", optAlns = "  ++ show alns
    ++ ", optScore = " ++ show score
    ++ " }"
```

Nun bekommen wir das Ergebnis in einer Form präsentiert, die einen schnellen Überblick ermöglicht.

```ghci
ghci> putStrLn $ showResult res
Given a pairwise alignment problem with the following key data:

  g_max   = 1
  w_match = 1
  w_miss  = -1
  w_gap   = -2
  seqA    = "AGTAC"
  seqB    = "ATGC"


The problem is optimally solved by the following 1 global alignment(s),
with score 0:

AGTAC
|-|.|
A-TGC
```

## Ausführung

Um die definierten Funktionen für Anwender nutzbar zu machen, bedarf es ein wenig mehr als nur Datentypen, Logik und Repräsentationsfunktionen.
Irgendwie müssen Nutzer die Software starten und Eingaben vornehmen können.
Der GHCi-REPL ist dafür nur bedingt geeignet.

Beim Start eines Haskell Programms, wird die Funktion `main` ausgeführt.
Diese hat den Typ `IO ()`, was bedeutet, dass sie mit Nebeneffekten belastete Ein- und Ausgaben durchführt und keinen Wert zurückgibt.
Wie `Maybe`, ist auch `IO` eine Monade.

Unsere `main` Funktion soll die Kommandozeilenargumente lesen und dann, wenn welche übergeben wurden, die Anwendungslogik mit diesen ausführen oder, wenn keine übergeben wurden, interaktiv danach fragen.

``` {.haskell #main}
main :: IO ()
main = do
    args <- getArgs
    let action = if (not.null) args
        then runArgs
        else runInteractive
    result <- action args
    putStrLn $ showResult result
```

### CLI Argumente

Nutzer sollen das Programm in einer Shell starten und die notwendigen Argumente beim Aufruf übergeben können.

Wir erwarten genau 5 Argumente.
Das erste ist ein Pfad zu einer FASTA-Datei mit mindestens 2 Sequenzen, das zweite ist die Anzahl zulässiger Gaps $\mathfrak{g}_\text{max}$ und die folgenden sind die Kosten, in der Reihenfolge $w_\text{match}$, $w_\text{miss}$ und $w_\text{gap}$.

``` {.haskell #run-args}
-- | Cast a String to an Int.
toInt :: String -> Int
toInt = read :: String -> Int

-- | Run the application from a list of command line arguments.
runArgs :: [String] -> IO AlnResult
runArgs (fp:g_maxArg:w_matchArg:w_missArg:w_gapArg:restArgs) = do
    -- parse file and unpack contents
    fastas <- readFasta fp
    let ((h1, s1):(h2, s2):restFastas) = fastas

    -- cast and unpack int args
    let intArgs = map toInt [g_maxArg, w_matchArg, w_missArg, w_gapArg]
    let [g_max, match, miss, gap] = intArgs

    -- build input data and align sequences
    let info = mkInfo g_max match miss gap s1 s2
    return $ align info
```

Die `runArgs` Funktion erwartet also die Argumente

1. Dateipfad zu FASTA,
2. $\mathfrak{g}_\text{max}$,
3. $w_\text{match}$,
4. $w_\text{miss}$ und
5. $w_\text{gap}$

und kann nun genutzt werden um Sequenzen zu alinieren.

### Interaktiv

Falls ein Nutzer zur Übergabe der Argumente nicht die Kommandozeile nutzen will, definieren wir eine Funktion um diese stattdessen interaktiv übergeben zu können.

``` {.haskell #run-interactive}
runInteractive :: [String] -> IO AlnResult
runInteractive _ = do
    info <- askInfo
    return $ align info
```

Dafür brauchen wir eine Funktion um aus den übergebenen Werten einen `AlnInfo` Record zu bilden.

``` {.haskell #ask-info}
askInfo :: IO AlnInfo
askInfo = do
    putStrLn "Provide a path to a FASTA file containing at least two sequences."
    fp <- getLine
    ((h1, s1):(h2, s2):restFastas) <- readFasta fp

    putStrLn "How many gaps are allowed in the alignment?"
    g_maxStr <- getLine
    let g_max = read g_maxStr :: Int

    putStrLn "Weight of matches, mismatches and gaps?"
    putStrLn "(Seperate input by commas.)"
    weightStr <- getLine
    let weights = tokenize weightStr
    let [w_match, w_miss, w_gap] = map (read :: String -> Int) weights

    return $ mkInfo g_max w_match w_miss w_gap s1 s2
```

Und einige Helfer um mit Nutzereingaben umzugehen.

``` {.haskell #ask-helpers}
-- | Helper to split strings on a specific character.
split :: Char -> String -> [String]
split c xs = reverse $ split' [] "" xs
  where
    split' :: [String] -> String -> String -> [String]
    split' accum curr [] = curr:accum
    split' accum curr [x] = accum
    split' accum curr (x:xs)
      | x == c    = split' (curr:accum) "" xs
      | otherwise = split' accum (x:curr) xs

-- | Helper to discard leading and trailing whitespace from a string.
strip :: String -> String
strip = rstrip.lstrip
  where
    lstrip [] = []
    lstrip (x:xs)
      | x == ' ' = lstrip xs
      | otherwise = (x:xs)

    rstrip = reverse.lstrip.reverse

tokenize :: String -> [String]
tokenize s = map strip $ split ',' s
```

### Parsen

Nutzer sollen Sequenzen i.F.v. Dateien übergeben können.
Definieren wir also eine Funktion, die einen Pfad zu einer FASTA-Datei nimmt und deren Sequenzen zurückgibt.

``` {.haskell #read-fasta}
-- | Convert a FastaSequence into a (header, sequence) tuple.
tuplify :: FastaSequence -> (String, String)
tuplify FastaSequence{ fastaHeader = h, fastaSeq = s } = (h, s)

-- | Read a FASTA file located at the given path, and produce a list of (header, sequence) tuples.
readFasta :: String -> IO [(String, String)]
readFasta path = do
    fastaString <- readFile path
    let fastas = parseFasta fastaString

    return $ map tuplify fastas
```

Wir nutzen hier das 3rd-Party Modul `fasta`.
Dieses muss installiert sein, damit der Code funktioniert.

## Modularisierung

Ein zentraler Zweck des Software-Engineerings ist es, die Komplexität von Softwarelösungen zu managen.
Wichtige Techniken dafür sind Modularisierung und Hierarchisierung.

Nun fassen wir die definierten Blöcke mit den Funktionen und Datentypen im  `Align.Naive.Data` Modul zusammen.

Bei der Modularisierung versuchen wir solche Teile des Systems in Komponenten zu bündeln, die ähnliche Zwecke haben und bei der Hierarchisierung versuchen wir eine konsistente (Halb-) Ordnung von Modulen und Submodulen zu bilden.

Unsere Software soll Sequenzen alinieren, weswegen es Sinn ergibt, sie zu einem `Align` Modul zusammenzufassen.
Wir haben eine naive und eine sinnvolle Lösung implementiert und Scaffolding-Code für Nutzereingaben geschrieben.
Diese können in `Align.Data` bzw. `Align.Naive.Data` gebündelt werden.
Das Hauptmodul kann dann zusätzlich `Align.Data` exportieren.

### Hauptmodul

Module in Haskell sind Deklarationen der Form `module Name (<exports>) where <code>`.
Ein Modul kann andere Submodule, die es importiert hat, exportieren.
So können Submodule definiert werden.

Wir definieren das Modul `Align` und brauchen die Submodule `Align.Data` und `Align.Naive.Data`.
Bevor wir mit `Align.Naive.Data` arbeiten können, müssen wir jedoch das `Align.Naive` Modul definieren.

Weiterhin soll `Align` beim import standardmäßig den Code in `Align.Data` verfügbar machen, nicht aber den in `Align.Naive`, da dies zu Namenskonflikten führen würde.
Um dies zu vermeiden, nutzen wir einen qualifizierten Import für `Align.Naive`.

``` {.haskell file=src/Align.hs}
module Align
    ( module Align.Data
    , module Align.Naive ) where

import Align.Data
import qualified Align.Naive
```

### Naives Modul

Dieses importiert einfach nur `Align.Naive.Data` und exportiert es dann wieder.
Der einzige Zweck dieses Umwegs ist es, ein konsistentes Namensschema für unsere Module zu ermöglichen.

``` {.haskell file=src/Align/Naive.hs}
module Align.Naive
    ( module Align.Naive.Data ) where

import Align.Naive.Data
```

Nun definieren wir das `Align.Naive.Data` Modul.
Dieses enthält die  naiven Datentypen und Funktionen zur Berechnung von Alignments.

``` {.haskell file=src/Align/Naive/Data.hs}
{-# LANGUAGE InstanceSigs #-}

module Align.Naive.Data where

import Align.Data (Cost(..))
import Data.Char (toUpper)
import Data.Traversable (Traversable, fmapDefault, foldMapDefault)

<<base>>
<<naive-seq>>
<<naive-seq-classes>>
<<aln-char>>
<<aln-seq>>
<<successor>>
<<combination>>
<<combinations>>
<<alignments>>
<<naive-aln>>
<<naive-align-helpers>>
<<naive-align>>
```

### Needleman-Wunsch Modul

Das Modul zum Berechnen von Alignments mithilfe von NW, hat den folgenden Aufbau:

``` {.haskell file=src/Align/Data.hs}
module Align.Data where

<<align-imports>>

<<types>>
<<helpers>>
<<computation>>
<<representations>>
```

Zunächst fassen wir die Typendeklarationen zusammen.

``` {.haskell #types}
-- DATA TYPES

<<type-cost>>
<<type-seq>>
<<type-seq-arr>>
<<type-aln-info>>
<<type-aln-result>>
<<type-mat-parts>>
<<type-nw-matrix>>
<<type-scores>>
```

Anschließend bündeln wir die Hilfsfunktionen, die wir später in den Berechnungen verwenden.

``` {.haskell #helpers}
-- HELPER FUNCTIONS

-- helpers for matrix computation
<<range-hs>>
<<candidates-hs>>
<<next-cell>>
<<weight>>
<<max-helpers>>
<<max-val>>

<<init-mat>>
<<fill-cell>>
<<fill-from>>

-- helpers for backtracking
<<origs>>
<<find-rev-paths>>
<<convert-path>>
```

Nun werden die eigentlichen Berechnungen zusammengefasst.

``` {.haskell #computation}
-- COMPUTATIONS

<<fill>>
<<backtrack>>
<<align>>
```

Auch die Repräsentationsfunktionen können wir gruppieren.

``` {.haskell #representations}
<<show-aln-char>>
<<show-steps>>
<<show-aln-info>>
<<show-aln-result>>
<<show-aln-helpers>>
<<show-aln>>
```

### Anwendungsmodule

Das Folgende muss nicht groß kommentiert werden.
Für die Anwendungslogik definieren wir ein `Main` Modul.

``` {.haskell file=app/Main.hs}
module Main where

import Align.Data (mkInfo, align, mkInfo, AlnInfo (..), showResult, AlnResult (..))
import Data.Fasta.String.Parse (parseFasta)
import Data.Fasta.String.Types (FastaSequence (..))
import System.Environment (getArgs)

<<read-fasta>>

<<run-args>>

<<ask-helpers>>
<<ask-info>>
<<run-interactive>>

<<main>>
```

## Paketierung

Haskell-Projekte können mithilfe der *Common Architecture for Building Applications and Libraries* (**Cabal**) gebaut und paketiert werden.
Dafür wird eine `project.cabal`{.bare} Datei im Project-Root angelegt.

::: info
Im Folgenden wird der Aufbau eines Cabal-Files im literarischen Programmierstil erklärt.
Da Cabal allerdings keine Kommentare vor der Versionsangabe akzeptiert und Entangle[^entangle] Kommentare nutzt, um Codeblöcke auseinanderzuhalten, produziert dieses Beispiel keine validen Dateien.

[^entangle]: Das Tool, welches das Generieren von Source-Dateien, aus Fließtext mit eingewobenen Codeblöcken, ermöglicht.

Aus diesem Grund wurde dem Projekt mit der `seafovl.cabal`{.bare} Datei ein valides, manuell geschriebenes, Cabal-File, mit identischem Inhalt, beigefügt.
:::

Der Aufbau eines Cabal-Files sieht folgendermaßen aus:

``` {.cabal #seafovl.cabal}
cabal-version:      3.4

<<cabal-info>>

common common-options
    default-language: Haskell2010
    ghc-options: -Wall -O +RTS -sstderr

<<cabal-library>>
<<cabal-executable>>
```

Nach einer Präambel mit der Cabal-Version, folgen allgemeine Projektinformationen, Deklarationen von geteilten Optionen und Build-Targets.
Die Build-Targets können entweder ausführbare Dateien oder Libraries zum einbinden in anderen Projekten sein.

Die folgenden Eck-Daten beschreiben das Projekt:

``` {.cabal #cabal-info}
name:               seafovl
author:             Fynn Freyer
synopsis:           SEquence Aligner with Formally Verified Logic
description:        Seafovl is a formally verified sequence aligner.

license:            MIT
license-file:       LICENSE
copyright:          Copyright 2024 Fynn Freyer

-- Package version conforms to https://pvp.haskell.org
--       +-+------- breaking API changes
--       | | +----- non-breaking API additions
--       | | | +--- code changes with no API change
version: 0.1.0.0
maintainer:         fynn.freyer@student.htw-berlin.de

category:           Data
build-type:         Simple

extra-doc-files:    README.md,
                    CHANGELOG.md
```

Damit wir die Software bauen können, brauchen wir Build-Targets.
Von diesen können wir auch mehrere definieren.

Zum Einen wollen wir anderen Programmierern ermöglichen den geschriebenen Code in ihre eigenen Projekte einzubinden.
Dies entspricht einem `library`{.bare} Build.

Dabei müssen wir angeben welche Module unsere Bibliothek exportiert und von welchen externen Paketen sie abhängt.

``` {.cabal #cabal-library}
library
    import:           common-options
    exposed-modules:  Align,
                      Align.Data,
                      Align.Naive,
                      Align.Naive.Data,
    build-depends:    base   ^>=4.17.1.0,
                      array  ^>=0.5,
                      matrix ^>=0.3
    hs-source-dirs:   src
```

Zum Anderen sollen Nutzer die Software direkt ausführen können.
Dies entspricht einem `executable`{.bare} Build.

Dabei müssen wir zusätzlich zu den Abhängigkeiten, welche den zuvor definierten `library`{.bare} Build enthalten, angeben welche Datei die `main` Funktion enthält und ob ggf. weitere Module als das mit der `main` eingebunden werden sollen.

``` {.cabal #cabal-executable}
executable seafovl
    import:           common-options
    main-is:          Main.hs
    build-depends:    base   ^>=4.17.1.0,
                      fasta  ^>=0.10,
                      seafovl
    hs-source-dirs:   app
```

Nun können wir die Anwendung mit `cabal run`{.bare} kompilieren und starten.

## Test

Können wir mit NW nun auch längere Sequenzen verarbeiten?

### Testdaten

Im `assets/`{.bare} Ordner liegen die FASTA-Dateien `ins_prot.fa`{.bare}, `ins.fa`{.bare} und `pol.fa`{.bare}.

Die `ins.fa`{.bare} und `ins_prot.fa`{.bare} Dateien enthalten die DNA- und Aminosäuresequenzen des Insulin-Proteins von Menschen[^accession_ins_homo] und Dromedaren.[^accession_ins_camelus]
In beiden Organismen haben die Sequenzen dieselbe Länge.
Im Fall der DNA 331 Basen und bei den Proteinen 110 Aminosäuren.

[^accession_ins_homo]: Die Accession-Number ist [`AAA59172.1`{.bare}](https://www.ncbi.nlm.nih.gov/protein/AAA59172.1) für das Protein, bzw. [`AH002844.2`{.bare}](https://www.ncbi.nlm.nih.gov/nuccore/AH002844.2) mit Region `join(2424..2610,3397..3542)`{.bare} für die DNA.
[^accession_ins_camelus]: Die Accession-Number ist [`KAB1251309.1`{.bare}](https://www.ncbi.nlm.nih.gov/protein/KAB1251309.1/) für das Protein, bzw. [`JWIN03000075`{.bare}](https://www.ncbi.nlm.nih.gov/nuccore/JWIN03000075), mit Region `join(6667075..6667261,6667771..6667916)`{.bare} für die DNA.

Die `pol.fa`{.bare} Datei enthält Sequenzen der POL Region für das humane und simiane Immundefizienz-Virus (**HIV** und **SIV**), mit Längen von 2739, bzw. 3180, Basen.

### Insulin

Wir setzen für beide Dateien Kosten mit $w_\text{match} = 1, w_\text{miss} = -1$ und $w_\text{gap} = -2$.
Beim Alinieren der Aminosäuren erlauben wir  20 Gaps, bei der DNA 40.

::: info
Die folgenden Ausgaben sind gekürzt, wobei Auslassungen mit `...` kenntlich gemacht wurden.

Weiterhin wurde eine Messung mit `/usr/bin/time -p cmd` vorgenommen.
Diese soll nicht repräsentativ sein, sondern hat nur den Sinn dem Leser eine ungefähre Ahnung über die notwendige Ausführungszeit vermitteln.
Der angegebene Wert entspricht dem Wert `real`.
:::

```terminal
$ cabal run -- seafovl assets/ins_prot.fa 20 1 -1 -2
Given a pairwise alignment problem with the following key data:

  g_max   = 20
  w_match = 1
  w_miss  = -1
  w_gap   = -2
  seqA    = "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHL..."
  seqB    = "MALWTRLLALLALLALGAPTPARAFANQHLCGSHL..."


The problem is optimally solved by the following 1 global alignment(s), with score 74:

MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGG
||||.|||.|||||||..|.||.||.|||||||||||||||||||||||||||.|||.||.|||.||||||
MALWTRLLALLALLALGAPTPARAFANQHLCGSHLVEALYLVCGERGFFYTPKARREVEDTQVGGVELGGG

PGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN
||||.||||..||..||||||||||.|.|||||||||||
PGAGGLQPLGPEGRPQKRGIVEQCCASVCSLYQLENYCN
```

Wenn wir die Aminosäuresequenzen alinieren, brauchen wir 0,19 Sekunden.

Machen wir mit der DNA weiter.

```terminal
$ cabal run -- seafovl assets/ins.fa 40 1 -1 -2
Given a pairwise alignment problem with the following key data:

  g_max   = 20
  w_match = 1
  w_miss  = -1
  w_gap   = -2
  seqA    = "ATGGCCCTGTGGATGCGCCTCCTGCCCCTGC..."
  seqB    = "ATGGCCCTGTGGACACGCCTGCTGGCCCTGC..."


The problem is optimally solved by the following 4 global alignment(s), with score 225:

ATGGCCCTGTGGATGCGCCTCCTGCCCCTGCTGGCGCTGCTGGCCCTCTGGGGACCTGACCCAGCCGCAGC
|||||||||||||..|||||.|||.||||||||||.||||||||||||.|||..||...|||.|||...||
ATGGCCCTGTGGACACGCCTGCTGGCCCTGCTGGCCCTGCTGGCCCTCGGGGCGCCCACCCCCGCCCGGGC

...

TGCTGTACCAGCATCTGCTCCCTCTACCAGCTGGAGAACTACTGCAACTAG
|||||..|||||.|||||||.||||||||||||||||||||||||||||||
TGCTGCGCCAGCGTCTGCTCGCTCTACCAGCTGGAGAACTACTGCAACTAG


...
```

Hier benötigen wir bereits 6,05 Sekunden.

### HIV und SIV {#failed_test_performance}

Auch hier setzen wir $w_\text{match} = 1, w_\text{miss} = -1$ und $w_\text{gap} = -2$, aber erlauben beim Alinieren 200 Gaps.

::: danger
Der folgende Aufruf wird nicht in einer angemessenen Zeit fertig werden.

Die Details dazu befinden sich im [Diskussionsteil](#time_analysis).
:::

```terminal
$ cabal run -- seafovl assets/pol.fa 200 1 -1 -2
...
```
