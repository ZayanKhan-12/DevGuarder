document.addEventListener("DOMContentLoaded", () => {
  const trustScoreElement = document.getElementById("trustScore");
  const alertList = document.getElementById("alertList");
  const scanButton = document.getElementById("scanButton");

  // Mock API check function (replace with actual backend logic)
  function checkTrustScore() {
    const score = Math.floor(Math.random() * 100); // Simulate score 0-100
    trustScoreElement.textContent = `Trust Score: ${score}/100`;

    if (score < 40) {
      alertList.innerHTML = `<li>🚨 Suspicious package detected!</li>`;
    } else if (score < 70) {
      alertList.innerHTML = `<li>⚠️ Proceed with caution.</li>`;
    } else {
      alertList.innerHTML = `<li>✅ No threats detected.</li>`;
    }
  }

  scanButton.addEventListener("click", checkTrustScore);
  checkTrustScore(); // Run check on load
});
