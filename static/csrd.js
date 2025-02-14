google.charts.load('current', { packages: ['gauge'] });
google.charts.setOnLoadCallback(drawChart);

let gaugeChart, gaugeOptions, gaugeData;

function drawChart() {
    gaugeData = google.visualization.arrayToDataTable([
        ['Label', 'Value'],
        ['Score', 50] 
    ]);

    gaugeOptions = {
        width: 400, height: 200,
        redFrom: 0, redTo: 40,
        yellowFrom: 41, yellowTo: 70,
        greenFrom: 71, greenTo: 100,
        minorTicks: 5
    };

    gaugeChart = new google.visualization.Gauge(document.getElementById('speedometerChart'));
    gaugeChart.draw(gaugeData, gaugeOptions);
}

document.getElementById("analyzeForm").addEventListener("submit", function (e) {
    e.preventDefault();

    let username = document.getElementById("profileUrl").value.trim();
    if (!username) {
        alert("Please enter an Instagram username!");
        return;
    }

    document.getElementById("analyzeBtn").textContent = "Analyzing...";
    
    fetch("/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: username }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            
            document.getElementById("followers").textContent = data.followers;
            document.getElementById("likes").textContent = data.uploads;
            document.getElementById("comments").textContent = data.following;

            
            gaugeData.setValue(0, 1, data.real_probability);
            gaugeChart.draw(gaugeData, gaugeOptions);
        }
    })
    .catch(error => console.error("Error:", error))
    .finally(() => {
        document.getElementById("analyzeBtn").textContent = "Analyze";
    });
});
