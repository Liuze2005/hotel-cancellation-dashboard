from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Hotel Revenue Dashboard", layout="wide")

# ---- 读取数据（放在和 app.py 同目录下）----
DATA_FILE = Path(__file__).parent / "hotel_bookings.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df["arrival_date"] = pd.to_datetime(
        df["arrival_date_year"].astype(str) + "-" + df["arrival_date_month"] + "-"
        + df["arrival_date_day_of_month"].astype(str),
        format="%Y-%B-%d", errors="coerce",
    )
    df["arrival_ym"] = df["arrival_date"].dt.to_period("M")
    # 清洗 ADR：剔除负数和极端高价，避免平均值失真
    df = df[(df["adr"] > 0) & (df["adr"] <= 2000)].copy()
    return df

df = load_data()

# ---- 标题（带队名）+ 一句话说明 ----
st.title("Hotel Revenue Dashboard")
st.caption(
    "For the Hotel Revenue Manager — monitor booking cancellation and ADR "
    "to decide whether to raise or lower room prices."
)

# ---- 筛选器：决策者真正会用到的 ----
st.sidebar.header("Filters")
hotel_sel = st.sidebar.selectbox("Hotel", ["All", "Resort Hotel", "City Hotel"])
month_sel = st.sidebar.selectbox("Arrival Month", ["All"] + sorted(
    [str(m) for m in df["arrival_date"].dt.to_period("M").unique()]))

d = df.copy()
if hotel_sel != "All":
    d = d[d["hotel"] == hotel_sel]
if month_sel != "All":
    d = d[d["arrival_ym"].astype(str) == month_sel]

# ---- 顶部：3 个 headline KPI（st.metric 横排）----
total = len(d)
canceled = int(d["is_canceled"].sum())
cancel_rate = canceled / total if total else 0
avg_adr = d["adr"].mean() if total else 0
net_bookings = total - canceled

c1, c2, c3 = st.columns(3)
c1.metric("Overall Cancellation Rate", f"{cancel_rate:.1%}")
c2.metric("Average Daily Rate (ADR)", f"€{avg_adr:.2f}")
c3.metric("Net Valid Bookings", f"{net_bookings:,}")

# ---- 中部：支撑图表 1（为什么 KPI 动了）----
st.subheader("Why did it move? — Monthly cancellation rate vs ADR")
monthly = (d.groupby("arrival_ym")
           .agg(total=("is_canceled", "count"), cancel=("is_canceled", "sum"),
                adr=("adr", "mean"))
           .reset_index())
monthly["cancel_rate"] = monthly["cancel"] / monthly["total"]
monthly["ym"] = monthly["arrival_ym"].dt.to_timestamp()
st.line_chart(monthly.set_index("ym")["cancel_rate"],
              y_label="Cancellation rate")

# ---- 中部：支撑图表 2（是哪个渠道在贡献取消）----
st.subheader("Cancellation rate by market segment")
seg = (d.groupby("market_segment")["is_canceled"].mean()
       .sort_values(ascending=False))
st.bar_chart(seg, y_label="Cancellation rate")

# ---- 给决策者的行动提示 ----
st.markdown("### Pricing decision guidance")
if cancel_rate > 0.35:
    st.warning("High cancellation rate — consider a lower rate or a "
               "non-refundable tier to cut booking risk.")
elif cancel_rate < 0.20:
    st.success("Low cancellation, strong demand — consider testing a price increase.")
else:
    st.info("Cancellation within normal range — hold current pricing and keep monitoring.")

# ---- 数据误导风险说明 ----
st.caption(
    "Caveats: ADR values ≤0 or >2000 are filtered out. "
    "Non-Refund deposits can still be cancelled. "
    "The dataset is a static Kaggle snapshot (not live PMS data)."
)

# ---- 底部：数据期间 + 生产刷新频率（Step 4 硬性要求）----
st.info(
    "Data: Jul 2015 – Aug 2017, Kaggle snapshot. "
    "In production: refreshed nightly from the PMS; the revenue manager "
    "reviews every morning, with a deep-dive on Mondays."
)
