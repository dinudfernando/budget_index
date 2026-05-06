# Budget Index
![image](https://github.com/dinudfernando/budget_index/blob/main/src/assets/budget_index_logo.png)


Budget Index is a personal finance dashboard built with Streamlit and pandas. It lets you track income and expenses, visualize trends over time, compare categories, and drill down into detailed views for each spending or income category.

---

## Features

- At‑a‑glance dashboard with KPIs, income vs expense donut, and watchlist of categories. 
- Timeframe switcher (W, M, Q, Y, 2Y, 5Y) that filters all charts and KPIs from the same control.  
- Category detail page with:
  - Category selector and group (Income/Expenses) subheading  
  - Interactive historical chart with pan/zoom and short date labels  
  - Timeframe control + “New Data” navigation  
  - Stats panel (sum, average, median, min, max, volatility, frequency)  
  - Comparison panel (donut chart vs other categories in the same group, standing, portion, totals)  
  - View History table with search, filter, and sort  
- Data Entry page to add new income or expense records into `transactions.json`, with validation and group‑specific category lists.  

---

## How to Run

From the project root:

1. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate    # macOS / Linux
   # or
   .\.venv\Scripts\activate     # Windows
   ```

2. Install dependencies (example):

   ```bash
   pip install streamlit pandas altair
   ```

3. Run the app (entrypoint is under `dist/`):

   ```bash
   streamlit run dist/main.py
   ```

4. Open the URL Streamlit prints (usually `http://localhost:8501`) in your browser.

---

## Usage / Help

### Main dashboard (`main.py`)

- Use the timeframe switcher (W, M, Q, Y, 2Y, 5Y) at the top to change the window for all charts and KPIs. 
- Read the KPI cards (Total Income, Total Expenses, Net Cash Flow, Savings Rate) to get a quick snapshot.  
- The income vs expenses donut shows the proportion between the two groups.  
- In the watchlist, click any category button (e.g., “Food”, “Housing”, “Salary”) to open its detailed category page in `category_info.py`.  

### Category detail (`pages/category_info.py`)

- The **Category** selector in the header picks which category you’re inspecting.  
- The group caption under the title shows whether it’s an Income or Expenses category.  
- The main line chart shows historical amounts over time; use mouse drag and scroll to zoom and pan.  
- Below the chart:
  - Use the timeframe switcher on the left to filter that category’s history (W, M, Y, 2Y, 5Y).  
  - Click “+ New Data” to navigate to the data entry page.  
- The **Stats** panel shows key numbers for the selected timeframe:
  - Sum, Average, Median, Frequency, Max, Min, Volatility‑like metric, and timing information.  
- The **Comparison** panel shows:
  - Donut chart of the selected category vs “All Others” in the same group  
  - Standing (rank within group), Portion (% of group total), Category Total, Group Total.  
- The **View History** section:
  - Use the search box to filter by date, amount, tag, or group text.  
  - Use the Tag dropdown and Sort by date controls to refine the table.  
  - The table itself is sortable by clicking column headers. 

### New data entry (`pages/data_entry.py`)

- Use the **Group** dropdown to choose Income or Expenses. The **Category** list updates based on the selected group.  
- Set the **Date**, **Amount**, and **Tag**.  
- Click **Save Record** to append the transaction to `transactions.json`.  
- On success, the new record is shown and the dashboard will pick it up on the next run (or after cache clears).

---

## File Structure

High‑level layout (only key paths shown):

```text
project-root/
├─ README.md          # This file, app overview and instructions
├─ dist/
│  ├─ main.py         # Main dashboard (At a Glance / watchlist / timeframe switcher)
│  ├─ data/
│  │  ├─ transactions.json  # Transaction data (date, group, category, amount, tag)
│  │  └─ budgets.json       # Monthly budgets per category
│  └─ pages/
│     ├─ category_info.py   # Category detail page (chart, stats, comparison, history)
│     └─ data_entry.py   
├─ src/
│  ├─ main.py        
│  ├─ data/
│  │  ├─ transactions.json  
│  │  └─ budgets.json       
│  └─ pages/
│     ├─ category_info.py   
│     └─ data_entry.py      
└─ .venv/ (optional)  # Virtual environment (ignored in most repos)
```

### `dist/main.py`

- Thin entrypoint used by `streamlit run dist/main.py`.  
- Typically imports and runs the main dashboard logic or redirects to `src/main.py`.

---
## AI Usage
- Readme Documentation 
-