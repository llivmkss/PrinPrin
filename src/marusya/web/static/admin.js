
"use strict";

const loginView = document.querySelector("#login-view");
const adminView = document.querySelector("#admin-view");
const loginForm = document.querySelector("#login-form");
const loginStatus = document.querySelector("#login-status");

const currentAdmin = document.querySelector("#current-admin");

const bookingsBody = document.querySelector("#bookings-body");
const bookingsStatus = document.querySelector("#bookings-status");

const occupancyForm = document.querySelector("#occupancy-form");
const occupancyDay = document.querySelector("#occupancy-day");
const occupancyBody = document.querySelector("#occupancy-body");
const occupancyStatus = document.querySelector("#occupancy-status");

let authorization = null;

function showMessage(element, text, isError = false) {
    element.textContent = text;
    element.className = isError ? "message error" : "message";
}

function makeBasicHeader(username, password) {
    const credentials = `${username}:${password}`;
    const bytes = new TextEncoder().encode(credentials);

    let binary = "";

    for (const byte of bytes) {
        binary += String.fromCharCode(byte);
    }

    return `Basic ${btoa(binary)}`;
}

async function apiRequest(path, authHeader, options = {}) {
    const response = await fetch(path, {
        ...options,
        cache: "no-store",
        headers: {
            Authorization: authHeader,
            Accept: "application/json",
            ...(options.headers || {}),
        },
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        let detail = "Не удалось выполнить запрос.";

        if (typeof data.detail === "string") {
            detail = data.detail;
        } else if (Array.isArray(data.detail)) {
            detail = data.detail.map((item) => item.msg).join("; ");
        }

        const error = new Error(detail);
        error.status = response.status;
        throw error;
    }

    return data;
}

function formatDateTime(value) {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return date.toLocaleString("ru-RU", {
        dateStyle: "short",
        timeStyle: "short",
    });
}

function addCell(row, value) {
    const cell = document.createElement("td");
    cell.textContent = String(value);
    row.append(cell);
    return cell;
}

function logout(message = "") {
    authorization = null;

    loginView.hidden = false;
    adminView.hidden = true;

    loginForm.reset();
    bookingsBody.replaceChildren();
    occupancyBody.replaceChildren();

    showMessage(loginStatus, message, Boolean(message));
}

function handleError(error, messageElement) {
    if (error.status === 401) {
        logout("Авторизация не пройдена. Войдите снова.");
        return;
    }

    showMessage(messageElement, error.message, true);
}

function renderBookings(bookings) {
    bookingsBody.replaceChildren();

    const active = bookings.filter(
        (booking) => booking.status === "активно"
    ).length;

    document.querySelector("#total-count").textContent =
        bookings.length;

    document.querySelector("#active-count").textContent =
        active;

    document.querySelector("#cancelled-count").textContent =
        bookings.length - active;

    if (bookings.length === 0) {
        const row = document.createElement("tr");
        const cell = addCell(
            row,
            "Бронирований пока нет."
        );

        cell.colSpan = 8;
        cell.className = "empty-cell";
        bookingsBody.append(row);
        return;
    }

    for (const booking of bookings) {
        const row = document.createElement("tr");

        addCell(row, booking.id);
        addCell(row, booking.customer_name);
        addCell(row, booking.customer_phone);
        addCell(row, booking.table_number);
        addCell(row, booking.guests);
        addCell(row, formatDateTime(booking.start));

        const statusCell = document.createElement("td");
        const status = document.createElement("span");

        status.textContent = booking.status;
        status.className = booking.status === "активно"
            ? "status status-active"
            : "status status-cancelled";

        statusCell.append(status);
        row.append(statusCell);

        const actionCell = document.createElement("td");

        if (booking.status === "активно") {
            const button = document.createElement("button");

            button.type = "button";
            button.className = "small-button";
            button.textContent = "Отменить";

            button.addEventListener("click", () => {
                cancelBooking(booking, button);
            });

            actionCell.append(button);
        } else {
            actionCell.textContent = "—";
        }

        row.append(actionCell);
        bookingsBody.append(row);
    }
}

function renderOccupancy(occupancies) {
    occupancyBody.replaceChildren();

    for (const occupancy of occupancies) {
        const row = document.createElement("tr");

        addCell(row, occupancy.table.number);
        addCell(row, occupancy.table.zone);
        addCell(row, occupancy.table.capacity);

        const periods = occupancy.bookings.map(
            (booking) =>
                `${formatDateTime(booking.start)} — ` +
                `${formatDateTime(booking.end)}`
        );

        addCell(
            row,
            periods.length > 0
                ? periods.join("; ")
                : "Свободен весь день"
        );

        occupancyBody.append(row);
    }

    if (occupancies.length === 0) {
        const row = document.createElement("tr");
        const cell = addCell(row, "Столики не найдены.");

        cell.colSpan = 4;
        cell.className = "empty-cell";
        occupancyBody.append(row);
    }
}

async function refreshBookings() {
    const usedAuthorization = authorization;

    if (!usedAuthorization) {
        return;
    }

    showMessage(bookingsStatus, "Загружаем бронирования...");

    try {
        const bookings = await apiRequest(
            "/api/admin/bookings",
            usedAuthorization
        );

        if (authorization !== usedAuthorization) {
            return;
        }

        renderBookings(bookings);

        showMessage(
            bookingsStatus,
            `Загружено бронирований: ${bookings.length}`
        );
    } catch (error) {
        handleError(error, bookingsStatus);
    }
}

async function refreshOccupancy() {
    const usedAuthorization = authorization;

    if (!usedAuthorization) {
        return;
    }

    const day = occupancyDay.value;

    if (!day) {
        showMessage(
            occupancyStatus,
            "Сначала выберите дату.",
            true
        );
        return;
    }

    showMessage(occupancyStatus, "Загружаем расписание...");

    try {
        const query = new URLSearchParams({ day });

        const occupancies = await apiRequest(
            `/api/admin/occupancy?${query.toString()}`,
            usedAuthorization
        );

        if (authorization !== usedAuthorization) {
            return;
        }

        renderOccupancy(occupancies);
        showMessage(occupancyStatus, "Расписание загружено.");
    } catch (error) {
        handleError(error, occupancyStatus);
    }
}

async function cancelBooking(booking, button) {
    const confirmed = window.confirm(
        `Отменить бронирование №${booking.id} ` +
        `для клиента ${booking.customer_name}?`
    );

    if (!confirmed) {
        return;
    }

    const usedAuthorization = authorization;

    if (!usedAuthorization) {
        return;
    }

    button.disabled = true;

    try {
        await apiRequest(
            `/api/admin/bookings/${booking.id}/cancel`,
            usedAuthorization,
            { method: "POST" }
        );

        if (authorization !== usedAuthorization) {
            return;
        }

        await refreshBookings();
        await refreshOccupancy();

        if (authorization === usedAuthorization) {
            showMessage(
                bookingsStatus,
                `Бронирование №${booking.id} отменено.`
            );
        }
    } catch (error) {
        handleError(error, bookingsStatus);
    } finally {
        button.disabled = false;
    }
}

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.querySelector(
        "#admin-login"
    ).value.trim();

    const passwordInput = document.querySelector(
        "#admin-password"
    );

    const authHeader = makeBasicHeader(
        username,
        passwordInput.value
    );

    showMessage(loginStatus, "Проверяем учётные данные...");

    try {
        const bookings = await apiRequest(
            "/api/admin/bookings",
            authHeader
        );

        authorization = authHeader;

        loginForm.reset();
        loginView.hidden = true;
        adminView.hidden = false;

        currentAdmin.textContent = username;
        renderBookings(bookings);

        showMessage(
            bookingsStatus,
            `Загружено бронирований: ${bookings.length}`
        );

        await refreshOccupancy();
    } catch (error) {
        showMessage(loginStatus, error.message, true);
        passwordInput.value = "";
    }
});

document.querySelector("#logout-button")
    .addEventListener("click", () => logout());

document.querySelector("#refresh-bookings")
    .addEventListener("click", refreshBookings);

occupancyForm.addEventListener("submit", (event) => {
    event.preventDefault();
    refreshOccupancy();
});

const today = new Date();
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, "0");
const day = String(today.getDate()).padStart(2, "0");

occupancyDay.value = `${year}-${month}-${day}`;
