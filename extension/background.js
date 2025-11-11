chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "jobApplied") {
    console.log("📤 Sending job to Flask API:", message.data);

    fetch("http://127.0.0.1:5000/add_job", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(message.data)
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("✅ Flask API response:", data);
      })
      .catch((err) => {
        console.error("❌ Error sending job to Flask API:", err);
      });
  }
});
