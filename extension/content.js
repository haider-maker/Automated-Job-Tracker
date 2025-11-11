document.addEventListener("click", async (e) => {
  const button = e.target.closest("button");

  if (button && button.innerText.toLowerCase().includes("apply")) {
    const jobTitle = document.querySelector("h1")?.innerText || "Unknown";
    const company = document.querySelector(".topcard__flavor")?.innerText || "Unknown";
    const url = window.location.href;

    const data = {
      company: company.trim(),
      position: jobTitle.trim(),
      job_url: url,
      platform: "LinkedIn",
      notes: "Auto-added from Chrome extension"
    };

    console.log("Detected Apply click:", data);

    try {
      await fetch("http://127.0.0.1:5000/add_job", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      console.log("✅ Sent to Flask successfully!");
    } catch (err) {
      console.error("❌ Failed to send to Flask:", err);
    }
  }
});
