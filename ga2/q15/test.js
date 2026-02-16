const https = require("https");

const data = JSON.stringify({
    type: "array",
    value: [59, 69, 14, 1, 4, 85, 13],
});

const opts = {
    hostname: "tds-ga2-q15.tds-23f3003225.workers.dev",
    path: "/data",
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "Content-Length": data.length,
    },
};

const req = https.request(opts, (res) => {
    let body = "";
    res.on("data", (chunk) => (body += chunk));
    res.on("end", () => {
        console.log("Status:", res.statusCode);
        console.log("Response:", body);
    });
});

req.write(data);
req.end();
