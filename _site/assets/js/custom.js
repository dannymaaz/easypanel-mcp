// EasyPanel MCP Documentation - Custom Script
// Implements dynamic year and high-end inline translation (ES / EN)

document.addEventListener("DOMContentLoaded", function () {
  // 1. Dynamic Year Update
  const yearElement = document.getElementById("current-year");
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }

  // 2. Setup Google Translate API Elements
  setupTranslationElements();
});

// Setup Translate Widget & Language Toggle Button
function setupTranslationElements() {
  // Create hidden Google Translate element container
  const translateDiv = document.createElement("div");
  translateDiv.id = "google_translate_element";
  translateDiv.style.display = "none";
  document.body.appendChild(translateDiv);

  // Ingest Google Translate JS API Script
  const translateScript = document.createElement("script");
  translateScript.src = "https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
  document.head.appendChild(translateScript);

  // Define global init function for Google Translate
  window.googleTranslateElementInit = function () {
    new google.translate.TranslateElement({
      pageLanguage: 'es',
      includedLanguages: 'en,es',
      autoDisplay: false
    }, 'google_translate_element');
  };

  // Wait for header to be ready, then inject the toggle button
  const headerActions = document.querySelector(".md-header__option") || document.querySelector(".md-header__inner");
  if (headerActions) {
    const langBtn = document.createElement("button");
    langBtn.className = "md-icon lang-toggle-btn";
    langBtn.title = "Cambiar Idioma / Switch Language";
    langBtn.setAttribute("aria-label", "Switch Language");
    
    // SVG Globe Icon
    langBtn.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path d="M17.9 17.39c-.26-.8-1.01-1.39-1.9-1.39h-1v-3a1 1 0 0 0-1-1H8v-2h2a1 1 0 0 0 1-1V7h2a2 2 0 0 0 2-2v-.41a7.72 7.72 0 0 1 2.9 12.8M11 17v-2.5a.5.5 0 0 0-.5-.5h-4v-.5A2.5 2.5 0 0 1 9 11h.5a.5.5 0 0 0 .5-.5V8h3.5a.5.5 0 0 0 .5-.5v-3a8 8 0 0 1 6.54 11.85A10 10 0 1 0 11 17m1-15a10 10 0 1 1-10 10A10 10 0 0 1 12 2Z"/>
      </svg>
      <span class="lang-text">ES</span>
    `;

    // Insert button right before the search or theme toggle
    const searchDiv = document.querySelector(".md-search");
    if (searchDiv) {
      searchDiv.parentNode.insertBefore(langBtn, searchDiv);
    } else {
      headerActions.appendChild(langBtn);
    }

    // Toggle logic
    let currentLang = "es";
    langBtn.addEventListener("click", function () {
      const selectEl = document.querySelector("#google_translate_element select");
      if (!selectEl) return;

      if (currentLang === "es") {
        selectEl.value = "en";
        currentLang = "en";
        langBtn.querySelector(".lang-text").textContent = "EN";
      } else {
        selectEl.value = "es";
        currentLang = "es";
        langBtn.querySelector(".lang-text").textContent = "ES";
      }

      // Fire change event to trigger Google Translate
      selectEl.dispatchEvent(new Event("change"));
    });
  }
}
