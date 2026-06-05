import Poco from "commodetto/Poco";

const render = new Poco(screen);

// Fonts
const timeFont = new render.Font("Bitham-Bold", 42);
const dateFont = new render.Font("Gothic-Bold", 24);

// #7C6F9F
const purple = render.makeColor(124, 111, 159);

// #46342B
const lightTan = render.makeColor(70, 52, 43);

// getDay() / getMonth() are zero-indexed
const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
];

// Vertical gap between the time and date lines
const lineGap = 6;

function draw(event) {
    const now = event.date;

    render.begin();
    render.fillRectangle(lightTan, 0, 0, render.width, render.height);

    // Get hours in 12 hour format
    let hours = now.getHours() % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const ampm = now.getHours() >= 12 ? "pm" : "am";
    const timeStr = `${hours}:${minutes} ${ampm}`;

    // Center the time on screen, sitting just above the vertical middle
    const timeY = (render.height / 2) - timeFont.height + 5;
    const timeWidth = render.getTextWidth(timeStr, timeFont);
    render.drawText(timeStr, timeFont, purple,
        (render.width - timeWidth) / 2, timeY);

    // Date below the time, e.g. "Mon Jan 01"
    const dayName = DAYS[now.getDay()];
    const monthName = MONTHS[now.getMonth()];
    const dateStr = `${dayName} ${monthName} ${String(now.getDate()).padStart(2, "0")}`;

    const dateWidth = render.getTextWidth(dateStr, dateFont);
    render.drawText(dateStr, dateFont, purple,
        (render.width - dateWidth) / 2, timeY + timeFont.height + lineGap);

    render.end();
}

watch.addEventListener("minutechange", draw);
