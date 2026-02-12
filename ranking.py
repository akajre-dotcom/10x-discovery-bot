import pandas as pd

def normalize(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-9)

def rank_stocks(df):
    df["NormSales"] = normalize(df["SalesGrowth"])
    df["NormROCE"] = normalize(df["ROCE"])

    df["Score"] = 0.6 * df["NormSales"] + 0.4 * df["NormROCE"]

    priority = {"Moonshot": 1, "Acceleration": 2, "Growth": 3}
    df["Priority"] = df["Bucket"].map(priority)

    df = df.sort_values(by=["Priority", "Score"], ascending=[True, False])
    df = df.drop_duplicates(subset="Name", keep="first")

    top_growth = df[df["Bucket"] == "Growth"].head(5)
    top_acc = df[df["Bucket"] == "Acceleration"].head(5)
    top_moon = df[df["Bucket"] == "Moonshot"].head(5)

    final_df = pd.concat([top_growth, top_acc, top_moon])

    return final_df
