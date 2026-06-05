// Where things go: an anchor point per element, derived from the renderer and
// fonts. `x` is the horizontal center anchor (widgets offset by half their
// content width to center); `y` is the top of the element.
export function createLayout(render, theme) {
    const lineGap = 6;
    const centerX = render.width / 2;

    const timeY = (render.height / 2) - theme.fonts.time.height + 5;
    const dateY = timeY + theme.fonts.time.height + lineGap;

    // Battery is corner-anchored (top-left coords, not a center anchor); the
    // extra 2px on the right leaves room for the terminal nub.
    const margin = 8;
    const batteryWidth = 20;
    const batteryHeight = 10;

    return {
        time: { x: centerX, y: timeY },
        date: { x: centerX, y: dateY },
        battery: {
            x: render.width - margin - batteryWidth - 2,
            y: margin,
            width: batteryWidth,
            height: batteryHeight
        }
    };
}
