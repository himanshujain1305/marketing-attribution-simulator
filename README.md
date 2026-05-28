# Marketing Attribution Simulator

A Streamlit app that compares how marketing channel performance changes across four attribution models — first-touch, last-touch, linear, and time-decay — using a synthetic customer journey dataset.

---

## Why I Built This

Marketing teams often rely on a single attribution model to make budget decisions, most commonly last-touch. The problem is that last-touch attribution ignores every channel that created or nurtured demand before the final conversion. Channels that appear weak under last-touch may be the primary drivers of awareness or consideration.

I built this tool to make that tradeoff visible. By running all four major attribution models side by side on the same dataset, the simulator shows how channel rankings shift depending on which model is applied — and why that matters before reallocating budget.

---

## What the Tool Does

The simulator takes a customer journey dataset (one row per marketing touchpoint) and computes attributed revenue and ROI for every channel under four attribution models simultaneously. Results are displayed as interactive charts, a summary table, and auto-generated marketing insights.

**The app helps answer:**
- Which channels receive revenue credit under first-touch vs. last-touch attribution?
- Which channels are undervalued when only one attribution model is used?
- How does ROI change across first-touch, last-touch, linear, and time-decay models?
- What should a marketer consider before changing budget allocation?

---

## Dataset Used

The app ships with a **synthetic sample dataset** (`sample_data/sample_customer_journeys.csv`) generated for portfolio and demo purposes. It contains approximately 1,057 touchpoint records across a simulated customer base with multi-step conversion journeys.

**Schema:**

| Column | Description |
|---|---|
| `customer_id` | Unique customer identifier |
| `touch_number` | Sequential position of this touchpoint in the journey |
| `touch_date` | Date of the touchpoint |
| `channel` | Marketing channel (e.g., Email, Paid Search, Display) |
| `campaign` | Campaign name |
| `converted` | Whether the customer ultimately converted (1/0) |
| `revenue` | Revenue attributed to the conversion event |
| `cost` | Cost associated with this touchpoint |

You can also upload your own CSV in the same format using the sidebar file uploader.

> **Note:** All data used in this project is synthetic and was generated solely for demonstration purposes. It does not represent any real customers, campaigns, or business.

---

## Attribution Models Included

| Model | Logic |
|---|---|
| **First-touch** | 100% of revenue credit goes to the first channel a customer encountered |
| **Last-touch** | 100% of revenue credit goes to the final channel before conversion |
| **Linear** | Revenue credit is split equally across all touchpoints in the journey |
| **Time-decay** | More credit is given to touchpoints closer to conversion, using an exponential decay function (decay rate: 0.6) |

---

## Features

- **Executive summary** — total customers, converted customers, conversion rate, and total revenue at a glance
- **Model comparison chart** — grouped bar chart showing attributed revenue per channel under all four models simultaneously
- **Channel ROI chart** — grouped bar chart showing how ROI shifts across models per channel
- **Attribution summary table** — full tabular view of attributed revenue, attributed conversions, cost, and ROI by channel and model
- **Auto-generated insights** — plain-language interpretation of which channels look strongest under each model
- **Recommended next move** — contextual guidance on how to interpret and act on the results
- **Downloadable cleaned CSV** — export the cleaned customer journey dataset
- **Downloadable markdown action plan** — export a templated attribution action plan as a `.md` file
- **CSV upload** — bring your own customer journey data in the same schema

---

## Screenshots

> Screenshots will be added after deployment.

| View | Description |
|---|---|
| `screenshot_executive_summary.png` | Top-level KPI metrics |
| `screenshot_model_comparison.png` | Attributed revenue by channel and model |
| `screenshot_roi_comparison.png` | ROI by channel and model |
| `screenshot_insights.png` | Auto-generated marketing interpretation |

---

## How to Run Locally

**Prerequisites:** Python 3.9+

```bash
# Clone the repo
git clone https://github.com/himanshujain/marketing-attribution-simulator.git
cd marketing-attribution-simulator

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`. It loads the sample dataset automatically on launch. Use the sidebar to switch to your own CSV.

---

## Example Use Case

Suppose you are a marketing analyst reviewing Q1 performance. Under last-touch attribution, Paid Search claims 60% of revenue. Before cutting Email spend, you open the simulator, upload your journey data, and check the Linear and First-touch views. You find that Email consistently drives first engagement for customers who eventually convert via Paid Search. Under linear attribution, Email's ROI exceeds Paid Search. Cutting Email would likely reduce the pipeline that Paid Search closes.

This is the kind of analysis the simulator is designed to surface quickly, without writing custom SQL or building a new dashboard from scratch.

---

## Key Learning

Building this reinforced a core principle in marketing analytics: **attribution models are lenses, not ground truth.** Each model tells a different part of the same story. First-touch answers "what created demand?" Last-touch answers "what closed the deal?" Linear answers "what contributed throughout?" Time-decay answers "what mattered most near conversion?"

No single model is correct. The insight comes from comparing them.

---

## Future Improvements

- Add a **U-shaped (position-based) attribution model** (40% first, 40% last, 20% middle)
- Add a **custom weight attribution** builder where the user sets their own touchpoint weights
- Add a **channel overlap heatmap** showing which channels appear together most often in converting journeys
- Add support for **date range filtering** to compare attribution across time periods
- Add a **cohort view** to track how attribution patterns shift by acquisition month
- Deploy to Streamlit Community Cloud with a persistent demo link

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.9+ | Core language |
| Streamlit | App framework and UI |
| Pandas | Data manipulation and attribution calculations |
| NumPy | Numerical operations (ROI, decay weights) |
| Plotly Express | Interactive bar charts |

---

Built by Himanshu Jain — Marketing Analytics Portfolio Project
