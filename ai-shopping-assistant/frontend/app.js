const API = "/api";

async function fetchWatchlist() {
  const res = await fetch(`${API}/watchlist`);
  const items = await res.json();
  renderTable(items);
  document.getElementById("itemCount").textContent = `${items.length} item${items.length !== 1 ? "s" : ""}`;
}

function renderTable(items) {
  const tbody = document.getElementById("watchlistBody");
  if (!items.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty">No alerts yet. Add one above.</td></tr>`;
    return;
  }

  tbody.innerHTML = items.map(item => {
    const priceClass = item.current_price && item.current_price <= item.target_price
      ? "price-hit" : "price-above";

    const currentDisplay = item.current_price
      ? `<span class="${priceClass}">₹${item.current_price.toLocaleString("en-IN")}</span>`
      : `<span style="color:#aaa">—</span>`;

    let badge;
    if (item.notified) {
      badge = `<span class="badge badge-notified">Notified</span>`;
    } else if (!item.is_active) {
      badge = `<span class="badge badge-paused">Paused</span>`;
    } else {
      badge = `<span class="badge badge-active">Watching</span>`;
    }

    const toggleLabel = item.is_active ? "Pause" : "Resume";

    return `
      <tr>
        <td class="product-name">
          <a href="${item.product_url}" target="_blank" title="${item.product_name}">
            ${item.product_name}
          </a>
        </td>
        <td>₹${item.target_price.toLocaleString("en-IN")}</td>
        <td>${currentDisplay}</td>
        <td>${item.whatsapp_number}</td>
        <td>${badge}</td>
        <td class="actions">
          <button class="btn-icon" onclick="toggleActive(${item.id}, ${!item.is_active})">${toggleLabel}</button>
          ${item.notified ? `<button class="btn-icon" onclick="resetNotified(${item.id})">Re-watch</button>` : ""}
          <button class="btn-icon danger" onclick="deleteItem(${item.id})">Delete</button>
        </td>
      </tr>`;
  }).join("");
}

document.getElementById("addForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    product_name: document.getElementById("productName").value.trim(),
    product_url: document.getElementById("productUrl").value.trim(),
    target_price: parseFloat(document.getElementById("targetPrice").value),
    whatsapp_number: document.getElementById("whatsappNumber").value.trim(),
  };

  const res = await fetch(`${API}/watchlist`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (res.ok) {
    e.target.reset();
    showToast("Alert added successfully");
    fetchWatchlist();
  } else {
    showToast("Failed to add alert", true);
  }
});

async function deleteItem(id) {
  if (!confirm("Remove this alert?")) return;
  await fetch(`${API}/watchlist/${id}`, { method: "DELETE" });
  showToast("Alert removed");
  fetchWatchlist();
}

async function toggleActive(id, isActive) {
  await fetch(`${API}/watchlist/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ is_active: isActive }),
  });
  fetchWatchlist();
}

async function resetNotified(id) {
  await fetch(`${API}/watchlist/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ notified: false, is_active: true }),
  });
  showToast("Re-watching product");
  fetchWatchlist();
}

document.getElementById("checkNowBtn").addEventListener("click", async () => {
  const btn = document.getElementById("checkNowBtn");
  btn.disabled = true;
  btn.textContent = "Checking...";
  await fetch(`${API}/check-now`, { method: "POST" });
  showToast("Price check triggered");
  setTimeout(() => {
    btn.disabled = false;
    btn.textContent = "🔄 Check Prices Now";
    fetchWatchlist();
  }, 3000);
});

function showToast(msg, isError = false) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.style.background = isError ? "#e74c3c" : "#1a1a2e";
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3000);
}

// Init
fetchWatchlist();
