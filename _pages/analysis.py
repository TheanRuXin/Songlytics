import os
from io import BytesIO
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.express as px

from dotenv import load_dotenv

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

load_dotenv()

DATASET_PATH = os.getenv(
    "SPOTIFY_DATASET_PATH",
    "C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_cleaned.csv"
)

AUDIO_FEATURES = {
    "Danceability": "danceability",
    "Energy": "energy",
    "Loudness": "loudness",
    "Speechiness": "speechiness",
    "Acousticness": "acousticness",
    "Instrumentalness": "instrumentalness",
    "Liveness": "liveness",
    "Valence": "valence",
    "Tempo": "tempo"
}

@st.cache_data
def load_dataset():
    df = pd.read_csv(
        DATASET_PATH
    )

    numeric_columns = [
        "popularity",
        "duration_ms",
        "danceability",
        "energy",
        "loudness",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    df = df.dropna(
        subset=[
            "popularity",
            "track_genre"
        ]
    )

    df["track_genre"] = (
        df["track_genre"]
        .astype(str)
        .str.strip()
    )

    return df

def format_duration(milliseconds):
    if pd.isna(milliseconds):
        return "N/A"

    seconds = int(
        milliseconds / 1000
    )

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    return (
        f"{minutes}:"
        f"{remaining_seconds:02d}"
    )

def correlation_description(value):
    if pd.isna(value):
        return "Unavailable"

    abs_value = abs(value)

    if abs_value < 0.1:
        strength = "Very weak"

    elif abs_value < 0.3:
        strength = "Weak"

    elif abs_value < 0.5:
        strength = "Moderate"

    elif abs_value < 0.7:
        strength = "Strong"

    else:
        strength = "Very strong"

    if value > 0:
        direction = "positive"

    elif value < 0:
        direction = "negative"

    else:
        return "No linear relationship"

    return (
        f"{strength} {direction} "
        "linear relationship"
    )

def generate_analysis_pdf(
    df,
    selected_genre,
    explicit_filter,
    popularity_range,
    feature_label,
    feature_column
):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=14
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=10,
        spaceAfter=8
    )

    body_style = styles["BodyText"]

    elements = []

    elements.append(
        Paragraph(
            "Songlytics Analysis Report",
            title_style
        )
    )

    elements.append(
        Paragraph(
            "Generated: "
            + datetime.now().strftime(
                "%d %b %Y %H:%M"
            ),
            body_style
        )
    )

    elements.append(
        Spacer(
            1,
            12
        )
    )

    elements.append(
        Paragraph(
            "Selected Filters",
            heading_style
        )
    )

    filter_data = [
        [
            "Filter",
            "Selection"
        ],
        [
            "Genre",
            selected_genre
        ],
        [
            "Explicit Content",
            explicit_filter
        ],
        [
            "Popularity Range",
            (
                f"{popularity_range[0]} - "
                f"{popularity_range[1]}"
            )
        ]
    ]

    filter_table = Table(
        filter_data,
        colWidths=[
            6 * cm,
            10 * cm
        ]
    )

    filter_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    elements.append(
        filter_table
    )

    elements.append(
        Paragraph(
            "Dataset Summary",
            heading_style
        )
    )

    total_songs = len(df)

    avg_popularity = (
        df["popularity"].mean()
        if total_songs
        else 0
    )

    total_genres = (
        df["track_genre"]
        .nunique()
        if total_songs
        else 0
    )

    avg_duration = (
        df["duration_ms"].mean()
        if total_songs
        else 0
    )

    summary_data = [
        [
            "Metric",
            "Value"
        ],
        [
            "Total Songs",
            f"{total_songs:,}"
        ],
        [
            "Average Popularity",
            f"{avg_popularity:.2f}"
        ],
        [
            "Total Genres",
            str(total_genres)
        ],
        [
            "Average Duration",
            format_duration(
                avg_duration
            )
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            8 * cm,
            8 * cm
        ]
    )

    summary_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    elements.append(
        summary_table
    )

    elements.append(
        Paragraph(
            "Popularity Distribution",
            heading_style
        )
    )

    popularity_bins = pd.cut(
        df["popularity"],
        bins=[
            -1,
            20,
            40,
            60,
            80,
            100
        ],
        labels=[
            "0-20",
            "21-40",
            "41-60",
            "61-80",
            "81-100"
        ]
    )

    distribution = (
        popularity_bins
        .value_counts()
        .sort_index()
    )

    distribution_data = [
        [
            "Popularity Range",
            "Number of Songs"
        ]
    ]

    for index, value in distribution.items():
        distribution_data.append([
            str(index),
            f"{int(value):,}"
        ])

    distribution_table = Table(
        distribution_data,
        colWidths=[
            8 * cm,
            8 * cm
        ]
    )

    distribution_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    elements.append(
        distribution_table
    )

    elements.append(
        Paragraph(
            "Top Genres by Average Popularity",
            heading_style
        )
    )

    genre_summary = (
        df.groupby(
            "track_genre"
        )
        .agg(
            average_popularity=(
                "popularity",
                "mean"
            ),
            songs=(
                "track_genre",
                "size"
            )
        )
        .reset_index()
        .sort_values(
            "average_popularity",
            ascending=False
        )
        .head(10)
    )

    genre_data = [
        [
            "Genre",
            "Average Popularity",
            "Songs"
        ]
    ]

    for _, row in genre_summary.iterrows():
        genre_data.append([
            str(
                row["track_genre"]
            ),
            f"{row['average_popularity']:.2f}",
            str(
                int(
                    row["songs"]
                )
            )
        ])

    genre_table = Table(
        genre_data,
        colWidths=[
            7 * cm,
            5 * cm,
            4 * cm
        ]
    )

    genre_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    elements.append(
        genre_table
    )

    elements.append(
        Paragraph(
            "Audio Feature Analysis",
            heading_style
        )
    )

    valid_feature_data = (
        df[
            [
                feature_column,
                "popularity"
            ]
        ]
        .dropna()
    )

    if len(valid_feature_data) > 1:
        correlation = (
            valid_feature_data[
                feature_column
            ]
            .corr(
                valid_feature_data[
                    "popularity"
                ]
            )
        )

    else:
        correlation = float("nan")

    feature_text = (
        f"Selected Feature: {feature_label}<br/>"
        f"Correlation with Popularity: "
        f"{correlation:.4f}<br/>"
        f"Interpretation: "
        f"{correlation_description(correlation)}"
    )

    elements.append(
        Paragraph(
            feature_text,
            body_style
        )
    )

    elements.append(
        Spacer(
            1,
            12
        )
    )

    elements.append(
        Paragraph(
            "Note: Correlation describes linear "
            "association and does not indicate causation.",
            body_style
        )
    )

    document.build(
        elements
    )

    buffer.seek(0)

    return buffer.getvalue()

def show_analysis():
    st.title(
        "📊 Music Analysis Dashboard"
    )

    st.caption(
        "Explore song popularity, genres, "
        "and audio characteristics in the "
        "Songlytics dataset."
    )

    try:
        df = load_dataset()

    except Exception as e:
        st.error(
            f"Unable to load dataset: {e}"
        )
        return

    st.subheader(
        "🔍 Filters"
    )

    col1, col2, col3 = st.columns(
        [
            1,
            1,
            2
        ]
    )

    genres = sorted(
        df["track_genre"]
        .dropna()
        .unique()
        .tolist()
    )

    with col1:
        selected_genre = st.selectbox(
            "Genre",
            [
                "All Genres"
            ] + genres
        )

    with col2:
        explicit_filter = st.selectbox(
            "Explicit Content",
            [
                "All",
                "Non-Explicit",
                "Explicit"
            ]
        )

    with col3:
        popularity_range = st.slider(
            "Popularity Score",
            min_value=0,
            max_value=100,
            value=(
                0,
                100
            )
        )

    filtered_df = df.copy()

    if selected_genre != "All Genres":
        filtered_df = filtered_df[
            filtered_df[
                "track_genre"
            ] == selected_genre
        ]

    if explicit_filter == "Explicit":
        filtered_df = filtered_df[
            filtered_df[
                "explicit"
            ].astype(bool)
        ]

    elif (
        explicit_filter
        == "Non-Explicit"
    ):
        filtered_df = filtered_df[
            ~filtered_df[
                "explicit"
            ].astype(bool)
        ]

    filtered_df = filtered_df[
        filtered_df[
            "popularity"
        ].between(
            popularity_range[0],
            popularity_range[1]
        )
    ]

    if filtered_df.empty:
        st.warning(
            "No songs match the selected filters."
        )
        return

    st.divider()

    total_songs = len(
        filtered_df
    )

    avg_popularity = (
        filtered_df[
            "popularity"
        ].mean()
    )

    total_genres = (
        filtered_df[
            "track_genre"
        ].nunique()
    )

    avg_duration = (
        filtered_df[
            "duration_ms"
        ].mean()
    )

    metric1, metric2, metric3, metric4 = (
        st.columns(4)
    )

    with metric1:
        st.metric(
            "Total Songs",
            f"{total_songs:,}"
        )

    with metric2:
        st.metric(
            "Average Popularity",
            f"{avg_popularity:.1f}"
        )

    with metric3:
        st.metric(
            "Genres",
            total_genres
        )

    with metric4:
        st.metric(
            "Average Duration",
            format_duration(
                avg_duration
            )
        )

    st.divider()

    st.subheader(
        "📈 Popularity Distribution"
    )

    popularity_chart = px.histogram(
        filtered_df,
        x="popularity",
        nbins=20,
        labels={
            "popularity":
                "Popularity Score"
        }
    )

    popularity_chart.update_layout(
        xaxis_title="Popularity Score",
        yaxis_title="Number of Songs",
        showlegend=False
    )

    st.plotly_chart(
        popularity_chart,
        use_container_width=True
    )

    st.caption(
        "This chart shows how song popularity "
        "scores are distributed in the selected data."
    )

    st.divider()

    st.subheader(
        "🎵 Genre Analysis"
    )

    genre_summary = (
        filtered_df
        .groupby(
            "track_genre"
        )
        .agg(
            average_popularity=(
                "popularity",
                "mean"
            ),
            songs=(
                "track_genre",
                "size"
            )
        )
        .reset_index()
        .sort_values(
            "average_popularity",
            ascending=False
        )
        .head(10)
    )

    genre_chart = px.bar(
        genre_summary,
        x="average_popularity",
        y="track_genre",
        orientation="h",
        labels={
            "average_popularity":
                "Average Popularity",
            "track_genre":
                "Genre"
        },
        hover_data=[
            "songs"
        ]
    )

    genre_chart.update_layout(
        yaxis={
            "categoryorder":
                "total ascending"
        },
        showlegend=False
    )

    st.plotly_chart(
        genre_chart,
        use_container_width=True
    )

    st.caption(
        "The chart shows the top genres based "
        "on average popularity within the "
        "selected filters."
    )

    st.divider()

    st.subheader(
        "🎚️ Audio Feature Analysis"
    )

    feature_label = st.selectbox(
        "Select an audio feature:",
        list(
            AUDIO_FEATURES.keys()
        )
    )

    feature_column = (
        AUDIO_FEATURES[
            feature_label
        ]
    )

    feature_data = (
        filtered_df[
            [
                feature_column,
                "popularity"
            ]
        ]
        .dropna()
    )

    if len(feature_data) > 1:
        correlation = (
            feature_data[
                feature_column
            ]
            .corr(
                feature_data[
                    "popularity"
                ]
            )
        )

    else:
        correlation = float(
            "nan"
        )

    col1, col2 = st.columns(
        [
            1,
            3
        ]
    )

    with col1:
        st.metric(
            "Correlation",
            (
                f"{correlation:.3f}"
                if pd.notna(
                    correlation
                )
                else "N/A"
            )
        )

        st.info(
            correlation_description(
                correlation
            )
        )

    try:
        bin_count = min(
            10,
            feature_data[
                feature_column
            ].nunique()
        )

        if bin_count >= 2:
            feature_data = (
                feature_data.copy()
            )

            feature_data[
                "feature_range"
            ] = pd.qcut(
                feature_data[
                    feature_column
                ],
                q=bin_count,
                duplicates="drop"
            )

            feature_summary = (
                feature_data
                .groupby(
                    "feature_range",
                    observed=True
                )
                .agg(
                    feature_value=(
                        feature_column,
                        "mean"
                    ),
                    average_popularity=(
                        "popularity",
                        "mean"
                    )
                )
                .reset_index()
            )

            with col2:
                feature_chart = px.line(
                    feature_summary,
                    x="feature_value",
                    y="average_popularity",
                    markers=True,
                    labels={
                        "feature_value":
                            feature_label,
                        "average_popularity":
                            "Average Popularity"
                    }
                )

                feature_chart.update_layout(
                    xaxis_title=feature_label,
                    yaxis_title=(
                        "Average Popularity"
                    )
                )

                st.plotly_chart(
                    feature_chart,
                    use_container_width=True
                )

        else:
            with col2:
                st.info(
                    "Not enough unique values "
                    "to display this chart."
                )

    except Exception:
        with col2:
            st.info(
                "Unable to generate feature chart."
            )

    st.caption(
        "A correlation close to 0 indicates a "
        "weak linear relationship. The Random "
        "Forest model can still learn nonlinear "
        "relationships between multiple features."
    )

    st.divider()

    st.subheader(
        "📄 Analysis Report"
    )

    st.write(
        "Generate a PDF summary based on the "
        "current filters and selected audio feature."
    )

    pdf_data = generate_analysis_pdf(
        filtered_df,
        selected_genre,
        explicit_filter,
        popularity_range,
        feature_label,
        feature_column
    )

    st.download_button(
        label="📄 Generate Analysis PDF Report",
        data=pdf_data,
        file_name=(
            "Songlytics_Analysis_Report.pdf"
        ),
        mime="application/pdf",
        use_container_width=True
    )