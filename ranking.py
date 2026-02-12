import pandas as pd

def select_structured(df):

    selected = []

    # Category 1 – Top 3 Sales Growth
    top_sales = df.sort_values("SalesGrowth", ascending=False).head(3)
    selected.append(top_sales)

    # Category 2 – Top 3 ROCE (not already selected)
    remaining = df[~df["Name"].isin(pd.concat(selected)["Name"])]
    top_roce = remaining.sort_values("ROCE", ascending=False).head(3)
    selected.append(top_roce)

    # Category 3 – Top 3 Profit Growth
    remaining = df[~df["Name"].isin(pd.concat(selected)["Name"])]
    top_profit = remaining.sort_values("ProfitGrowth", ascending=False).head(3)
    selected.append(top_profit)

    # Category 4 – Smallest market cap in top quartile growth
    remaining = df[~df["Name"].isin(pd.concat(selected)["Name"])]
    quartile = remaining["SalesGrowth"].quantile(0.75)
    high_growth = remaining[remaining["SalesGrowth"] >= quartile]
    small_caps = high_growth.sort_values("MarketCap").head(2)
    selected.append(small_caps)

    # Category 5 – Early stage ROCE band
    remaining = df[~df["Name"].isin(pd.concat(selected)["Name"])]
    early_stage = remaining[
        (remaining["ROCE"] >= 12) &
        (remaining["ROCE"] <= 18) &
        (remaining["SalesGrowth"] > 40)
    ].head(2)
    selected.append(early_stage)

    final_df = pd.concat(selected).drop_duplicates("Name")

    return final_df
