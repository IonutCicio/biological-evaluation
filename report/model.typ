#set text(font: "New Computer Modern", lang: "en", weight: "light", size: 11pt)
#set page(margin: 1.75in)
#set par(leading: 0.55em, spacing: 0.85em, justify: true)
#set heading(numbering: "1.1")
#set math.equation(numbering: "(1)")

#let listing(kind, caption, body) = {
    strong({
        upper(kind.first()) + kind.slice(1)
        sym.space
        context counter(kind).step()
        context counter(kind).display()
        sym.space
    })
    [(#caption)*.*]
    sym.space

    body
}

#let listing-def(caption, body) = listing("definition", caption, body)

= Kinetic constants estimation in biochemical networks

== Problem definition

#listing-def[Biochemical network][
    A biochemical network $G$ is a tuple $(S, R, E, nu)$ where

    - $S = U union X union Y$ is the set of *species* of the biochemical network
        where
        - $U$ is the set of input species of the network
        - $X$ is the set of internal species // species which are neither inputs or outputs
        - $Y$ is the set of output species of the network
        - $U, X, Y$ are *non-disjoint* sets

    - $R$ is the set of *reactions* in the biochemical network
        - $R_"reversible" subset.eq R$ is the subset of reversible reactions

    - $E subset.eq S times R times T$ is the set of *relationships* between the
        species and reactions, with $T$ as the set of relationship types

    - $nu = (nu_"reactant", nu_"product")$

        - $nu_t : E_t -> NN_1$ with $t in {"reactant", "product"}$ are the
            stoichiometry functions for the reactants and products of the
            reactions

    // TODO: page 5 A reac- tion is always catalysed by a specific enzyme; we describe isoenzymes by distinct reactions.
    // TODO: mi conviene modellare le "costanti di equilibrio" e le "velocità con cui si raggiungono piuttosto che k_1 e k_2?
    // Beh, in questo modo posso dire: si, tu devi andare più veloce o più lento
    // Oppure, si, tu devi essere di più e tu di meno

    // TODO: this is meant to handle species which are both reactants and products of reactions

    // - $nu_"reactant" : E_"reactant" -> NN_1$ is the stoichiometry function
    //     for the reactants of the reactions
    //
    // - $nu_"product" : E_"product" -> NN_1$ is the stoichiometry function for
    //     the products of the reactions

    with

    - $T = {"product", "reactant", "enzyme", "activator", "inhibitor"}$

    - $E_t = {(s, r) | (s, r, t) in E}$
        is the projection of $E$ over $t in T$

    - $E_"modifier" = E_("enzyme") union E_("inhibitor")$

    // - $nu : S times R times {"reactant", "product"} -> NN_1$ is the
    //     stoichiometry function

]

\

$
    S -> P
$

$
    limits(v)^dot = (k_2 dot.c E dot.c S) / (S + (k_(-1) + k_2) / k_1)
$

\

$
    "sia" S_1 + S_2 -> P "una reazione con enzima" E
$

$
    limits(v)^dot = (k_2 dot.c [E] dot.c [S_1 dot.c S_2]) / ([S_1 dot.c S_2] + (k_(-1) + k_2) / k_1)
$

#align(center)[ dove $[S]$ è la concentrazione della species S]


\

```cyp
MATCH (r:ReactionLikeEvent)
WHERE EXISTS {
    MATCH (r)--(c1:CatalystActivity), (r)--(c2:CatalystActivity)
    WHERE c1 <> c2
}
RETURN COUNT (DISTINCT r) // 17
```

```cyp
MATCH path = ({dbId: 983702})--(:CatalystActivity)
RETURN path
```


// TODO: is there a reaction which takes an enzyme (catalyst activity) and gives out a complex containing the enzyme?
// TODO: again the question, is there something that is both catalyst and input of reaction?
// TODO: is this the case for really reversible reactions???? (The enzyme may catalyze the reaction in both directions, pag 62, 4.25).
// TODO: c'è qualcosa con più di un catalyst activity?

Let $NN_1 = NN \\ {0}$

One enzyme molecule can catalyze thousands of reactions per second (this
so-called turn­ over number ranges from 102 to 107 s 1). Enzyme cataly­ sis leads
to a rate acceleration of about 106 up to 1012-fold compared to the
noncatalyzed, spontaneous reaction.

The turnover number (kcat) of an enzyme is the maximum number of substrate
molecules one enzyme active site can convert into product per second, indicating
its catalytic efficiency, calculated as Vmax (maximum reaction velocity) divided
by the total enzyme concentration. It shows how fast an enzyme works, with
values ranging from less than one to millions of molecules per second, and is
key to understanding how effectively an enzyme processes substrates

$10^2 "to" 10^7 "reactions"/s$

Chemical and biochemical kinetics rely on the assumption that the reaction rate
v at a certain point in time and space can be expressed as a unique function of
the concentrations of all substances at this point in time and space.

Classical enzyme kinetics assumes for sake of simplicity a spatial homogeneity
(the “well-stirred” test tube) and no direct dependency of the rate on time:

*time-invariant* system

concentration: always based on a volume
- $n / V space "quantity" / "litre"$


// TODO: S -> = simple decay

== Assumptions

=== Assumption 1 (quasi-equilibrium of E and ES)

Michaelis and Menten [5] considered a quasi-equilibrium between the free enzyme
and the enzyme–substrate complex, meaning that the reversible conversion of $E$
and $S$ to $"ES"$ is much faster than the decomposition of $"ES"$ into $E$ and
$P$, or in terms of the kinetic constants, that is,

$k_1, k_(-1) >> k_2$

- (possibile assunzione "quasi-equilibrium" di enzima-libero e complesso) // TODO:
enzima-specie "la reazione regolata da un enzima, che produce il complesso
"enzima - specie" è molto più lenta della reazione che prende il complesso e ci
fa cose!"

=== Assumption 2 (concentration of ES is constant)

This works only if $S(t = 0) >> E$ (because the turnover rate of $E$ is kinda
big, thus $(dif"ES") / (dif t) = 0$

#pagebreak()

Given a biochemical network $G = (S, R, , nu)$ let @modular-rate-laws be the
general form of a modular rate law that describes the kinetics of reaction
$r in R$.

=== Stuff

1. Draw a wiring diagram of all steps to consider (e.g., Eq. (4.11)). It
    contains all substrates and products ($S$ and $P$) and $n$ free or bound
    enzyme species
($E$ and $"ES"$).
2. The right sides of the ODEs for the concentrations changes sum up the rates
    of all steps leading to or away from a certain substance (e.g., Eqs.
    (4.12)–(4.15)). The rates follow mass action kinetics (Eq. (4.3)).
// OK! So basically, I have the normal rates of the kinetics
3. The sum of all enzyme-containing species is equal to the total enzyme
    concentration $E_"total"$ (the right side of all differential equations for
    enzyme species sums up to zero). This constitutes one equation (ok, but what
    if enzymes are produced?)

4. The assumption of quasi-steady state for $n - 1$ enzyme species (i.e.,
    setting the right sides of the respective ODEs equal to zero) together with
    (3) result in $n$ algebraic equations for the concentrations of the $n$
    enzyme species.

5. The reaction rate is equal to the rate of product formation (e.g., Eq.
    (4.16)). Insert the respective concen­ trations of enzyme species resulting
    from (4).

#pagebreak()

// TODO take a reaction which is reversible, check catalysts!

// TODO: effector = regulator... (inhibitor and activator, vs positive and negative)
// TODO: ah, are there reactions with multiple "catalyst activity!"???

// TODO: cell designer to open SBML file
// TODO: copasi for simulations
// TODO: vcell

// 4.1.6
// Generalized Mass Action Kinetics

// TODO: other than project, define projection while keeping information? Nah

// Let's denote the concentration with [e]

$
    v_r = E_"total" dot.c f_"reg" dot.c T / (D + D_"reg")
$ <modular-rate-laws>

where

$
    E_"total" = sum_((s, r) \ in \ E_"enzyme") [s] + "complexes that contain the enzyme??"
$

$
    f_"reg" =
    product_((s, r) in E_"enzyme") [s]^(n^s_r) / (K^s_r + [s]^(n^s_r))
    product_((s, r) in E_"inhibitor") K^s_r / (K^s_r + [s]^(n^s_r))
$

$
    T =
    k^"for"_"cat" limits(product)_((s, r) \ in \ E_"reactant") ([s] / K^r_(m, s))^(nu_"reactant" (s, r))
    - k^"back"_"cat" limits(product)_((s, r) \ in \ E_"product") ([s] / K^r_(m, s))^(nu_"product" (s, r))
$


Power-law modular rate law: D = 1 (such as mass action kinetics)
// TODO: mass-action -> power-law (generalization of mass action, why is it a generalization? how does it work?)
$
    D_1 = 1
$

Common modular rate law
$
    D_2 = product_( (s, r) \ in \ E_"reactant" ) (1 + sum_(n = 1)^(nu_"reactant" (s, r)) ([s] / K_(m, s))^n ) \
    + product_( (s, r) \ in \ E_"product" ) (1 + sum_(n = 1)^(nu_"product" (s, r)) ([s] / K_(m, s))^n )
$

Simultaneous binding modular rate law
$
    D_3 = product_( (s, r) \ in \ E_"reactant" ) (1 + [s] / K_(m , s))^(nu_"reactant" (s, r)) product_( (s, r) \ in \ E_"product" ) (1 + [s] / K_(m , s))^(nu_"product" (s, r))
$

Direct binding modular rate law:

$
    D_4 = 1
    + product_((s, r) in E_"reactant") ([s] / K_(m, s)^r)^(nu_"reactant" (s, r))
    + product_((s, r) in E_"product") ([s] / K_(m, s)^r)^(nu_"product" (s, r))
$

Force-dependent modular rate law:

$
    D_5 = sqrt(
        product_( (s, r) \ in \ E_"reactant" ) (1 + [s] / K_(m , s))^(nu_"reactant" (s, r)) product_( (s, r) \ in \ E_"product" ) (1 + [s] / K_(m , s))^(nu_"product" (s, r))
    )
$


// TODO: how many species are involved in a reaction on average? This can determine how the law scales

// https://pmc.ncbi.nlm.nih.gov/articles/PMC1781438/

// \

// #line(stroke: .1pt, length: 100%)

// \

// === Kinetics

// #align(center, box(width: auto)[
//     $
//         v = E_"total" dot.c
//         // (
//         product_((s, r) in E_"enzyme") s^(n^s_r) / (K^s_r + s^(n^s_r))
//         product_((s, r) in E_"inhibitor") K^s_r / (K^s_r + s^(n^s_r))
//         // f_"reg"
//         // )
//         dot.c
//         (
//         k^"for"_"cat" limits(product)_((s, r) in E_"reactant") (s / K_(m, s))^(nu_"reactant" (s, r))
//         - k^"back"_"cat" limits(product)_((s, r) in E_"product") (s / K_(m, s))^(nu_"product" (s, r))
//         ) /
//         D
//     $
// ])

// product_i (1 + sum_(a = 1)^i (S_i / K_(m, S_i))^a)
// + product_j (1 + sum_(a = 1)^j (P_j / K_(m, P_j))^a)
// - 1

// k^"for"_"cat" product_i (S_i / K_(m, S_i))^(n_(-i))
// - k^"back"_"cat" product_j (P_j / K_(m, P_j))^(n_j)

\

// X, D, C

#listing-def[Dynamic biological model][
    Given a biochemical network $G = (S, R, E, nu)$ let $B = (G′, cal(K))$ be
    the biological model derived from $G$ with added modular law kinetics, with
    $G′ =
    (S, R′, E′, nu′)$ where

    - $R' = R union R_"input" union R_"output"$ with
        - $R_"input" = { r_s | s in U - Y}$
        - $R_"output" = { r_s | s in Y - U}$
    - $E' = E union {(s, r, "product") | r_s in R_"input"} union {(s, r, "reactant") | r_s in R_"output"}$

    - $nu' = (nu'_"reactant", nu'_"product")$
        - $
                nu'_"reactant"(s, r) = cases(
                    1 quad & "if " (s, r) in R_"input",
                    nu_"reactant" (s, r) quad & "otherwise"
                )
            $
        - $
                nu'_"product"(s, r) = cases(
                    1 quad & "if " (s, r) in R_"output",
                    nu_"product" (s, r) quad & "otherwise"
                )
            $

    // TODO: what if the reaction is not reversible
    Then $cal(K)$, the set of constants, can be defined on $G'$ as
    $
        cal(K) = & { k^"for"_("cat", r) | r in R' } union \
                 & { k^"back"_("cat", r) | r in R' } union \
                 & { K^r_(m, s) | (s, r) in E'_"reactant" union E'_"product" } union \
                 & { K^s_r | r in R' and (s, r) in E_"modifier" } union \
                 & { n^s_r | r in R' and (s, r) in E_"modifier" }
    $
    where
    - $k_r$ is the kinetic constant of reaction $r$
    - $K_r^s$ is the apparent dissociation constant of modifier $s$ in reaction
        $r$
    - $n_s^r$ the hill coefficient of modifier $s$ in reaction $r$
]

// Approximation: An "irreversible" reaction in biological networks is often modeled as a very fast forward reaction with a negligible reverse rate constant, which fits within the convenience kinetics framework by making the product release term dominant or the reverse rate effectively zero.

// Focus on Flux: By emphasizing the saturation curve and steady-state behavior (like quasi-steady-state), it captures how enzyme activity changes with substrate concentration, mimicking unidirectional flow in metabolic pathways.

// TODO: compute how many constants does a specific model have

// TODO: is there a species which is both inhibitor and enzyme in the same reaction?
// TODO: does cineca slurm support slurm rest api? Nah, it doesnt, it must enable job submission from node


// "modifier"^+

// - $nu : E_r -> NN_+$
// - $nu : E_p -> NN_+$
// - $nu : E_r union E_p -> NN_1$ is the *stoichiometry* of the reactants of
//     products of the reaction

// is the set of relationship types between species and reactions
// , with $T$ the relationship type


#pagebreak()

== Convenience Kinetics and Modular Rate Laws

#set math.equation(numbering: none)

#align(center)[#box(width: auto)[
        $
            v = E_"total" dot.c f_"reg" dot.c
            (k^"for"_"cat" product_i (S_i / K_(m, S_i))^(n_(-i)) - k^"back"_"cat" product_j (P_j / K_(m, P_j))^(n_j)) /
            (
            product_i (1 + sum_(a = 1)^i (S_i / K_(m, S_i))^a)
            + product_j (1 + sum_(a = 1)^j (P_j / K_(m, P_j))^a)
            - 1
            )
        $
    ]
]

/ $v$: amount of substance that is converted in the reaction
/ $E_"total"$: ? oh, wait, wtf????? Is it computable? $E_"total"$ is the enzyme
    concentration
/ $f_"reg"$: ?
/ $k^"for"_"cat"$: constant of reaction moving "forward" when the reaction is
    reversible (why cat?)
/ $k^"back"_"cat"$: turnover rate!!! (same for forward)
/ $K_(m, S_i), K_(m, P_j)$: constant which somehow reduces the probability of
    reaction of that species, what does that $m$ stand for?

$
    f_"reg" = cases(
        1 quad & "if no regulation is present",
        product (M/(K_A + M) dot.c K_I / (K_I + M)) quad & "otherwise (resp. positive and negative regulation)"
    )
$
where
- $M$ is the concentration of the modifier
- $K_A, K_I$ measured in concentration units (values denote concentrations, at
    which the inhibitor or activator has its half-maximal effect)

now:
- the denominator should somehow "slow down" the reaction... right?
    - well, in the worst case the denominator is exactly 1
- is it > or < of 1? It must be at least 1
- what is the domain of $K_(m, S)$? Is it >= 0? Yeah, it must be.
- Where are the modifiers? Are the modifiers in $E_"total"$?

$
    K_V = (K^"for"_"cat" dot.c K^"back"_"cat")^(1/2)
$

$ E_"total" $
pare pericolosa, perché è la somma della concentrazione degli enzimi + la somma
del prodotto

// A turnover rate (or number, kcat) in a reaction, especially with enzymes or
// catalysts, measures how efficiently a single active site converts substrate
// molecules into products per unit of time, typically seconds. It's the maximum
// number of substrate molecules transformed per active site when the enzyme is
// fully saturated with substrate, expressed as molecules/active site/second (s⁻¹).
// A higher turnover number indicates a faster, more efficient catalyst

// when is a reaction half-maximal? When it reaches 50% of its maximum response or rate.
// K_m: substrate concentration yielding half of the maximum velocity  V_max / 2
// half-maximal if the reaction products are absent


#pagebreak()

#listing-def[Biological model satisfiability problem][
    Given a biological model $B = (G, cal(K))$ and a let $cal(S)$ be the set of
    concentrations of species of the species in the network,
    $cal(S) = {s | s in S}$ and $S_"avg" = {s_"avg" | s in S}$ the set of
    average concentrations of the species, $T in RR^+$ the time horizon,
    $phi in [0, 1]$ the following constraints must hold:
    // TODO: maybe time horizon >= 0
    #[
        #set math.equation(numbering: "(1)")

        $ forall s in cal(S) quad 0 <= [s] <= 1 $

        $
            & forall k_r_1, k_r_2 in cal(K), s in S \
            & quad (s, r_1, i) in E and (s, r_2) in (E_(m^+) union E_(m^-)) and r_1 != r_2 -> k_r_1 < k_r_2
        $

        $ forall s in cal(S)_"avg" quad s (phi dot.c T) - s(T) = 0 $
    ]
    // TODO: what other constraints do I have to handle?
    // - I handle the 0 <= s <= 1
    // - I handle the modifiers concentrations
    // - I handle the the transitory
    // - TODO: I have to handle the mythical "target values" or something ("aderenza" baby)
]

#listing-def[Optimization problem][
]

// #pagebreak()


#pagebreak()

#set page(margin: 1in)
#set raw(syntaxes: "Cypher.sublime-syntax", lang: "cyp")
#show raw: set block(
    fill: luma(250),
    stroke: .1pt + black,
    breakable: false,
    width: 100%,
    inset: 1em,
)
#show raw: set text(font: "LMMonoLt10", size: 10.5pt)

// TODO: rename into something better, like "Appendix" or "Interesting stuff"
= Queries

== Multiple compartments per species

Because the functions of biologic molecules critically depend on their
subcellular locations, chemically identical entities located in different
compartments are represented as distinct physical entities. (TODO: this is a
citation)

\

#figure(
    ```
    MATCH (physicalEntity:PhysicalEntity)
    WHERE EXISTS {
        MATCH
            (physicalEntity)--(compartment1:Compartment),
            (physicalEntity)--(compartment2:Compartment)
        WHERE
            compartment1 <> compartment2
    }
    RETURN COUNT(DISTINCT physicalEntity) // 6347
    ```,
    caption: [
        Entities connected to multiple compartments
    ],
)

\

#figure(
    ```
    MATCH (physicalEntity:PhysicalEntity)
    WHERE EXISTS {
        MATCH
            (physicalEntity)-[:compartment]-(compartment1:Compartment),
            (physicalEntity)-[:compartment]-(compartment2:Compartment)
        WHERE
            compartment1 <> compartment2
    }
    RETURN COUNT(DISTINCT physicalEntity) // 656
    ```,
    caption: [
        Entities with multiple compartments only using the `[:compartment]`
        relation
    ],
)

\

#figure(
    ```
    MATCH (physicalEntity:PhysicalEntity)
    WHERE EXISTS {
        MATCH
            (physicalEntity)-[:compartment]-(compartment1:Compartment),
            (physicalEntity)-[:compartment]-(compartment2:Compartment)
        WHERE
            compartment1 <> compartment2
            AND NOT EXISTS {
                MATCH (compartment1)-[:surroundedBy]-(compartment2)
            }
    }
    RETURN COUNT(DISTINCT physicalEntity) // 491
    ```,
    caption: [
        Entities with multiple compartments where one compartment is not
        `[:surroundedBy]` the other
    ],
)


\



#figure(
    ```
    MATCH (physicalEntity:PhysicalEntity)
    WHERE
        EXISTS {
            MATCH
                (physicalEntity)-[:compartment]-(compartment1:Compartment),
                (physicalEntity)-[:compartment]-(compartment2:Compartment)
            WHERE
                compartment1 <> compartment2
                AND NOT EXISTS {
                    MATCH (compartment1)-[:surroundedBy]-(compartment2)
                }
        }
        AND "EntitySet" IN labels(physicalEntity)
    RETURN COUNT(DISTINCT physicalEntity) // 491
    ```,
    caption: [
        Entities with multiple unrelated compartments which are entity-sets (how
        do I treat these?)
    ],
)


== Reactions with multiple compartments

// TODO: some reactions have compartments
// TODO: some reactions have multiple compartments, lol... sadge
// TODO: it does matter, sadly

#figure(
    ```
    MATCH (reaction:ReactionLikeEvent)
    WHERE EXISTS {
        MATCH
            (reaction)--(compartment1:Compartment),
            (reaction)--(compartment2:Compartment)
        WHERE
            compartment1 <> compartment2
    }
    RETURN COUNT (DISTINCT reaction) // 36322 (out of 93672)
    ```,
    caption: [
    ],
)

#figure(
    ```
    MATCH (reaction:ReactionLikeEvent)
    WHERE EXISTS {
        MATCH
            (reaction)--(compartment1:Compartment),
            (reaction)--(compartment2:Compartment)
        WHERE
            compartment1 <> compartment2
            AND NOT EXISTS {
                MATCH (compartment1)-[:surroundedBy]-(compartment2)
            }
    }
    RETURN COUNT (DISTINCT reaction) // 20974
    ```,
    caption: [

    ],
)

#figure(
    ```
    MATCH (reaction:ReactionLikeEvent)
    WHERE EXISTS {
        MATCH
            (reaction)--(compartment1:Compartment),
            (reaction)--(compartment2:Compartment)
        WHERE
            compartment1 <> compartment2
            AND NOT EXISTS {
                MATCH (compartment1)--(compartment2)
            }
    }
    RETURN COUNT (DISTINCT reaction) 20833 (if you remove :surroundedBy)
    ```,
    caption: [
        https://reactome.org/PathwayBrowser/#/R-HSA-9646399&FLG=R-HSA-9640114&FLGINT
    ],
)

// compartment optional on reaction!

https://sbml.org/documents/faq/ // compartment

https://raw.githubusercontent.com/combine-org/combine-specifications/main/specifications/files/sbml.level-3.version-2.core.release-2.pdf

#figure(
    ```
    MATCH (reaction:ReactionLikeEvent)
    WHERE EXISTS {
        MATCH
            (reaction)--(compartment1:Compartment),
            (reaction)--(compartment2:Compartment)
        WHERE
            compartment1 <> compartment2
            AND NOT EXISTS {
                MATCH (compartment1)-[:surroundedBy]-(compartment2)
            }
            AND EXISTS {
                MATCH (compartment1)--(compartment2)
            }
    }
    RETURN COUNT (DISTINCT reaction) // 189 "componentOf"
    ```,
)

#figure(
    ```
    MATCH (:Compartment)-[relation]-(:Compartment)
    RETURN DISTINCT type(relation)
    ```,
)

== Species which are both inputs and outputs of a reaction

// TODO: what happens when a species is both input and output of a reaction?
```
MATCH (reaction:ReactionLikeEvent)-[:input]->(p:PhysicalEntity)
WHERE EXISTS {
    MATCH (n)-[:output]->(p)
}
RETURN COUNT(n) // 1062
```

\

```
MATCH (n:ReactionLikeEvent)-[:input]->(p:PhysicalEntity)
WHERE EXISTS {
    MATCH (n)-[:output]->(p), (m)-[:output]->(p)
    WHERE n <> m
}
RETURN COUNT (n) // 895
```

\

```
MATCH (n:ReactionLikeEvent)-[:input]->(p:PhysicalEntity)
WHERE EXISTS {
    MATCH (n)-[:output]->(p), (n)-[:output]->(q)
    WHERE p <> q
}
RETURN COUNT (n) // 741
```

\

```
MATCH (n:ReactionLikeEvent)-[r1:input]->(p:PhysicalEntity)
WHERE EXISTS {
    MATCH (n)-[r2:output]->(p), (n)-[:output]->(q)
    WHERE
        p <> q
        AND r1.stoichiometry <> r2.stoichiometry
}
RETURN COUNT (n) // 36
```

\

Di queste 36, 24 sono "electron transfer"

```
MATCH (n:ReactionLikeEvent)-[r1:input]->(p:PhysicalEntity)
WHERE EXISTS {
    MATCH (n)-[r2:output]->(p), (n)-[:output]->(q)
    WHERE
        p <> q
        AND r1.stoichiometry <> r2.stoichiometry
}
AND NOT n.displayName STARTS WITH 'Electron transfer'
RETURN COUNT (n) // 12
```


\

// Di queste 12, 11 sono
// - "CYP19A1 hydroxylates ANDST to E1"
// e una è
// - "Prdm9 Trimethylates Histone H3 (murine, bovine)"

// GenomeEncodedEntity
// Any informational macromolecule (DNA, RNA, protein) or entity derived from one by
// post-synthetic modifications, for example, covalently modified forms of proteins.
// GenomeEncodedEntity is a subclass of PhysicalEntity and has one subclass:
// EntityWithAccessionedSequence. Unlike an EntityWithAccessionedSequence, a
// GenomeEncodedEntity is not required to have a reference entity, though a reference to an entity
// in a database can be specified in the crossReference attribute.

// TODO if a physicalEntity is a Complex and a component of the complex mediates the molecularFunction,
// that component should be identified as the activeUnit of the CatalystActivity.


== Enzymes which are both positive and negative regulators
// TODO: If the Regulator is a Complex, the specific Complex component(s) that play the regulatory role
// can be specified as activeUnit(s) of the NegativeRegulation instance.

// https://pitkley.dev/blog/atom-grammar-to-sublime-syntax/
// TODO: can something be both a an enzyme and an inhibitor in a reaction

Reactions that are driven by an enzyme are described as requiring a catalyst
activity, modeled in Reactome by linking the macromolecule that provides the
activity to the GO molecular function term [10,11] that describes the activity.
In addition, the Reactome data model allows reactions to be modulated by
positive and negative regulatory factors. When a precise regulatory mechanism
('positive allosteric regulation', 'noncompetitive inhibition') is known, this
information is captured.

```
MATCH (reaction:ReactionLikeEvent)
WHERE EXISTS {
    MATCH
        (reaction)-[:catalystActivity]->
            (:CatalystActivity)-[:physicalEntity]->(enzyme),
        (reaction)-[:regulatedBy]->
            (:NegativeRegulation)-[:regulator]->(inhibitor)
    WHERE enzyme = inhibitor
}
RETURN COUNT(DISTINCT reaction) // 4
```

\

```
MATCH (reaction:ReactionLikeEvent)
WHERE EXISTS {
    MATCH
        (reaction)-[:regulatedBy]->
            (:PositiveRegulation)-[:regulator]->(enzyme),
        (reaction)-[:regulatedBy]->
            (:NegativeRegulation)-[:regulator]->(inhibitor)
    WHERE enzyme = inhibitor
}
RETURN COUNT(DISTINCT reaction) // 4
```

\

```
MATCH
    (reaction:ReactionLikeEvent),
    path1 = (reaction)-[:catalystActivity]->
            (:CatalystActivity)-[:physicalEntity]->(),
    path2 = (reaction)-[:regulatedBy]->
        (:NegativeRegulation)-[:regulator]->()
WHERE
    reaction.dbId IN [164341, 164087, 164136, 164055]
RETURN path1, path2
UNION
MATCH
    (reaction:ReactionLikeEvent),
    path1 = (reaction)-[:regulatedBy]->
        (:PositiveRegulation)-[:regulator]->(),
    path2 = (reaction)-[:regulatedBy]->
        (:NegativeRegulation)-[:regulator]->()
WHERE
    reaction.dbId IN [8950347, 10181912, 10290972, 10761215]
RETURN path1, path2
```
- top ones are all in either _"Mus musculus"_ or in _"Rattus norvegicus"_
- bottom ones are basically the same reaction, but inferred to multiple species

// TODO: https://jjj.biochem.sun.ac.za/
// TODO: https://www.ebi.ac.uk/biomodels/
// TODO: https://academic.oup.com/nar/article/31/1/248/2401298
// inferredTo Doesn't need to be traversed I think, I TODO: check if there is "inverredTo" stuff within the same species?
// TODO: super useful! https://pmc.ncbi.nlm.nih.gov/articles/PMC1868929/#:~:text=Reactions%20that%20are%20driven%20by%20an%20enzyme,inhibition')%20is%20known%2C%20this%20information%20is%20captured.

// MATCH ({reaction})-[:catalystActivity]->(:CatalystActivity)-[:physicalEntity]->(physicalEntity:PhysicalEntity)

// MATCH ({reaction})-[:regulatedBy]->(regulation:Regulation)-[:regulator]->(physicalEntity:PhysicalEntity)
// RETURN
//     COLLECT({{
//         physicalEntity: physicalEntity,
//         category: CASE
//             WHEN "PositiveRegulation" IN labels(regulation) THEN "positive_regulator"
//             WHEN "NegativeRegulation" IN labels(regulation) THEN "negative_regulator"
//             ELSE ""
//         END
//     }}) AS {reaction_regulators}

// The Reactome data model extends the concept of a biochemical reaction to include such things as the association of two proteins to form a complex, or the transport of an ubiquitinated protein into the proteasome. Reactions are chained together by shared physical entities; an output of one reaction may be an input for another reaction and serve as the catalyst for yet another reaction.
//
// TODO: how to model: "association of two proteins to forma a complex", "transport of protein"
// Because the functions of biologic molecules critically depend on their subcellular locations, chemically identical entities located in different compartments are represented as distinct physical entities. For example, extracellular D-glucose and cytosolic D-glucose are distinct Reactome entities.
// TODO: interesting, how can I use the reference entity? Reactome handles this using the concept of a 'reference entity', which captures the invariant features of a molecule such as its name, reference chemical structure, amino acid or nucleotide sequence (when relevant), and accession numbers in reference databases.
// TODO: WHAT I DO!! https://pmc.ncbi.nlm.nih.gov/articles/PMC5256869/
// TODO: the thing to search is "parameter estimation in biological networks"
// TODO: is there a way to model directly concentrations in roadrunner?
// TODO: what do compartments have to do in all of this?
// TODO: what happens when a species is both input and output of a reaction?
// TODO: what better kinetic law to use?
// TODO: should I have a reaction type
// Let ℕ1 = ℕ\ {0} be the set of natural numbers excluding 0.
// TODO: make a diagram to show all cases
// TODO: is it more common for a reaction to be reversible or not?
// TODO: wtf is normal reaction?
// TODO: p5.js to do animation of graph, like consumption and etc...
// TODO: non è che la direzione inversa ha bisogno di catalizzatori !!!! ?
// TODO: how many reactions are not reversible in Reactome?
// TODO: In the enzyme kinetics term \(k_{cat}\) (catalytic rate constant), the "cat" part stands for catalytic, referring to the enzyme's ability to catalyze (speed up) a reaction

```
MATCH
    path = (r1 {dbId: 1482894})-[:reverseReaction]-(r2),
    path2 = (r1)--(:PhysicalEntity),
    path3 = (r2)--(:PhysicalEntity)
RETURN path, path2, path3
```
