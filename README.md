# Hotel Revenue Dashboard — Team 6 Liu Zeyu

A Streamlit dashboard that helps a hotel revenue manager use booking-cancellation
data to decide whether to raise or lower room prices.

## Step 1 — Dataset and Decision-Maker

**Dataset:** Hotel Booking Demand
- Source: [Kaggle — Hotel Booking Demand](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand)
- Real, anonymized booking records from two Portuguese hotels (Resort Hotel and City Hotel).
- Time period: July 2015 – August 2017 (2017 data is incomplete, stops in August).
- One row = one booking record.
- File size ~17 MB (below the 25 MB limit; no sampling or aggregation was needed).

**Decision-maker (one role, not "everyone"):**
The **Hotel Revenue Manager**. This role repeatedly monitors bookings, cancellations,
ADR, occupancy and channel mix, and acts on them: adjusting how many rooms go to
each OTA channel, tightening cancellation policy, and raising or lowering prices.

## Step 2 — Justify the Dashboard

**1. Who looks at it, and how often?**
The revenue manager checks every morning for daily signals and does a full weekly
review every Monday before the pricing meeting.

**2. What decision does it support?**
> If the revenue manager sees that the cancellation rate is high while booking
> volume stays strong, they will consider **lowering** room prices (demand exists,
> the price is the problem). If the cancellation rate is low and bookings are still
> growing, they will consider **raising** prices (demand is strong).

**3. What do they do today without it, and what does it cost?**
Today they export spreadsheets and build pivot tables by hand, or wait for IT's
monthly report. Cost: abnormal cancellation is noticed too late, rooms sit empty,
price changes lag the market, and channels can't be compared side by side. Both
overpricing (empty rooms) and underpricing (forgone revenue) cost money.

**4. Why a dashboard, not a weekly email / report / alert?**
The revenue manager re-asks the same questions every day: cancellation rate, ADR,
occupancy, channel performance. Static emails can't be filtered by hotel, month or
segment. Alerts only work for single thresholds and can't give the overall picture.
So: a dashboard for the recurring overview, plus one alert for high-cancellation risk.

## Step 3 — What Matters

**EDA (done in a notebook):** checked shape, dtypes, missing values (company/agent
largely null, some country null), the ~37% cancellation rate, Resort vs City
difference (City ~42%, Resort ~28%), cancellation by market segment and channel,
lead-time vs cancellation, ADR outliers (negative and extremely high values), and
seasonality by arrival month.

**Top of the page — 3 headline KPIs (`st.metric`, in `st.columns`):**
1. Overall cancellation rate — the single most important signal for pricing.
2. Average Daily Rate (ADR) — cleaned to remove outliers.
3. Net valid bookings — how much revenue is actually realized.

**Middle — supporting charts that explain WHY a KPI moved:**
1. Monthly cancellation-rate trend — reveals when a spike happened.
2. Cancellation rate by market segment — locates which channel is driving cancellations.

**Filters (only what the decision-maker uses):** Hotel (Resort / City) and arrival
month. Enough to slice the view without clutter.

**Order rationale:** KPI first answers "is anything wrong right now"; charts explain
why; no large detail table is shown because the revenue manager never reads raw
booking rows.

**Two things we chose NOT to show, and why:**
1. A full country breakdown map — interesting for marketing, but it does not change a
   pricing or channel-quota decision.
2. The raw agent/company ID list — heavily null, anonymized, and not something the
   manager acts on.

**Things in the data that could mislead the viewer, and how we handle them:**
1. Negative and extreme-high ADR values would skew the average → we filter ADR ≤ 0
   and > 2000 and caption it.
2. Non-Refund deposits can still be cancelled (a classic counter-intuitive point) →
   noted in the caveats caption.
3. The dataset ends in August 2017 and is a static Kaggle snapshot → clearly labeled.

## Step 4 — Refresh Frequency

**1. How often should data refresh?** Nightly.
Bookings and cancellations change every day, but pricing and quota decisions run on
a daily/weekly cycle, so real-time refresh adds cost without improving decisions.
Exception: arrivals within the next 3 days should be a same-day alert, not a
dashboard check.

**2. How often should someone review it?** Every morning for the revenue manager,
with a Monday deep-dive. Data refresh (nightly) is not the same as review cadence.

**3. What should be tracked over time, and what triggers action?**
Track the 30-day-ahead cancellation rate by segment. Trigger: if any segment's
cancellation rate exceeds its historical average by more than +10 percentage points,
the manager calls the channel and re-negotiates quota or policy.

**4. What does stale data cost?** One day late may mean several empty rooms; one week
late during peak season can lose a full week of revenue. Hence nightly is reasonable.

**Dashboard footnote (shown in the app):**
> Data: Jul 2015 – Aug 2017, Kaggle snapshot. In production: refreshed nightly from
> the PMS; the revenue manager reviews every morning, with a deep-dive on Mondays.
