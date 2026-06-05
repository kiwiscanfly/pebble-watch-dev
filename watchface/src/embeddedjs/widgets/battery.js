const LOW_PERCENT = 20;
const MEDIUM_PERCENT = 40;

// Pure: pick the fill color for a charge level. `colors` is theme.colors.battery.
export function batteryColor(percent, colors) {
    if (percent <= LOW_PERCENT) {
        return colors.low;
    }
    if (percent <= MEDIUM_PERCENT) {
        return colors.medium;
    }
    return colors.good;
}

// Battery-shaped indicator: outline + terminal nub, with the charge level drawn
// inside and masked to the interior via Poco's rectangular clip. Shows a bolt
// while charging.
export function draw(ctx, state) {
    const { render, theme, layout, images } = ctx;
    const geom = layout.battery;
    const colors = theme.colors.battery;
    const { percent, charging } = state.battery;

    // 1px body outline + terminal nub protruding just past the right edge.
    // NOTE: frameRoundRect args are (x, y, width, height) — a Pebble GRect —
    // despite the typings naming them x0/y0/x1/y1.
    render.frameRoundRect(geom.x, geom.y, geom.width, geom.height, colors.outline, 1);
    const nubHeight = 4;
    const nubY = geom.y + (((geom.height - nubHeight) / 2) | 0);
    render.fillRectangle(colors.outline, geom.x + geom.width, nubY, 2, nubHeight);

    // Interior sits just inside the 1px frame, so the fill is flush with it (no
    // gap). Clip to it so the fill can't spill out; the unfilled part is left as
    // the background painted earlier this frame.
    const innerX = geom.x + 1;
    const innerY = geom.y + 1;
    const innerWidth = geom.width - 2;
    const innerHeight = geom.height - 2;

    render.clip(innerX, innerY, innerWidth, innerHeight);

    const fillWidth = ((percent * innerWidth) / 100) | 0;
    render.fillRectangle(batteryColor(percent, colors), innerX, innerY, fillWidth, innerHeight);

    if (charging) {
        const bolt = images.bolt;
        const boltX = innerX + (((innerWidth - bolt.width) / 2) | 0);
        const boltY = innerY + (((innerHeight - bolt.height) / 2) | 0);
        render.drawDCI(bolt, boltX, boltY);
    }

    render.clip(); // pop
}
