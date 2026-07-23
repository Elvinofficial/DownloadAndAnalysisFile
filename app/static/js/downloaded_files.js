const API_FILES_URL = "/api/v1/files";
const API_CALCULATIONS_URL = "/api/v1/calculations";

const calculateButton = document.getElementById(
    "calculate-button",
);

const sortBySelect = document.getElementById(
    "sort-by",
);

const sortOrderSelect = document.getElementById(
    "sort-order",
);

const pageSizeSelect = document.getElementById(
    "page-size",
);

const selectPageButton = document.getElementById(
    "select-page-button",
);

const selectAllButton = document.getElementById(
    "select-all-button",
);

const clearSelectionButton = document.getElementById(
    "clear-selection-button",
);

const selectCurrentPageCheckbox = document.getElementById(
    "select-current-page-checkbox",
);

const selectedCount = document.getElementById(
    "selected-count",
);

const totalCount = document.getElementById(
    "total-count",
);

const filesLoading = document.getElementById(
    "files-loading",
);

const filesEmpty = document.getElementById(
    "files-empty",
);

const filesError = document.getElementById(
    "files-error",
);

const filesTableWrapper = document.getElementById(
    "files-table-wrapper",
);

const filesTableBody = document.getElementById(
    "files-table-body",
);

const pagination = document.getElementById(
    "pagination",
);

const previousPageButton = document.getElementById(
    "previous-page-button",
);

const nextPageButton = document.getElementById(
    "next-page-button",
);

const paginationInfo = document.getElementById(
    "pagination-info",
);

const calculationSection = document.getElementById(
    "calculation-section",
);

const calculationLoading = document.getElementById(
    "calculation-loading",
);

const calculationError = document.getElementById(
    "calculation-error",
);

const totalStatisticsCard = document.getElementById(
    "total-statistics-card",
);

const totalDigitsCount = document.getElementById(
    "total-digits-count",
);

const totalDigitsGrid = document.getElementById(
    "total-digits-grid",
);

const fileStatisticsContainer = document.getElementById(
    "file-statistics-container",
);


let currentPage = 1;
let totalPages = 1;
let currentItems = [];
let totalFiles = 0;

const selectedFileIds = new Set();


sortBySelect.addEventListener(
    "change",
    handleFiltersChange,
);

sortOrderSelect.addEventListener(
    "change",
    handleFiltersChange,
);

pageSizeSelect.addEventListener(
    "change",
    handleFiltersChange,
);

previousPageButton.addEventListener(
    "click",
    async () => {
        if (currentPage <= 1) {
            return;
        }

        currentPage -= 1;
        await loadFiles();
    },
);

nextPageButton.addEventListener(
    "click",
    async () => {
        if (currentPage >= totalPages) {
            return;
        }

        currentPage += 1;
        await loadFiles();
    },
);

selectCurrentPageCheckbox.addEventListener(
    "change",
    () => {
        setCurrentPageSelection(
            selectCurrentPageCheckbox.checked,
        );
    },
);

selectPageButton.addEventListener(
    "click",
    () => {
        const shouldSelect =
            !areAllCurrentPageFilesSelected();

        setCurrentPageSelection(shouldSelect);
    },
);

clearSelectionButton.addEventListener(
    "click",
    () => {
        selectedFileIds.clear();
        updateSelectionInterface();
        renderFiles();
    },
);

selectAllButton.addEventListener(
    "click",
    selectAllFiles,
);

calculateButton.addEventListener(
    "click",
    calculateSelectedFiles,
);


loadFiles();


async function handleFiltersChange() {
    currentPage = 1;
    await loadFiles();
}


async function loadFiles() {
    setFilesLoadingState();

    const params = new URLSearchParams({
        page: String(currentPage),
        page_size: pageSizeSelect.value,
        sort_by: sortBySelect.value,
        sort_order: sortOrderSelect.value,
    });

    try {
        const response = await fetch(
            `${API_FILES_URL}?${params.toString()}`,
        );

        if (!response.ok) {
            throw await createResponseError(response);
        }

        const result = await response.json();

        currentItems = result.items;
        currentPage = result.page;
        totalPages = result.total_pages;
        totalFiles = result.total;

        renderFiles();
        renderPagination();
        updateSelectionInterface();

        filesLoading.classList.add("hidden");

        if (currentItems.length === 0) {
            filesEmpty.classList.remove("hidden");
            filesTableWrapper.classList.add("hidden");
            pagination.classList.add("hidden");
        } else {
            filesEmpty.classList.add("hidden");
            filesTableWrapper.classList.remove("hidden");
            pagination.classList.remove("hidden");
        }

    } catch (error) {
        filesLoading.classList.add("hidden");
        filesTableWrapper.classList.add("hidden");
        pagination.classList.add("hidden");

        showFilesError(
            error instanceof Error
                ? error.message
                : "Не удалось загрузить файлы.",
        );
    }
}


function renderFiles() {
    filesTableBody.replaceChildren();

    for (const file of currentItems) {
        const row = document.createElement("tr");

        const checkboxCell = document.createElement("td");
        checkboxCell.className = "files-table__checkbox";

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = file.id;
        checkbox.checked = selectedFileIds.has(file.id);
        checkbox.setAttribute(
            "aria-label",
            `Выбрать файл ${file.file_name}`,
        );

        checkbox.addEventListener(
            "change",
            () => {
                if (checkbox.checked) {
                    selectedFileIds.add(file.id);
                } else {
                    selectedFileIds.delete(file.id);
                }

                updateSelectionInterface();
            },
        );

        checkboxCell.append(checkbox);

        const nameCell = document.createElement("td");
        nameCell.textContent = file.file_name;

        const dateCell = document.createElement("td");
        dateCell.textContent = formatNovosibirskDate(
            file.downloaded_at,
        );

        row.append(
            checkboxCell,
            nameCell,
            dateCell,
        );

        filesTableBody.append(row);
    }

    updateCurrentPageSelectionState();
}


function renderPagination() {
    paginationInfo.textContent =
        `Страница ${currentPage} из ${totalPages}`;

    previousPageButton.disabled = currentPage <= 1;
    nextPageButton.disabled = currentPage >= totalPages;
}


function setFilesLoadingState() {
    filesLoading.classList.remove("hidden");
    filesEmpty.classList.add("hidden");
    filesError.classList.add("hidden");
    filesTableWrapper.classList.add("hidden");
    pagination.classList.add("hidden");
}


function showFilesError(message) {
    filesError.textContent = message;
    filesError.classList.remove("hidden");
}


function setCurrentPageSelection(shouldSelect) {
    for (const file of currentItems) {
        if (shouldSelect) {
            selectedFileIds.add(file.id);
        } else {
            selectedFileIds.delete(file.id);
        }
    }

    renderFiles();
    updateSelectionInterface();
}


function areAllCurrentPageFilesSelected() {
    return (
        currentItems.length > 0
        && currentItems.every(
            (file) => selectedFileIds.has(file.id),
        )
    );
}


function updateCurrentPageSelectionState() {
    const selectedOnPage = currentItems.filter(
        (file) => selectedFileIds.has(file.id),
    ).length;

    selectCurrentPageCheckbox.checked =
        currentItems.length > 0
        && selectedOnPage === currentItems.length;

    selectCurrentPageCheckbox.indeterminate =
        selectedOnPage > 0
        && selectedOnPage < currentItems.length;

    selectPageButton.textContent =
        selectCurrentPageCheckbox.checked
            ? "Снять выбор со страницы"
            : "Выбрать страницу";
}


function updateSelectionInterface() {
    selectedCount.textContent = String(
        selectedFileIds.size,
    );

    totalCount.textContent = String(totalFiles);

    calculateButton.disabled =
        selectedFileIds.size === 0;

    clearSelectionButton.disabled =
        selectedFileIds.size === 0;

    updateCurrentPageSelectionState();
}


async function selectAllFiles() {
    selectAllButton.disabled = true;
    selectAllButton.textContent = "Выбираем...";

    try {
        const pageSize = 100;
        let page = 1;
        let pages = 1;

        do {
            const params = new URLSearchParams({
                page: String(page),
                page_size: String(pageSize),
                sort_by: sortBySelect.value,
                sort_order: sortOrderSelect.value,
            });

            const response = await fetch(
                `${API_FILES_URL}?${params.toString()}`,
            );

            if (!response.ok) {
                throw await createResponseError(response);
            }

            const result = await response.json();

            for (const file of result.items) {
                selectedFileIds.add(file.id);
            }

            pages = result.total_pages;
            page += 1;

        } while (page <= pages);

        renderFiles();
        updateSelectionInterface();

    } catch (error) {
        showFilesError(
            error instanceof Error
                ? error.message
                : "Не удалось выбрать все файлы.",
        );

    } finally {
        selectAllButton.disabled = false;
        selectAllButton.textContent = "Выбрать все файлы";
    }
}


async function calculateSelectedFiles() {
    if (selectedFileIds.size === 0) {
        return;
    }

    resetCalculationState();

    calculationSection.classList.remove("hidden");
    calculationLoading.classList.remove("hidden");

    calculateButton.disabled = true;
    calculateButton.textContent = "Выполняем расчёты...";

    calculationSection.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });

    try {
        const response = await fetch(
            API_CALCULATIONS_URL,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    file_ids: Array.from(selectedFileIds),
                }),
            },
        );

        if (!response.ok) {
            throw await createResponseError(response);
        }

        const result = await response.json();

        renderCalculationResult(result);

    } catch (error) {
        calculationError.textContent =
            error instanceof Error
                ? error.message
                : "Не удалось выполнить расчёты.";

        calculationError.classList.remove("hidden");

    } finally {
        calculationLoading.classList.add("hidden");

        calculateButton.disabled =
            selectedFileIds.size === 0;

        calculateButton.textContent =
            "Произвести расчёты";
    }
}


function renderCalculationResult(result) {
    totalDigitsCount.textContent = String(
        result.total.total_digits,
    );

    renderDigitsGrid(
        totalDigitsGrid,
        result.total.digits,
    );

    totalStatisticsCard.classList.remove("hidden");

    fileStatisticsContainer.replaceChildren();

    for (const fileResult of result.files) {
        const card = document.createElement("section");
        card.className = "card file-statistics__card";

        const header = document.createElement("div");
        header.className = "download-card__header";

        const titleContainer = document.createElement("div");

        const label = document.createElement("p");
        label.className = "card__label";
        label.textContent = "Файл";

        const title = document.createElement("h3");
        title.className = "card__title";
        title.textContent = fileResult.file_name;

        titleContainer.append(label, title);

        const badge = document.createElement("span");
        badge.className =
            "status-badge status-badge--completed";

        badge.textContent =
            `Всего цифр: ` +
            `${fileResult.statistics.total_digits}`;

        header.append(titleContainer, badge);

        const digitsGrid = document.createElement("div");
        digitsGrid.className = "digits-grid";

        renderDigitsGrid(
            digitsGrid,
            fileResult.statistics.digits,
        );

        card.append(header, digitsGrid);
        fileStatisticsContainer.append(card);
    }
}


function renderDigitsGrid(container, digits) {
    container.replaceChildren();

    for (let digit = 0; digit <= 9; digit += 1) {
        const item = document.createElement("article");
        item.className = "digit-statistic";

        const digitValue = document.createElement("span");
        digitValue.className = "digit-statistic__digit";
        digitValue.textContent = String(digit);

        const countValue = document.createElement("strong");
        countValue.className = "digit-statistic__count";
        countValue.textContent = String(
            digits[String(digit)] ?? 0,
        );

        item.append(digitValue, countValue);
        container.append(item);
    }
}


function resetCalculationState() {
    calculationError.classList.add("hidden");
    calculationError.textContent = "";

    totalStatisticsCard.classList.add("hidden");
    totalDigitsGrid.replaceChildren();

    fileStatisticsContainer.replaceChildren();
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
        // Ответ не содержит JSON.
    }

    return new Error(message);
}