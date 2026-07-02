const targetInput = document.getElementById("ha-target");
const saveStatus = document.getElementById("save-status");
const captureStatus = document.getElementById("capture-status");

// Restore saved settings and render the last-capture / target status line.
chrome.storage.local.get(["haTarget", "lastCapture"], ({ haTarget, lastCapture }) => {
  if (haTarget) targetInput.value = haTarget;

  const bits = [];
  bits.push(haTarget ? "Auto-forward: ON" : "Auto-forward: off (copy/paste)");
  if (lastCapture && lastCapture.time) {
    const when = new Date(lastCapture.time).toLocaleString();
    bits.push(
      `Last capture: ${when}${lastCapture.hasCode ? " ✓" : " (no code)"}`
    );
  } else {
    bits.push("No capture yet");
  }
  captureStatus.textContent = bits.join(" · ");
});

document.getElementById("save-target").addEventListener("click", () => {
  const value = targetInput.value.trim();
  if (!value) {
    saveStatus.textContent = "Enter a URL, or use Clear to disable forwarding.";
    return;
  }
  try {
    new URL(value); // validate before saving
  } catch {
    saveStatus.textContent = "That doesn't look like a valid URL.";
    return;
  }
  chrome.storage.local.set({ haTarget: value }, () => {
    saveStatus.textContent = "Saved. Callbacks will auto-forward here.";
  });
});

document.getElementById("clear-target").addEventListener("click", () => {
  chrome.storage.local.remove("haTarget", () => {
    targetInput.value = "";
    saveStatus.textContent = "Cleared. Callbacks will show the capture page.";
  });
});
