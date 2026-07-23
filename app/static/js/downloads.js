const startButton = document.getElementById(
    "start-download-button",
);

const statusTitle = document.getElementById(
    "download-status-title",
);

const statusBadge = document.getElementById(
    "download-status-badge",
);

const startedAt = document.getElementById(
    "started-at",
);

const totalFiles = document.getElementById(
    "total-files",
);

const downloadedFiles = document.getElementById(
    "downloaded-files",
);

const progressPercent = document.getElementById(
    "progress-percent",
);

const progressBar = document.getElementById(
    "progress-bar",
);

const downloadMessage = document.getElementById(
    "download-message",
);

const errorContainer = document.getElementById(
    "error-container",
);

const errorMessage = document.getElementById(
    "error-message",
);

const TERMINAL_STATUSES = new Set([
    "completed",
    "failed",
]);

let pollingTimer = null;


startButton.addEventListener(
    "click",
    startDownload,
);


async function startDownload() {
    stopPolling();
    resetError();

    startButton.disabled = true;
    startButton.textContent = "Запуск...";

    setStatus(
        "pending",
        "Создание задачи",
    );

    downloadMessage.textContent =
        "Создаём задачу на скачивание файлов...";

    try {
        const response = await fetch(
            "/api/v1/downloads",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            },
        );

        if (!response.ok) {
            throw await createResponseError(response);
        }

        const result = await response.json();

        await loadDownloadJob(result.job_id);

        pollingTimer = window.setInterval(
            () => loadDownloadJob(result.job_id),
            1000,
        );

    } catch (error) {
        showRequestError(error);

        startButton.disabled = false;
        startButton.textContent = "Скачать данные";
    }
}


async function loadDownloadJob(jobId) {
    try {
        const response = await fetch(
            `/api/v1/downloads/${jobId}`,
        );

        if (!response.ok) {
            throw await createResponseError(response);
        }

        const job = await response.json();

        renderDownloadJob(job);

        const normalizedStatus = normalizeStatus(
            job.status,
        );

        if (TERMINAL_STATUSES.has(normalizedStatus)) {
            stopPolling();

            startButton.disabled = false;
            startButton.textContent = "Скачать данные";
        }

    } catch (error) {
        stopPolling();
        showRequestError(error);

        startButton.disabled = false;
        startButton.textContent = "Скачать данные";
    }
}


function renderDownloadJob(job) {
    const normalizedStatus = normalizeStatus(
        job.status,
    );

    totalFiles.textContent = job.total_files;
    downloadedFiles.textContent = job.downloaded_files;

    const percent = Math.min(
        Math.max(job.progress_percent, 0),
        100,
    );

    progressPercent.textContent = `${percent}%`;
    progressBar.style.width = `${percent}%`;

    startedAt.textContent = job.started_at
        ? formatNovosibirskDate(job.started_at)
        : "Ожидается";

    resetError();

    switch (normalizedStatus) {
        case "pending":
            setStatus(
                "pending",
                "Задача ожидает запуска",
            );

            downloadMessage.textContent =
                "Задача создана и ожидает выполнения.";

            break;

        case "processing":
        case "running":
        case "in_progress":
            setStatus(
                "processing",
                "Скачивание выполняется",
            );

            if (job.total_files === 0) {
                downloadMessage.textContent =
                    "Получаем список файлов...";
            } else {
                downloadMessage.textContent =
                    `Получено ${job.total_files} названий файлов, ` +
                    `скачано ${job.downloaded_files} ` +
                    `из ${job.total_files}.`;
            }

            break;

        case "completed":
            setStatus(
                "completed",
                "Скачивание завершено",
            );

            if (job.total_files === 0) {
                downloadMessage.textContent =
                    "Внешний сервис не вернул новых файлов.";
            } else {
                downloadMessage.textContent =
                    `Получено ${job.total_files} названий файлов, ` +
                    `скачано ${job.downloaded_files} ` +
                    `из ${job.total_files}.`;
            }

            break;

        case "failed":
            setStatus(
                "failed",
                "Скачивание завершилось ошибкой",
            );

            downloadMessage.textContent =
                "Не удалось завершить скачивание файлов.";

            showError(
                job.error_message
                || "Неизвестная ошибка выполнения задачи.",
            );

            break;

        default:
            setStatus(
                "pending",
                "Обработка задачи",
            );

            downloadMessage.textContent =
                "Получаем актуальное состояние задачи.";
    }
}


function setStatus(status, title) {
    statusTitle.textContent = title;

    statusBadge.className =
        `status-badge status-badge--${status}`;

    const labels = {
        idle: "Не запущено",
        pending: "Ожидание",
        processing: "Выполняется",
        completed: "Завершено",
        failed: "Ошибка",
    };

    statusBadge.textContent =
        labels[status] || "Обработка";
}


function normalizeStatus(status) {
    return String(status)
        .trim()
        .toLowerCase();
}


function formatNovosibirskDate(dateValue) {
    const date = new Date(dateValue);

    return new Intl.DateTimeFormat(
        "ru-RU",
        {
            timeZone: "Asia/Novosibirsk",
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
        },
    ).format(date);
}


function stopPolling() {
    if (pollingTimer !== null) {
        window.clearInterval(pollingTimer);
        pollingTimer = null;
    }
}


function resetError() {
    errorContainer.classList.add("hidden");
    errorMessage.textContent = "";
}


function showError(message) {
    errorMessage.textContent = message;
    errorContainer.classList.remove("hidden");
}


function showRequestError(error) {
    setStatus(
        "failed",
        "Не удалось выполнить запрос",
    );

    downloadMessage.textContent =
        "Проверьте доступность сервиса и повторите попытку.";

    showError(
        error instanceof Error
            ? error.message
            : "Произошла неизвестная ошибка.",
    );
}


async function createResponseError(response) {
    let message =
        `Сервер вернул ошибку ${response.status}.`;

    try {
        const body = await response.json();

        if (typeof body.detail === "string") {
            message = body.detail;
        } else if (body.detail?.message) {
            message = body.detail.message;
        }

    } catch {
        // Ответ сервера не содержит JSON.
    }

    return new Error(message);
}