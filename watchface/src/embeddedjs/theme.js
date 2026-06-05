// Visual style for the watchface: colors and fonts, built from the renderer.
export function createTheme(render) {
    return {
        colors: {
            background: render.makeColor(70, 52, 43), // #46342B
            foreground: render.makeColor(124, 111, 159) // #7C6F9F
        },
        fonts: {
            time: new render.Font("Bitham-Bold", 42),
            date: new render.Font("Gothic-Bold", 24)
        }
    };
}
