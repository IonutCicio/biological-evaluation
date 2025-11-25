#import "@preview/cetz:0.4.2"
#import "lib.typ": *

#set text(font: "LMMono10", size: 1.35em)
#set page(width: auto, height: auto, margin: 0em)


#cetz.canvas(length: 20pt * 5, {
    import cetz.draw: *

    content((0, 0), name: "Ca", molecule[$"Ca"^(2_+)$])
    content((0, -2), name: "ISPC", complex[Inactive \ Sarcomere \ Protein \
        Complex])

    circle((1, -1), name: "r1", radius: 5pt, fill: black)

    content((2, -1), name: "CBSPC", complex[Calcium \ Bound \ Sarcomere \
        Protein \ Complex])

    line("Ca", "r1")
    line("ISPC", "r1")
    line("r1", "CBSPC", mark: ARROW)

    content((.6, -.6), stoichiometry[2])

    content((2.75, 0), name: "ATP", molecule[ATP])
    line("ATP", (2.75, -1))
    content((2.75, -.6), stoichiometry[2])

    circle((3, -1), name: "r2", radius: 5pt, fill: black)

    content((4, -1), name: "ATPCBSPC", complex[ATP: Calcium \ Bound \ Sarcomere
        \ Protein \ Complex])

    line("CBSPC", "ATPCBSPC", mark: ARROW)

    content((5.4, 0), name: "MC", complex[Myosyn \ Complex])
    line("MC", (5.4, -1))

    line("ATPCBSPC", (6, -1))
    content((5.4, -1), SQUARE)
    content((5.4, -.85), CIRCLE)
    content((7, 0), name: "Pi", molecule[Pi])
    line((6, -1), "Pi", mark: ARROW)
    content((6.4, -.6), stoichiometry[2])

    content((7, -2), name: "ADPCBSPC", complex[ADP: Calcium \ Bound \ Sarcomere
        \ Protein \ Complex])
    line((6, -1), "ADPCBSPC", mark: ARROW)

    line("ADPCBSPC", (3, -2))
    line((3, -2), "CBSPC", mark: ARROW)
    content((2, -3), name: "ADP", molecule[ADP])
    line((3, -2), "ADP", mark: ARROW)

    content((2.6, -2.4), stoichiometry[2])
    content((4.6, -2), CIRCLE_CIRCLE)
})

