#import "@preview/cetz:0.4.2"
#import "lib.typ": *

#set text(font: "LMMono10", size: 1.35em)
#set page(width: auto, height: auto, margin: 0em)

#cetz.canvas(length: 5pt * 5, {
    import cetz.draw: *
    line((0, 1), (3, 1), mark: ARROW)
    content((1.4, 1), SQUARE)

    line((0, 0), (3, 0), mark: ARROW)
    content((1.4, 0), CIRCLE)
    content((1.4, 0), stoichiometry[2])

    line((0, -1), (3, -1), mark: ARROW)
    circle((1.4, -1), name: "r1", radius: 5pt, fill: black)
    // content((rel: (1, 0)), [Association/Binding])

    line((0, -2), (3, -2), mark: ARROW)
    content((1.4, -2), CIRCLE)

    line((0, -3), (3, -3), mark: ARROW)
    content((1.4, -3), CIRCLE_CIRCLE)
})
