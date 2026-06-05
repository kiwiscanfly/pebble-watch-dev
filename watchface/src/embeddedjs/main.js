import Poco from "commodetto/Poco";
import Battery from "embedded:sensor/Battery";
import { createTheme } from "theme";
import { createLayout } from "layout";
import { RESOURCES } from "resources";
import * as iconWidget from "widgets/icon";
import * as timeWidget from "widgets/time";
import * as dateWidget from "widgets/date";
import * as batteryWidget from "widgets/battery";

const render = new Poco(screen);
const theme = createTheme(render);
const layout = createLayout(render, theme);

// Loaded/created in init() rather than at import, so a missing resource or
// sensor surfaces in one place instead of silently blanking the watch.
const images = {};
let battery;

// Everything the widgets render from.
const state = {
    now: undefined,
    battery: { percent: 100, charging: false }
};

const ctx = { render, theme, layout, images };
const widgets = [iconWidget, timeWidget, dateWidget, batteryWidget];

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
    images.bolt = new Poco.PebbleDrawCommandImage(RESOURCES.BOLT);

    battery = new Battery({
        onSample() {
            const sample = this.sample();
            state.battery.percent = sample.percent;
            state.battery.charging = sample.charging;
            // Only redraw once we have a time to show, so a battery sample can't
            // race ahead of the first minutechange paint.
            if (state.now) {
                drawScreen();
            }
        }
    });

    const sample = battery.sample();
    state.battery.percent = sample.percent;
    state.battery.charging = sample.charging;
}

init();

// minutechange fires immediately on registration, painting the first frame.
watch.addEventListener("minutechange", (event) => {
    state.now = event.date;
    drawScreen();
});
