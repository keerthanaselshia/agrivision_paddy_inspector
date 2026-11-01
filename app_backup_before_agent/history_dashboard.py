
import pandas as pd
import streamlit as st

from history_db import get_inspections


def show_history_dashboard():
    st.header("Inspection History")
    st.caption("Review previously saved paddy leaf inspections.")

    records = get_inspections()

    if not records:
        st.info(
            "No inspection history yet. "
            "Complete and save a leaf inspection to see it here."
        )
        return

    df = pd.DataFrame(records)
    df["inspected_at"] = pd.to_datetime(
        df["inspected_at"], errors="coerce"
    )

    # Summary metrics
    total = len(df)
    disease_count = df["disease"].value_counts()

    disease_cols = st.columns(3)
    disease_cols[0].metric("Total inspections", total)

    if not disease_count.empty:
        disease_cols[1].metric(
            "Most recorded class",
            disease_count.index[0]
        )
    else:
        disease_cols[1].metric("Most recorded class", "—")

    valid_severity = pd.to_numeric(
        df["severity"], errors="coerce"
    ).dropna()

    average_severity = (
        f"{valid_severity.mean():.1f}%"
        if not valid_severity.empty else "—"
    )
    disease_cols[2].metric(
        "Average recorded severity", average_severity
    )

    st.subheader("Disease distribution")
    st.bar_chart(disease_count)

    # Filters
    st.subheader("Find inspections")

    search = st.text_input(
        "Search disease or location",
        placeholder="Example: Blast or Erode"
    )

    locations = sorted(
        value for value in df["location"].dropna().unique()
        if str(value).strip()
    )

    selected_location = st.selectbox(
        "Filter by location",
        ["All locations"] + locations
    )

    min_date = df["inspected_at"].min()
    max_date = df["inspected_at"].max()

    if pd.notna(min_date) and pd.notna(max_date):
        date_range = st.date_input(
            "Inspection date range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
    else:
        date_range = ()

    filtered = df.copy()

    if search.strip():
        query = search.strip()
        matches = (
            filtered["disease"].astype(str).str.contains(
                query, case=False, na=False
            )
            | filtered["location"].astype(str).str.contains(
                query, case=False, na=False
            )
        )
        filtered = filtered[matches]

    if selected_location != "All locations":
        filtered = filtered[
            filtered["location"] == selected_location
        ]

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered[
            filtered["inspected_at"].dt.date.between(
                start_date, end_date
            )
        ]

    # Table
    st.subheader("Saved inspection records")
    st.caption(f"{len(filtered)} matching record(s)")

    display_df = filtered.rename(columns={
        "id": "ID",
        "inspected_at": "Inspection time",
        "disease": "Predicted class",
        "confidence": "Confidence (%)",
        "severity": "Severity (%)",
        "severity_grade": "Severity grade",
        "location": "Location"
    })

    columns = [
        "ID",
        "Inspection time",
        "Predicted class",
        "Confidence (%)",
        "Severity (%)",
        "Severity grade",
        "Location"
    ]

    st.dataframe(
        display_df[columns],
        use_container_width=True,
        hide_index=True
    )
