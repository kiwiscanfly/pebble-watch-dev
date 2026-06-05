// The app icon, centered above the time.
export function draw(ctx) {
    const { render, layout, images } = ctx;
    const icon = images.icon;
    const y = (layout.time.y - icon.height) / 2;
    render.drawDCI(icon, layout.time.x - icon.width / 2, y);
}
