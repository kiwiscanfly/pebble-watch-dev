// All date/time formatting for the watchface.

// getDay() / getMonth() are zero-indexed
const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
];

// "9:05 pm" — 12-hour time
export function formatTime(now) {
    const hours = now.getHours() % 12 || 12; // the hour '0' should be '12'
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const ampm = now.getHours() >= 12 ? "pm" : "am";
    return `${hours}:${minutes} ${ampm}`;
}

// "Mon Jan 01"
export function formatDate(now) {
    const dayName = DAYS[now.getDay()];
    const monthName = MONTHS[now.getMonth()];
    const dayOfMonth = String(now.getDate()).padStart(2, "0");
    return `${dayName} ${monthName} ${dayOfMonth}`;
}
