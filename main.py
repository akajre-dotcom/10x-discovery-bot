report = "WEEKLY OPPORTUNITY DASHBOARD\n"
report += "="*50 + "\n\n"

for _, row in selected.iterrows():

    tag = generate_tag({
        "Name": row["Name"],
        "Bucket": row["Bucket"]
    })

    report += f"{row['Name']}\n"
    report += f"{tag}\n"
    report += "-"*40 + "\n"
