import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

df = pd.read_csv("alarm_message_data_user_5.csv")

df["Date"] = pd.to_datetime(df["Server Datetime"]).dt.date
df["VCC"] = df["Position"].str.extract(r"(VCC\d+)")
df["LOOP"] = df["Position"].str.extract(r"LOOP(\d+)")
df["Location"] = df["Position"]

df_unique = df.drop_duplicates(subset=["Date", "Train", "Position"])

pivot = (
    df_unique.groupby(["Location", "Train", "Date"]).size().reset_index(name="count")
)

fig, axes = plt.subplots(1, 2, figsize=(20, 12))

pivot_loc_date = df_unique.groupby(["Location", "Date"]).size().unstack(fill_value=0)
sns.heatmap(pivot_loc_date, cmap="YlOrRd", annot=True, fmt="d", ax=axes[0])
axes[0].set_title("Slip Occurrences by Location and Date", fontsize=14)
axes[0].set_xlabel("Date")
axes[0].set_ylabel("Location (VCC / LOOP)")
axes[0].tick_params(axis="x", rotation=45)

pivot_train_date = df_unique.groupby(["Train", "Date"]).size().unstack(fill_value=0)
sns.heatmap(pivot_train_date, cmap="YlOrRd", annot=True, fmt="d", ax=axes[1])
axes[1].set_title("Slip Occurrences by Train and Date", fontsize=14)
axes[1].set_xlabel("Date")
axes[1].set_ylabel("Train")
axes[1].tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.savefig("slip_heatmap_overview.png", dpi=150, bbox_inches="tight")
plt.close()

pivot_loc_train = df_unique.groupby(["Location", "Train"]).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(24, 16))
sns.heatmap(
    pivot_loc_train, cmap="YlOrRd", annot=True, fmt="d", ax=ax, annot_kws={"size": 8}
)
ax.set_title("Slip Occurrences by Location and Train (All Dates Combined)", fontsize=16)
ax.set_xlabel("Train", fontsize=12)
ax.set_ylabel("Location (VCC / LOOP)", fontsize=12)
plt.tight_layout()
plt.savefig("slip_heatmap_location_train.png", dpi=150, bbox_inches="tight")
plt.close()

dates = sorted(df_unique["Date"].unique())
n_dates = len(dates)
n_cols = 3
n_rows = (n_dates + n_cols - 1) // n_cols

fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5 * n_rows))
axes = axes.flatten() if n_dates > 1 else [axes]

for idx, date in enumerate(dates):
    df_day = df_unique[df_unique["Date"] == date]
    pivot_day = df_day.groupby(["Location", "Train"]).size().unstack(fill_value=0)

    sns.heatmap(
        pivot_day,
        cmap="YlOrRd",
        annot=True,
        fmt="d",
        ax=axes[idx],
        cbar_kws={"shrink": 0.5},
    )
    axes[idx].set_title(f"{date}", fontsize=12)
    axes[idx].set_xlabel("Train", fontsize=10)
    axes[idx].set_ylabel("Location", fontsize=10)
    axes[idx].tick_params(axis="x", rotation=45, labelsize=8)
    axes[idx].tick_params(axis="y", labelsize=7)

for idx in range(len(dates), len(axes)):
    axes[idx].axis("off")

plt.suptitle("Slip Occurrences Heatmap by Date", fontsize=16, y=1.02)
plt.tight_layout()
plt.savefig("slip_heatmap_by_date.png", dpi=150, bbox_inches="tight")
plt.close()

print("Heatmaps generated:")
print("1. slip_heatmap_overview.png - Location/Date and Train/Date views")
print("2. slip_heatmap_location_train.png - Location vs Train (all dates)")
print("3. slip_heatmap_by_date.png - Daily breakdown of Location vs Train")

summary = (
    df_unique.groupby(["Location", "Train", "Date"]).size().reset_index(name="count")
)
print(f"\nTotal unique slip events: {len(df_unique)}")
print(f"Date range: {min(dates)} to {max(dates)}")
print(f"Unique locations: {df_unique['Location'].nunique()}")
print(f"Unique trains: {df_unique['Train'].nunique()}")
