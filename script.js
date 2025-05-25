document.addEventListener("DOMContentLoaded", function () {
    const cardContainer = document.getElementById("cardContainer");

    fetch('http://127.0.0.1:5000/api/listings')
        .then(response => response.json())
        .then(data => {
            renderCards(data);
            initShortlistFunctionality();
        })
        .catch(error => console.error("Failed to load listings:", error));

    const shortlistedSet = new Set([0, 2]); // Default: 1st and 3rd
    let isFilterActive = false;

    function renderCards(listings) {
        listings.forEach((listing, index) => {
            const card = document.createElement("div");
            card.className = `card flex row${shortlistedSet.has(index) ? " dark" : ""}`;

            card.innerHTML = `
                <div class="flex column" id="cardLeft">
                    <div class="title flex column">
                        <p>${listing.title}</p>
                        <div class="starbox flex row">
                            <img src="./Assets/star_fill_icon.svg" />
                            <img src="./Assets/star_fill_icon.svg" />
                            <img src="./Assets/star_fill_icon.svg" />
                            <img src="./Assets/star_half_fill.svg" />
                            <img src="./Assets/star_empty_icon.svg" />
                        </div>
                    </div>
                    <p class="description">${listing.description}</p>
                    <div class="factBox flex row">
                        <div class="factCard flex column">
                            <p class="factTitle">${listing.projects}</p>
                            <p class="factDesc">Projects</p>
                        </div>
                        <div class="factCard flex column">
                            <p class="factTitle">${listing.years}</p>
                            <p class="factDesc">Years</p>
                        </div>
                        <div class="factCard flex column">
                            <p class="factTitle">${listing.price}</p>
                            <p class="factDesc">Price</p>
                        </div>
                    </div>
                    <div class="contactBox flex column">
                        ${listing.contact.map(number => `<div class="contactno">${number}</div>`).join('')}
                    </div>
                </div>
                <div class="flex column" id="cardRight">
                    <div class="actionBox flex column">
                        <img src="./Assets/arrow_right.svg" />
                        <p>Details</p>
                    </div>
                    <div class="actionBox flex column">
                        <img src="./Assets/eye_icon.svg" />
                        <p>Hide</p>
                    </div>
                    <div class="actionBox flex column">
                        <img src="${shortlistedSet.has(index) ? './Assets/shortlist_icon.svg' : './Assets/shortlist_invert_icon.svg'}" class="shortlist-icon" data-index="${index}" />
                        <p>Shortlist</p>
                    </div>
                    <div class="actionBox flex column">
                        <img src="./Assets/warning_icon.svg" />
                        <p>Report</p>
                    </div>
                </div>
            `;

            cardContainer.appendChild(card);
        });
    }

    function initShortlistFunctionality() {
        const cards = document.querySelectorAll(".card");
        const shortlistButtons = document.querySelectorAll(".shortlist-icon");
        const shortlistedFilter = document.querySelector("#shortlistedCard");

        shortlistButtons.forEach((btn) => {
            const index = parseInt(btn.dataset.index);
            btn.addEventListener("click", function () {
                const card = cards[index];
                if (shortlistedSet.has(index)) {
                    shortlistedSet.delete(index);
                    btn.src = "./Assets/shortlist_invert_icon.svg";
                    card.classList.remove("dark");
                } else {
                    shortlistedSet.add(index);
                    btn.src = "./Assets/shortlist_icon.svg";
                    card.classList.add("dark");
                }

                if (isFilterActive) updateCardVisibility();
            });
        });

        shortlistedFilter.addEventListener("click", function () {
            isFilterActive = !isFilterActive;
            const textElement = document.querySelector("#shortlistedText");
            if (textElement) {
                textElement.innerText = isFilterActive ? "All" : "Shortlisted";
            }
            updateCardVisibility();
        });

        function updateCardVisibility() {
            cards.forEach((card, index) => {
                if (isFilterActive && !shortlistedSet.has(index)) {
                    card.style.display = "none";
                } else {
                    card.style.display = "flex";
                }
            });
        }
    }
});
