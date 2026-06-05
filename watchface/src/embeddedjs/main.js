import Poco from "commodetto/Poco";
import { createTheme } from "theme";
import { createLayout } from "layout";
import { RESOURCES } from "resources";
import * as iconWidget from "widgets/icon";
import * as timeWidget from "widgets/time";
import * as dateWidget from "widgets/date";

const render = new Poco(screen);
const theme = createTheme(render);
const layout = createLayout(render, theme);

// Loaded in init() rather than at import, so a missing resource surfaces in one
// place instead of silently blanking the watch.
const images = {};

// Everything the widgets render from.
const state = {
    now: undefined
};

const ctx = { render, theme, layout, images };
const widgets = [iconWidget, timeWidget, dateWidget];

function drawScreen() {
    render.begin();
    render.fillRectangle(theme.colors.background, 0, 0, render.width, render.height);
    for (let i = 0; i < widgets.length; i++) {
        widgets[i].draw(ctx, state);
    }
    render.end();
}

function init() {
    images.icon = new Poco.PebbleDrawCommandImage(RESOURCES.ICON);
}

init();

// minutechange fires immediately on registration, painting the first frame.
watch.addEventListener("minutechange", (event) => {
    state.now = event.date;
    drawScreen();
});
