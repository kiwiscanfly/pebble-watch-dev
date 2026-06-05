// Where things go: an anchor point per element, derived from the renderer and
// fonts. `x` is the horizontal center anchor (widgets offset by half their
// content width to center); `y` is the top of the element.
export function createLayout(render, theme) {
    const lineGap = 6;
    const centerX = render.width / 2;

    const timeY = (render.height / 2) - theme.fonts.time.height + 5;
    const dateY = timeY + theme.fonts.time.height + lineGap;

    return {
        time: { x: centerX, y: timeY },
        date: { x: centerX, y: dateY }
    };
}
