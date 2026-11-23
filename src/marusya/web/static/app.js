
"use strict";

const searchForm = document.querySelector("#search-form");
const bookingForm = document.querySelector("#booking-form");

const tablesList = document.querySelector("#tables-list");
const searchStatus = document.querySelector("#search-status");
const bookingStatus = document.querySelector("#booking-status");
const selectedTableLabel = document.querySelector("#selected-table");

let selectedTableNumber = null;

function showMessage(element, message, type = "") {
    element.textContent = message;
    element.className = `message ${type}`;
}

async function readApiResponse(response) {
    const data = await response.json();

    if (!response.ok) {
        let message = "Не удалось выполнить запрос.";

        if (typeof data.detail === "string") {
            message = data.detail;
        } else if (Array.isArray(data.detail)) {
            message = data.detail
                .map((error) => error.msg)
                .join("; ");
        }

        throw new Error(message);
    }

    return data;
}

function createTableCard(table) {
    const card = document.createElement("article");
    card.className = "table-card";

    const title = document.createElement("h3");
    title.textContent = `Столик №${table.number}`;

    const capacity = document.createElement("p");
    capacity.textContent = `Количество мест: ${table.capacity}`;

    const zone = document.createElement("p");
    zone.textContent = `Зона: ${table.zone}`;

    const button = document.createElement("button");
    button.type = "button";
    button.className = "button";
    button.textContent = "Выбрать столик";

    button.addEventListener("click", () => {
        selectedTableNumber = table.number;
        selectedTableLabel.textContent =
            `Вы выбрали столик №${table.number}`;

        bookingForm.hidden = false;
        showMessage(bookingStatus, "");

        bookingForm.scrollIntoView({
            behavior: "smooth",
            block: "center",
        });
    });

    card.append(title, capacity, zone, button);
    return card;
}

searchForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    selectedTableNumber = null;
    bookingForm.hidden = true;
    tablesList.replaceChildren();

    showMessage(searchStatus, "Ищем свободные столики...");
    showMessage(bookingStatus, "");

    const start = document.querySelector("#start").value;
    const guests = document.querySelector("#guests").value;

    const parameters = new URLSearchParams({
        start,
        guests,
    });

    try {
        const response = await fetch(
            `/api/tables/available?${parameters.toString()}`
        );

        const tables = await readApiResponse(response);

        if (tables.length === 0) {
            showMessage(
                searchStatus,
                "Подходящих столиков нет. Попробуйте другое время."
            );
            return;
        }

        showMessage(
            searchStatus,
            `Найдено свободных столиков: ${tables.length}`
        );

        for (const table of tables) {
            tablesList.append(createTableCard(table));
        }
    } catch (error) {
        showMessage(searchStatus, error.message, "error");
    }
});

bookingForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (selectedTableNumber === null) {
        showMessage(
            bookingStatus,
            "Сначала выберите столик.",
            "error"
        );
        return;
    }

    const button = bookingForm.querySelector(
        'button[type="submit"]'
    );

    button.disabled = true;
    showMessage(bookingStatus, "Создаём бронирование...");

    const payload = {
        table_number: selectedTableNumber,
        start: document.querySelector("#start").value,
        guests: Number(document.querySelector("#guests").value),
        customer_name: document.querySelector("#customer-name").value,
        customer_phone: document.querySelector("#customer-phone").value,
    };

    try {
        const response = await fetch("/api/bookings", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        const booking = await readApiResponse(response);

        showMessage(
            bookingStatus,
            `Бронирование №${booking.id} успешно создано! ` +
            "Сохраните этот номер.",
            "success"
        );

        bookingForm.hidden = true;
        tablesList.replaceChildren();
        showMessage(searchStatus, "");
        selectedTableNumber = null;
    } catch (error) {
        showMessage(bookingStatus, error.message, "error");
    } finally {
        button.disabled = false;
    }
});
