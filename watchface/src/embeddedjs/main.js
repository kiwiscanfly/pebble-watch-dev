import Poco from "commodetto/Poco";
import { formatTime, formatDate } from "dateTime";

const render = new Poco(screen);

// Fonts
const timeFont = new render.Font("Bitham-Bold", 42);
const dateFont = new render.Font("Gothic-Bold", 24);

// #7C6F9F
const purple = render.makeColor(124, 111, 159);

// #46342B
const lightTan = render.makeColor(70, 52, 43);

// Vector icon (resources/svg/icon.svg -> resources/pdc/icon.pdc via svg2pdc).
// Resource ID 1 = the first entry in package.json "resources.media" (ICON).
const icon = new Poco.PebbleDrawCommandImage(1);

// Vertical gap between the time and date lines
const lineGap = 6;

// Left x to horizontally center something of the given width on screen
function centerX(width) {
    return (render.width - width) / 2;
}

// Draw text horizontally centered at the given y
function drawCentered(text, font, color, y) {
    render.drawText(text, font, color, centerX(render.getTextWidth(text, font)), y);
}

function draw(event) {
    const now = event.date;

    // Time sits just above the vertical middle, date below it, and the icon is
    // centered in the space above the time.
    const timeY = (render.height / 2) - timeFont.height + 5;
    const dateY = timeY + timeFont.height + lineGap;
    const iconY = (timeY - icon.height) / 2;

    render.begin();
    render.fillRectangle(lightTan, 0, 0, render.width, render.height);
    render.drawDCI(icon, centerX(icon.width), iconY);
    drawCentered(formatTime(now), timeFont, purple, timeY);
    drawCentered(formatDate(now), dateFont, purple, dateY);
    render.end();
}

watch.addEventListener("minutechange", draw);
