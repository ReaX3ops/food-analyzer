document.addEventListener("DOMContentLoaded", () => {

  // Animate result card in
  const resultCard = document.getElementById("result-card");
  if (resultCard) {
    requestAnimationFrame(() => resultCard.classList.add("show"));
  }

  // Show selected filename in upload zone
  const fileInput = document.getElementById("food_image");
  const fileNameDisplay = document.getElementById("file-name-display");
  if (fileInput && fileNameDisplay) {
    fileInput.addEventListener("change", () => {
      const name = fileInput.files[0]?.name;
      fileNameDisplay.textContent = name ? `Selected: ${name}` : "";
    });
  }

  // Language toggle
  const toggleBtn = document.getElementById("toggle-lang");
  if (!toggleBtn) return;

  let lang = "km";

  toggleBtn.addEventListener("click", () => {
    lang = lang === "km" ? "en" : "km";

    const labels = {
      food:        lang === "km" ? "ម្ហូប"       : "Food",
      calories:    lang === "km" ? "កាលូរី"     : "Calories",
      ingredients: lang === "km" ? "គ្រឿងផ្សំ" : "Ingredients",
    };

    document.getElementById("food-label").textContent        = labels.food;
    document.getElementById("calories-label").textContent    = labels.calories;
    document.getElementById("ingredients-label").textContent = labels.ingredients;

    const foodNameEl = document.getElementById("food-name");
    if (lang === "en" && foodNameEl.textContent.trim() === "មិនដឹង") {
      foodNameEl.textContent = "Unknown";
    } else if (lang === "km" && foodNameEl.textContent.trim() === "Unknown") {
      foodNameEl.textContent = "មិនដឹង";
    }
  });

});