import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dotenv import load_dotenv

load_dotenv()

DATASET_PATH = os.getenv(
    "SPOTIFY_DATASET_PATH",
    "C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_cleaned.csv"
)

AUDIO_FEATURES = [
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

@st.cache_data
def load_analysis_data():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    required_columns = [
        "track_id",
        "artists",
        "track_name",
        "popularity",
        "duration_ms",
        "explicit",
        "track_genre"
    ] + AUDIO_FEATURES

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Dataset is missing columns: "
            + ", ".join(missing)
        )

    df["popularity"] = pd.to_numeric(
        df["popularity"],
        errors="coerce"
    )

    df["duration_minutes"] = (
        df["duration_ms"] / 60000
    )

    df["explicit_label"] = df["explicit"].apply(
        lambda value: (
            "Explicit"
            if str(value).lower() in [
                "true",
                "1",
                "yes"
            ]
            else "Non-Explicit"
        )
    )

    df["popularity_range"] = pd.cut(
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

    return df

def apply_filters(
    df,
    selected_genres,
    selected_explicit,
    popularity_range
):
    filtered = df.copy()

    if selected_genres:
        filtered = filtered[
            filtered["track_genre"].isin(
                selected_genres
            )
        ]

    if selected_explicit:
        filtered = filtered[
            filtered["explicit_label"].isin(
                selected_explicit
            )
        ]

    filtered = filtered[
        filtered["popularity"].between(
            popularity_range[0],
            popularity_range[1]
        )
    ]

    return filtered

def show_filters(df):
    st.sidebar.markdown("### 📊 Analysis Filters")

    genres = sorted(
        df["track_genre"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_genres = st.sidebar.multiselect(
        "Genre",
        genres,
        placeholder="All Genres",
        key="analysis_genres"
    )

    selected_explicit = st.sidebar.multiselect(
        "Explicit Content",
        [
            "Explicit",
            "Non-Explicit"
        ],
        default=[
            "Explicit",
            "Non-Explicit"
        ],
        key="analysis_explicit"
    )

    popularity_range = st.sidebar.slider(
        "Popularity Score",
        min_value=0,
        max_value=100,
        value=(0, 100),
        key="analysis_popularity"
    )

    if st.sidebar.button(
        "🔄 Reset Analysis Filters",
        use_container_width=True
    ):
        for key in [
            "analysis_genres",
            "analysis_explicit",
            "analysis_popularity"
        ]:
            st.session_state.pop(
                key,
                None
            )

        st.rerun()

    return (
        selected_genres,
        selected_explicit,
        popularity_range
    )

def show_overview(df):
    st.markdown("## 📊 Dataset Overview")

    total_songs = df["track_id"].nunique()

    average_popularity = (
        df["popularity"].mean()
    )

    total_genres = (
        df["track_genre"].nunique()
    )

    average_duration = (
        df["duration_minutes"].mean()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🎵 Total Songs",
            f"{total_songs:,}"
        )

    with col2:
        st.metric(
            "⭐ Avg Popularity",
            f"{average_popularity:.1f}"
        )

    with col3:
        st.metric(
            "🎧 Total Genres",
            f"{total_genres:,}"
        )

    with col4:
        st.metric(
            "⏱️ Avg Duration",
            f"{average_duration:.2f} min"
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df,
            x="popularity",
            nbins=20,
            title="Popularity Score Distribution",
            labels={
                "popularity":
                    "Popularity Score"
            }
        )

        fig.update_layout(
            yaxis_title="Number of Songs",
            bargap=0.05
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:
        range_counts = (
            df["popularity_range"]
            .value_counts()
            .sort_index()
            .reset_index()
        )

        range_counts.columns = [
            "Popularity Range",
            "Songs"
        ]

        fig = px.pie(
            range_counts,
            names="Popularity Range",
            values="Songs",
            hole=0.45,
            title="Songs by Popularity Range"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    col1, col2 = st.columns(2)

    with col1:
        genre_counts = (
            df.groupby(
                "track_genre",
                observed=True
            )
            .size()
            .reset_index(
                name="Songs"
            )
            .sort_values(
                "Songs",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            genre_counts,
            x="Songs",
            y="track_genre",
            orientation="h",
            title="Top 10 Genres by Number of Songs",
            labels={
                "track_genre": "Genre"
            }
        )

        fig.update_layout(
            yaxis={
                "categoryorder":
                    "total ascending"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:
        explicit_summary = (
            df.groupby(
                "explicit_label",
                observed=True
            )["popularity"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            explicit_summary,
            x="explicit_label",
            y="popularity",
            title=(
                "Average Popularity: "
                "Explicit vs Non-Explicit"
            ),
            labels={
                "explicit_label":
                    "Content Type",
                "popularity":
                    "Average Popularity"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.info(
        "💡 The overview summarizes the current filtered dataset. "
        "All visualizations respond automatically to the filters."
    )

def show_genre_analysis(df):
    st.markdown(
        "## 🎧 Popularity & Genre Analysis"
    )

    if df.empty:
        st.warning(
            "No data available for the selected filters."
        )
        return

    genre_summary = (
        df.groupby(
            "track_genre",
            observed=True
        )
        .agg(
            Songs=(
                "track_id",
                "count"
            ),
            Average_Popularity=(
                "popularity",
                "mean"
            ),
            Median_Popularity=(
                "popularity",
                "median"
            )
        )
        .reset_index()
    )

    genre_summary[
        "Average_Popularity"
    ] = genre_summary[
        "Average_Popularity"
    ].round(2)

    genre_summary[
        "Median_Popularity"
    ] = genre_summary[
        "Median_Popularity"
    ].round(2)

    highest_genre = (
        genre_summary
        .sort_values(
            "Average_Popularity",
            ascending=False
        )
        .iloc[0]
    )

    largest_genre = (
        genre_summary
        .sort_values(
            "Songs",
            ascending=False
        )
        .iloc[0]
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "⭐ Highest Avg Popularity Genre",
            highest_genre[
                "track_genre"
            ],
            f"{highest_genre['Average_Popularity']:.1f}"
        )

    with col2:
        st.metric(
            "🎵 Most Common Genre",
            largest_genre[
                "track_genre"
            ],
            f"{int(largest_genre['Songs']):,} songs"
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        top_popularity = (
            genre_summary
            .sort_values(
                "Average_Popularity",
                ascending=False
            )
            .head(15)
        )

        fig = px.bar(
            top_popularity,
            x="Average_Popularity",
            y="track_genre",
            orientation="h",
            title=(
                "Top 15 Genres by "
                "Average Popularity"
            ),
            labels={
                "track_genre":
                    "Genre",
                "Average_Popularity":
                    "Average Popularity"
            }
        )

        fig.update_layout(
            yaxis={
                "categoryorder":
                    "total ascending"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:
        top_count = (
            genre_summary
            .sort_values(
                "Songs",
                ascending=False
            )
            .head(15)
        )

        fig = px.bar(
            top_count,
            x="Songs",
            y="track_genre",
            orientation="h",
            title=(
                "Top 15 Genres by "
                "Number of Songs"
            ),
            labels={
                "track_genre":
                    "Genre"
            }
        )

        fig.update_layout(
            yaxis={
                "categoryorder":
                    "total ascending"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown(
        "### Genre Representation vs Popularity"
    )

    fig = px.scatter(
        genre_summary,
        x="Songs",
        y="Average_Popularity",
        hover_name="track_genre",
        size="Songs",
        title=(
            "Genre Size vs Average Popularity"
        ),
        labels={
            "Songs":
                "Number of Songs",
            "Average_Popularity":
                "Average Popularity"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "A genre with high average popularity is not necessarily "
        "one of the most common genres in the dataset."
    )

    with st.expander(
        "📋 View Genre Summary Table"
    ):
        display_df = (
            genre_summary
            .rename(
                columns={
                    "track_genre":
                        "Genre",
                    "Average_Popularity":
                        "Average Popularity",
                    "Median_Popularity":
                        "Median Popularity"
                }
            )
            .sort_values(
                "Average Popularity",
                ascending=False
            )
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

def show_audio_analysis(df):
    st.markdown(
        "## 🎚️ Audio Feature Analysis"
    )

    if df.empty:
        st.warning(
            "No data available for the selected filters."
        )
        return

    selected_feature = st.selectbox(
        "Select an audio feature:",
        AUDIO_FEATURES,
        index=1,
        key="audio_analysis_feature"
    )

    feature_label = (
        selected_feature
        .replace("_", " ")
        .title()
    )

    correlation = (
        df[
            [
                selected_feature,
                "popularity"
            ]
        ]
        .corr()
        .iloc[0, 1]
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            f"Average {feature_label}",
            f"{df[selected_feature].mean():.3f}"
        )

    with col2:
        st.metric(
            "Correlation with Popularity",
            f"{correlation:.3f}"
        )

    with col3:
        st.metric(
            "Songs Analyzed",
            f"{len(df):,}"
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        sample_size = min(
            5000,
            len(df)
        )

        scatter_df = df.sample(
            n=sample_size,
            random_state=42
        )

        fig = px.scatter(
            scatter_df,
            x=selected_feature,
            y="popularity",
            opacity=0.35,
            title=(
                f"{feature_label} vs Popularity"
            ),
            labels={
                selected_feature:
                    feature_label,
                "popularity":
                    "Popularity"
            },
            hover_data=[
                "track_name",
                "artists",
                "track_genre"
            ]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:
        fig = px.histogram(
            df,
            x=selected_feature,
            nbins=30,
            title=(
                f"{feature_label} Distribution"
            ),
            labels={
                selected_feature:
                    feature_label
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown(
        "### Average Popularity Across Feature Range"
    )

    bin_df = df[
        [
            selected_feature,
            "popularity"
        ]
    ].dropna().copy()

    bin_df["Feature Range"] = pd.cut(
        bin_df[selected_feature],
        bins=10,
        duplicates="drop"
    )

    grouped = (
        bin_df.groupby(
            "Feature Range",
            observed=True
        )["popularity"]
        .mean()
        .reset_index()
    )

    grouped[
        "Feature Range"
    ] = grouped[
        "Feature Range"
    ].astype(str)

    fig = px.line(
        grouped,
        x="Feature Range",
        y="popularity",
        markers=True,
        title=(
            f"Average Popularity by "
            f"{feature_label} Range"
        ),
        labels={
            "popularity":
                "Average Popularity"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown(
        "### Audio Feature Correlation with Popularity"
    )

    correlations = []

    for feature in AUDIO_FEATURES:
        value = (
            df[
                [
                    feature,
                    "popularity"
                ]
            ]
            .corr()
            .iloc[0, 1]
        )

        correlations.append({
            "Feature":
                feature.replace(
                    "_",
                    " "
                ).title(),
            "Correlation":
                value
        })

    correlation_df = (
        pd.DataFrame(
            correlations
        )
        .sort_values(
            "Correlation"
        )
    )

    fig = px.bar(
        correlation_df,
        x="Correlation",
        y="Feature",
        orientation="h",
        title=(
            "Linear Correlation Between "
            "Audio Features and Popularity"
        )
    )

    fig.add_vline(
        x=0,
        line_width=1
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(
        "💡 Correlation values close to 0 indicate weak linear "
        "relationships. This does not mean the features are useless "
        "for prediction, because machine learning models such as "
        "Random Forest can learn nonlinear relationships and "
        "interactions between multiple features."
    )

    st.markdown(
        "### Audio Feature Correlation Matrix"
    )

    matrix_columns = (
        AUDIO_FEATURES
        + ["popularity"]
    )

    corr_matrix = (
        df[matrix_columns]
        .corr()
    )

    display_labels = [
        column.replace(
            "_",
            " "
        ).title()
        for column in matrix_columns
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=corr_matrix.values,
            x=display_labels,
            y=display_labels,
            zmin=-1,
            zmax=1,
            text=np.round(
                corr_matrix.values,
                2
            ),
            texttemplate="%{text}",
            hovertemplate=(
                "%{y} vs %{x}"
                "<br>Correlation: %{z:.3f}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title="Audio Feature Correlation Matrix",
        height=650
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

def show_analysis():
    st.markdown(
        """
        <style>
        .analysis-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(
                120deg,
                #4ecdc4,
                #ff6b6b
            );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="analysis-title">📊 Music Analytics</p>',
        unsafe_allow_html=True
    )

    st.caption(
        "Interactive analysis of song popularity, genres "
        "and audio characteristics."
    )

    try:
        df = load_analysis_data()

    except Exception as e:
        st.error(
            f"Unable to load analysis dataset: {e}"
        )
        return

    (
        selected_genres,
        selected_explicit,
        popularity_range
    ) = show_filters(df)

    filtered_df = apply_filters(
        df,
        selected_genres,
        selected_explicit,
        popularity_range
    )

    if filtered_df.empty:
        st.warning(
            "No songs match the selected filters."
        )
        return

    st.caption(
        f"Currently analyzing "
        f"{len(filtered_df):,} of "
        f"{len(df):,} songs."
    )

    overview_tab, genre_tab, audio_tab = st.tabs(
        [
            "📊 Overview",
            "🎧 Genre Analysis",
            "🎚️ Audio Feature Analysis"
        ]
    )

    with overview_tab:
        show_overview(
            filtered_df
        )

    with genre_tab:
        show_genre_analysis(
            filtered_df
        )

    with audio_tab:
        show_audio_analysis(
            filtered_df
        )

    st.divider()

    st.caption(
        "Interactive analytics powered by "
        "Pandas, Plotly and Streamlit"
    )