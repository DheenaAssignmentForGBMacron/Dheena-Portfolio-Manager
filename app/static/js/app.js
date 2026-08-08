// =====================================================
// DPM - Application Script
// =====================================================

console.log("app.js loaded");

// =====================================================
// Initialize
// =====================================================

document.addEventListener("DOMContentLoaded", () => {

    initializeAssetAutocomplete();
    initializeAssetSearch();
    initializeActionMenu();

});

// =====================================================
// Asset Autocomplete (Add/Edit Transaction)
// =====================================================

function initializeAssetAutocomplete() {

    const searchBox = document.getElementById("asset-search");
    const resultsBox = document.getElementById("asset-results");
    const assetId = document.getElementById("asset-id");

    if (!searchBox || !resultsBox) {
        return;
    }

    searchBox.addEventListener("input", async () => {

        const query = searchBox.value.trim();

        if (!query) {

            resultsBox.innerHTML = "";
            resultsBox.style.display = "none";
            return;

        }

        const response = await fetch(`/api/assets?q=${encodeURIComponent(query)}`);
        const assets = await response.json();

        resultsBox.innerHTML = "";

        if (assets.length === 0) {

            resultsBox.innerHTML = `
                <div class="asset-item no-result">
                    No asset found.
                    <br><br>
                    <a href="/add-asset">
                        + Create Asset
                    </a>
                </div>
            `;

            resultsBox.style.display = "block";
            return;

        }

        assets.forEach(asset => {

            const item = document.createElement("div");

            item.className = "asset-item";

            item.innerHTML = `
                <div class="asset-symbol">
                    ${asset.symbol}
                </div>

                <div class="asset-info">
                    ${asset.name}
                    •
                    ${asset.asset_class}
                    •
                    ${asset.exchange}
                </div>
            `;

            item.addEventListener("click", () => {

                searchBox.value = asset.symbol;

                if (assetId) {
                    assetId.value = asset.id;
                }

                resultsBox.style.display = "none";

            });

            resultsBox.appendChild(item);

        });

        resultsBox.style.display = "block";

    });

    document.addEventListener("click", event => {

        if (
            !searchBox.contains(event.target) &&
            !resultsBox.contains(event.target)
        ) {

            resultsBox.style.display = "none";

        }

    });

}

// =====================================================
// Assets Page Search
// =====================================================

function initializeAssetSearch() {

    const filterInput = document.getElementById("assetFilter");
    const tableRows = document.querySelectorAll("#assetTable tr");

    if (!filterInput || tableRows.length === 0) {
        return;
    }

    filterInput.addEventListener("input", () => {

        const filter = filterInput.value.toLowerCase();

        tableRows.forEach(row => {

            const text = row.innerText.toLowerCase();

            row.style.display = text.includes(filter)
                ? ""
                : "none";

        });

    });

}

// =====================================================
// Transaction Action Menu
// =====================================================

function initializeActionMenu() {

    let activeMenu = null;

    document.querySelectorAll(".menu-btn").forEach(button => {

        button.addEventListener("click", function (e) {

            e.stopPropagation();

            const menu = this.nextElementSibling;

            // Close previous menu
            if (activeMenu && activeMenu !== menu) {
                activeMenu.classList.remove("show");
            }

            // Toggle same menu
            if (menu.classList.contains("show")) {

                menu.classList.remove("show");
                activeMenu = null;
                return;
            }

            menu.classList.add("show");

            const btnRect = this.getBoundingClientRect();

            const menuWidth = menu.offsetWidth;
            const menuHeight = menu.offsetHeight;

            let left = btnRect.right - menuWidth;
            let top = btnRect.bottom + 6;

            // open upward if required
            if (top + menuHeight > window.innerHeight) {
                top = btnRect.top - menuHeight - 6;
            }

            // keep inside viewport
            left = Math.max(10, Math.min(left, window.innerWidth - menuWidth - 10));

            menu.style.left = left + "px";
            menu.style.top = top + "px";

            activeMenu = menu;

        });

    });

    document.addEventListener("click", () => {

        if (activeMenu) {

            activeMenu.classList.remove("show");
            activeMenu = null;

        }

    });

}

// =====================================================
// Error Modal
// =====================================================

function closeModal() {

    const modal = document.getElementById("errorModal");

    if (modal) {
        modal.style.display = "none";
    }

}