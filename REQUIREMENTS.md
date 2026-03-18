# Slip Analysis Dashboard - Requirements

## Overview
An interactive Streamlit dashboard for analyzing train slip occurrences with filtering capabilities and multiple visualization types.

---

## Data Sources

### Primary Data File
- **Default file**: `resources/alarm_message_data_user_5.csv`
- **Format**: CSV with columns:
  - Logger Datetime, Server Datetime
  - Train (e.g., T46)
  - VOBC Status (Active/Passive)
  - VOBC No. (e.g., 291)
  - Cab No (e.g., D391)
  - OM, Alarm, Position (VCC/LOOP), Pos, Detail, Alarm Level
- **User can upload**: Alternative CSV file with same format

### Reference Files
1. **`resources/loop_sequence.xlsx`**
   - Contains geographic location hierarchy in sequential order
   - Sheets: `DT` (Down Track), `UT` (Up Track)
   - Columns: VCC, Loop
   - All location ordering must follow this reference
   - Records not matching this file should be discarded

2. **`resources/TML_Train_ID_Formation.xlsx`**
   - Maps Train ID (EMU NO.) to VOBC IDs
   - Contains: VOBC no. Up End, VOBC no. Down End
   - Used for ID type switching (Train ID / Cab ID / VOBC)

---

## Data Processing Rules

### Direction Determination
- Infer direction (Down/Up) from position sequence matching loop_sequence
- Down (DT): Follows DT sheet sequence
- Up (UT): Follows UT sheet sequence

### Deduplication
- Deduplicate slip events by: timestamp, train, and location
- Variations like "slip1:Braking" vs "slip1:Braking [Location]" count as single occurrence

---

## Global Filters & Controls

### File Selection
- Default: `resources/alarm_message_data_user_5.csv`
- Option to browse and upload alternative CSV file

### Date Range Filter
- Slider to filter date range
- Applies to all dashboards

### Direction Filter
- Checkbox options: Down, Up, or Both
- If both directions selected: charts display side-by-side

### ID Type Selection
- Dropdown menu with options:
  - Train ID (default)
  - Cab ID
  - VOBC
- Mapping from `TML_Train_ID_Formation.xlsx`

---

## Dashboards

### Dashboard 1: Date vs Location Scatter Plot
- **Y-axis**: Date (older to newer, bottom to top)
- **X-axis**: Location (sorted by loop_sequence order)
- **Visualization**: Dot plot where size indicates number of occurrences
- **Filter**: Checkbox to toggle between:
  - All trains (default)
  - Individual trains (multi-select dropdown)

### Dashboard 2: Train ID vs Location Scatter Plot
- **Y-axis**: Train ID
- **X-axis**: Location (sorted by loop_sequence order)
- **Visualization**: Dot plot showing slip occurrences
- **Third dimension**: Date shown as hue (darker = more recent)
- **Sorting option**: Checkbox to sort trains by:
  - Frequency of slips (ascending order)
  - Train ID number (default)

### Dashboard 3: Slip Count by Train (Bar Chart)
- **Y-axis**: Number of slip occurrences
- **X-axis**: Train ID (sorted in descending order by count)
- **Hue**: Date of occurrence (darker = more recent)

### Dashboard 4: Slip Count by Location (Bar Chart)
- **Y-axis**: Number of slip occurrences
- **X-axis**: Location (VCC/LOOP combination, sorted descending by count)
- **Note**: Does NOT need to follow loop_sequence order
- **Hue**: Date of occurrence (darker = more recent)

### Dashboard 5: Correlation Heatmaps
Three separate heatmap charts showing slip correlation:
- **A. Train ID vs Location**
- **B. Train ID vs Time of Day**
- **C. Location vs Time of Day**

---

## Technical Notes

- Framework: Streamlit
- Exclude files in `./old implementation` folder
- Location format in data: "VCC1 / LOOP4" (parsed to match loop_sequence)
