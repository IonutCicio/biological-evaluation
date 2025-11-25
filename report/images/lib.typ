#let STROKE = 1pt + black

#let ARROW = (
    end: ">",
    fill: black,
    length: 10pt,
    width: 10pt,
)

#let SQUARE = box(width: 1em, height: 1em, fill: white, stroke: STROKE)
#let CIRCLE = box(
    width: 1em,
    height: 1em,
    radius: 100%,
    fill: white,
    stroke: STROKE,
)
#let CIRCLE_CIRCLE = box(
    width: 1.25em,
    height: 1.25em,
    radius: 100%,
    fill: white,
    stroke: STROKE,
    align(center + horizon, box(
        width: .75em,
        height: .75em,
        radius: 100%,
        fill: white,
        stroke: STROKE,
    )),
)

#let molecule(body) = context {
    let diameter = calc.max(measure(body).width, measure(body).height) + 1.5em

    box(
        // fill: green.lighten(75%),
        fill: luma(210),
        stroke: STROKE,
        radius: 100%,
        width: diameter,
        height: diameter,
        align(center + horizon, body),
    )
}

#let complex(body) = context {
    let corner-radius = 10pt
    let diameter = calc.max(measure(body).width, measure(body).height) + 1.5em

    box(
        width: diameter,
        height: diameter,
        align(center + horizon)[
            #place(
                center + horizon,
                curve(
                    // fill: aqua.lighten(75%),
                    fill: luma(240),
                    stroke: STROKE,
                    curve.move((0%, corner-radius)),
                    curve.line((0%, 100% - corner-radius)),
                    curve.line((corner-radius, 100%)),
                    curve.line((100% - corner-radius, 100%)),
                    curve.line((100%, 100% - corner-radius)),
                    curve.line((100%, corner-radius)),
                    curve.line((100% - corner-radius, 0%)),
                    curve.line((corner-radius, 0%)),
                    curve.line((0%, corner-radius)),
                    curve.close(),
                ),
            )
            #body
        ],
    )
}

#let stoichiometry(body) = context {
    let diameter = calc.max(measure(body).width, measure(body).height) + 1em

    align(center + horizon, box(
        width: diameter,
        height: diameter,
        stroke: STROKE,
        fill: white,
        body,
    ))
}
