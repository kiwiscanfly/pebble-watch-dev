import { formatTime } from "dateTime";

// Current time, centered on its layout anchor.
export function draw(ctx, state) {
    const { render, theme, layout } = ctx;
    const font = theme.fonts.time;
    const text = formatTime(state.now);
    const x = layout.time.x - render.getTextWidth(text, font) / 2;
    render.drawText(text, font, theme.colors.foreground, x, layout.time.y);
}
