#import "@preview/cetz:0.4.2"
#import "lib.typ": *

#set text(font: "LMMono10", size: 1.35em)
#set page(width: auto, height: auto, margin: 0em)


#cetz.canvas(length: 20pt * 5, {
    import cetz.draw: *

    content((0, 0), name: "O2", molecule[$"O"_2$])
    content((0, -2), name: "PCD", complex[Protonated \ Carbamino \ DeoxyHbA])

    content((1, -1), name: "r1", CIRCLE_CIRCLE)

    line("O2", "r1")
    line("PCD", "r1")

    content((2, 0), name: "H+", molecule[$"H"^+$])
    content((2, -1), name: "CO2", molecule[$"CO"_2$ \ #text(
            size: .7em,
        )[cytosol]])
    content((2, -2), name: "OHA", complex[OxyHbA])

    line("r1", "H+", mark: ARROW)
    line("r1", "CO2", mark: ARROW)
    line("r1", "OHA", mark: ARROW)

    content((.6, -.6), stoichiometry[4])
    content((1.4, -.6), stoichiometry[4])
    content((1.4, -1), stoichiometry[4])

    content((3, 0), name: "AQP1", complex[AQP1 \ tetramer])
    content((4, -1), name: "CO22", molecule[$"CO"_2$ \ extracellular \ region])

    line("CO2", "CO22", mark: ARROW)
    line("AQP1", (3, -1))

    content((3, -.85), CIRCLE)
    content((3, -1), SQUARE)
})
