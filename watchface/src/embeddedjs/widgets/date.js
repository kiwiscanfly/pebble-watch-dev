import { formatDate } from "dateTime";

// Current date, centered on its layout anchor below the time.
export function draw(ctx, state) {
    const { render, theme, layout } = ctx;
    const font = theme.fonts.date;
    const text = formatDate(state.now);
    const x = layout.date.x - render.getTextWidth(text, font) / 2;
    render.drawText(text, font, theme.colors.foreground, x, layout.date.y);
}
