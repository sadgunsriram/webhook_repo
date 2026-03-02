async function fetchEvents() {

    try {
        const res = await fetch("/events");

        if (!res.ok) {
            throw new Error("Network response not ok");
        }

        const data = await res.json();

        const container = document.getElementById("events");
        let html = "";

        // Make sure data is an array
        if (!Array.isArray(data) || data.length === 0) {
            html = "<div class='event'>No activity yet...</div>";
        } else {

            data.forEach(e => {

                if (e.action === "PUSH") {
                    html += `<div class="event">
                        "${e.author || "Unknown"}" pushed to "${e.to_branch || ""}" 
                        <br><small>${e.timestamp || ""}</small>
                    </div>`;
                }

                else if (e.action === "PULL_REQUEST") {
                    html += `<div class="event">
                        "${e.author || "Unknown"}" submitted a pull request 
                        from "${e.from_branch || ""}" to "${e.to_branch || ""}" 
                        <br><small>${e.timestamp || ""}</small>
                    </div>`;
                }

                else if (e.action === "MERGE") {
                    html += `<div class="event">
                        "${e.author || "Unknown"}" merged branch 
                        "${e.from_branch || ""}" to "${e.to_branch || ""}" 
                        <br><small>${e.timestamp || ""}</small>
                    </div>`;
                }

                else {
                    html += `<div class="event">
                        Unknown event type
                        <br><small>${e.timestamp || ""}</small>
                    </div>`;
                }
            });
        }

        container.innerHTML = html;

    } catch (error) {
        console.error("Fetch error:", error);
        document.getElementById("events").innerHTML =
            "<div class='event'>Error loading events</div>";
    }
}

// Poll every 15 seconds
setInterval(fetchEvents, 15000);

// Initial load
fetchEvents();
