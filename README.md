# Slip Analysis Dashboard

An interactive Streamlit dashboard for analyzing train slip occurrences data.

## Features

- **7 Interactive Dashboards** for visualizing slip patterns
- **Rainfall Correlation** - Overlay HKO daily rainfall data on scatter plots and heatmaps
- **Direction Filtering** - View Down (DT), Up (UT), or both directions side-by-side
- **ID Type Selection** - Switch between Train ID, Cab ID, or VOBC
- **Custom Data Upload** - Use your own CSV files with the same format

## Dashboards

1. **Date vs Location** - Scatter plot showing slip occurrences by date and location with rainfall overlay
2. **Date vs Train** - Scatter plot showing slip occurrences by date and train with rainfall overlay
3. **Train vs Location** - Scatter plot with date as color hue (Viridis palette)
4. **Slip Count by Train** - Stacked bar chart showing slip counts per train by date
5. **Slip Count by Location** - Stacked bar chart showing slip counts per location by date
6. **Slip Count by Date** - Stacked bar chart showing slip counts per date by train
7. **Correlation Heatmaps**:
   - A: Train vs Location
   - B: Train vs Time of Day
   - C: Location vs Time of Day
   - D: Train vs Rainfall
   - E: Location vs Rainfall
8. **Slip Records Table** - Filterable data table with location and ID filters

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/slip-analysis.git
cd slip-analysis

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Data Files

| File | Description |
|------|-------------|
| `resources/alarm_message_data_user_5.csv` | Main slip occurrence data |
| `resources/daily_HKO_RF_ALL.csv` | HKO daily rainfall data (1884-present) |
| `resources/loop_sequence.xlsx` | Location ordering for DT and UT directions |
| `resources/train_id_mapping.xlsx` | Mapping between Train ID, Cab ID, and VOBC |

## Project Structure

```
slip-analysis/
├── app.py                 # Main Streamlit application
├── utils/
│   ├── data_loader.py     # Data loading functions
│   ├── data_processor.py  # Data processing utilities
│   └── charts.py          # Chart generation functions
├── resources/             # Data files
└── requirements.txt       # Python dependencies
```

## Dependencies

- streamlit
- pandas
- plotly
- matplotlib
- openpyxl

## License

MIT License
