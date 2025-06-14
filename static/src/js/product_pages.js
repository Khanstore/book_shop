/** @odoo-module **/

function updatePages(productId) {
    if (!productId) return;
    console.log("🔄 Fetching pages for product ID:", productId);
    fetch("/get_product_pages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params: { product_id: productId }
        }),
    })
    .then(response => response.json())
    .then(result => {
//    code to show page
        const pages = result.result?.pages ?? 0;
        console.log("📘 Pages received:", pages);
        const pagesEl = document.getElementById('pages_value');
        const pagesDiv = document.getElementsByName('pages_div')[0];
        console.log("🔍 Element found:", pagesEl);

        if (pages > 0) {
            pagesDiv.style.display = 'block';
            pagesEl.textContent = pages;
        } else {
            pagesDiv.style.display = 'none';
        }

        //    code to show publication
        const publication = result.result?.publication ?? 0;
        console.log("📘 publication received:", pages);
        const publicationEl = document.getElementById('publication_value');
        const publicationDiv = document.getElementsByName('publication_div')[0];
        console.log("🔍 Element found:", publicationEl);

        if (publication > 0) {
            publicationDiv.style.display = 'block';
            publicationEl.textContent = publication;
        } else {
            publicationDiv.style.display = 'none';
        }
        //    code to show edition
        const edition = result.result?.edition ?? 0;
        console.log("📘 edition received:", edition);
        console.log("📘 edition received:", edition);
        const editionEl = document.getElementById('edition_value');
        const editionDiv = document.getElementsByName('edition_div')[0];
        console.log("🔍 Element found:", editionEl);
        const isValidEdition = (
            (typeof edition === 'number' && edition > 0) ||
            (typeof edition === 'string' && edition.trim() !== '')
        );

        if (isValidEdition) {
            editionDiv.style.display = 'block';
            editionEl.textContent = edition;
        } else {
            editionDiv.style.display = 'none';
        }
        // code to show paper
        const paper = result.result?.paper ?? 0;
        console.log("📘 paper received:", result.result);
        const paperEl = document.getElementById('paper_value');
        const paperDiv = document.getElementsByName('paper_div')[0];
        const isValidpaper = (
            (typeof paper === 'number' && paper > 0) ||
            (typeof paper === 'string' && paper.trim() !== '')
        );

        if (isValidpaper) {
            paperDiv.style.display = 'block';
            paperEl.textContent = paper;
        } else {
            paperDiv.style.display = 'none';
        }

        //    code to show Binding
        const binding = result.result?.binding ?? 0;
        console.log("📘 binding received:", binding);
        const bindingEl = document.getElementById('binding_value');
        const bindingDiv = document.getElementsByName('binding_div')[0];
        console.log("🔍 Element found:", bindingEl);
        const isValidBinding = (
            (typeof binding === 'number' && binding > 0) ||
            (typeof binding === 'string' && binding.trim() !== '')
        );

        if (isValidBinding) {
            bindingDiv.style.display = 'block';
            bindingEl.textContent = binding;
        } else {
            bindingDiv.style.display = 'none';
        }



        //    code to show page

    })
    .catch(err => console.error("❌ Fetch error:", err));
}

function waitForProductIdInput(callback) {
    const interval = setInterval(() => {
        const input = document.querySelector('input[name="product_id"]');
        if (input) {
            clearInterval(interval);
            callback(input);
        }
    }, 200);
}

function observeProductIdChanges(input) {
    let currentId = parseInt(input.value);
    updatePages(currentId);

    const observer = new MutationObserver(() => {
        const newId = parseInt(input.value);
        if (newId && newId !== currentId) {
            console.log("🆕 Product ID updated:", newId);
            currentId = newId;
            updatePages(newId);
        }
    });

    observer.observe(input, { attributes: true, attributeFilter: ['value'] });
}

console.log("📦 Product Pages JS Loaded");

waitForProductIdInput((input) => {
    console.log("✅ Detected input[name='product_id'], setting up observer...");
    observeProductIdChanges(input);
});
