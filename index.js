fetch("/api/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    message: "Hello, how can I assist you today?"
  })
})
.then(response => response.json())
.then(data => {
  console.log("Response from backend:", data);
})
.catch(error => {
  console.error("Error:", error);
});