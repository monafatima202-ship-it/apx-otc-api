const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
    const pair = req.query.pairs || "UNKNOWN_PAIR";
    
    // Time format set karna
    const now = new Date();
    const timeString = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:00 — +05:00 🇵🇰`;

    // JSON Data
    const responseData = {
      developer: "@Sadiq_Hussain",
      telegram: "https://t.me/your_bot_link",
      market: pair.toUpperCase(),
      data: [
        {
          time: timeString,
          open: "19.91024",
          high: "19.91045",
          low: "19.91010",
          close: "19.91033",
          color: "Green",
          volume: "1299"
        }
      ]
    };

    res.json(responseData);
});

app.listen(port, () => {
    console.log(`Bhai ki API is running on port ${port}`);
});
