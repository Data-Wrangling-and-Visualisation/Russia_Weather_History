# Weather Station Viewer

This project is a web application for visualizing historical weather data from weather stations. It scrapes data from [pogoda-service.ru](http://pogoda-service.ru), saves it in CSV format, and shows it with an interactive frontend with D3.js.

---
## Running the project

### 1. Run the backend
Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The server will run at: `http://127.0.0.1:8000`

### 2. Serve the frontend
In a separate terminal, serve the frontend using a simple HTTP server:

```bash
python -m http.server 8001
```

Then open: [http://localhost:8001](http://localhost:8001)

---

## API Endpoints

| Endpoint               | Description                                 |
|------------------------|---------------------------------------------|
| `/stations`            | List of all stations with metadata          |
| `/data/{station_id}`   | Returns CSV data for selected station       |
| `/missing/{station_id}`| Missing value stats per year (optional)     |

---

## Next steps

- Finish id to station name mapping
- Implement better NaN diagnostics
- Add filters by year, region, or data quality
- (Possibly) Move data to a separate database, like Mongo.
- (Possibly) Add map visualization of station locations
