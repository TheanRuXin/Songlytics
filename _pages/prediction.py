import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from services.prediction_service import predict, FEATURES, get_genres
from services.shap_service import explain
from services.history_service import save_prediction, save_simulation
from services.recommendation_service import recommend_feature_changes
from services.spotify_service import spotify_service

CSV_PATH = "C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_cleaned.csv"

@st.cache_data
def load_dataset():
    df = pd.read_csv(CSV_PATH)

    df["song"] = df["track_name"].astype(str)
    df["artist"] = df["artists"].astype(str)
    df["song_artist"] = df["song"] + " - " + df["artist"]

    return df

def clear_prediction_state():
    keys = [
        "prediction_done",
        "temp_features_df",
        "temp_song_name",
        "temp_artist_name",
        "temp_input_source",
        "last_prediction_result",
        "last_features_df",
        "last_explanation",
        "sim_features",
        "song_name",
        "song_name_for_sim",
        "show_simulation_mode"
    ]

    for key in keys:
        st.session_state.pop(key, None)

def get_logged_in_user_id():
    return st.session_state.get("user_id")

def display_prediction_results(
    result,
    explanation,
    features_df
):
    label = result["label"]
    score = result["score"]
    mae = result.get("mae", 0)

    if label == "High Popularity":
        color = "#48dbfb"
        emoji = "🚀"
        status = "This song has high predicted popularity."

    elif label == "Medium Popularity":
        color = "#feca57"
        emoji = "📈"
        status = "This song has moderate predicted popularity."

    else:
        color = "#ff6b6b"
        emoji = "⚠️"
        status = "This song has low predicted popularity."

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(
                135deg,
                {color},
                {color}dd
            );
            border-radius: 20px;
            padding: 25px;
            margin: 20px 0;
        ">
            <div style="
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 20px;
            ">
                <div>
                    <div style="
                        font-size: 1rem;
                        opacity: 0.9;
                    ">
                        AI Prediction Result
                    </div>

                    <div style="
                        font-size: 2.5rem;
                        font-weight: bold;
                    ">
                        {emoji} {label}
                    </div>

                    <div style="
                        font-size: 0.9rem;
                        opacity: 0.9;
                    ">
                        {status}
                    </div>
                </div>

                <div style="text-align: center;">
                    <div style="
                        font-size: 0.9rem;
                        opacity: 0.9;
                    ">
                        Predicted Score
                    </div>

                    <div style="
                        font-size: 2rem;
                        font-weight: bold;
                    ">
                        {score:.1f}
                    </div>

                    <div style="
                        font-size: 0.8rem;
                        opacity: 0.8;
                    ">
                        out of 100
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Predicted Popularity Score",
            f"{score:.1f}/100"
        )

    with col2:
        st.metric(
            "Model MAE",
            f"{mae:.2f}"
        )

    st.caption(
        "The prediction is an estimated popularity score generated "
        "by the Random Forest regression model."
    )

    if explanation:
        st.subheader("📊 Feature Impact Analysis")

        st.caption(
            "Positive SHAP values push the model prediction higher, "
            "while negative values push it lower."
        )

        df_exp = pd.DataFrame(
            explanation
        )

        if (
            "feature" in df_exp.columns
            and "impact" in df_exp.columns
        ):
            df_exp = df_exp.sort_values(
                "impact",
                ascending=True
            )

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=df_exp["impact"],
                        y=df_exp["feature"],
                        orientation="h",
                        marker_color=[
                            "#48dbfb"
                            if value > 0
                            else "#ff6b6b"
                            for value in df_exp["impact"]
                        ],
                        text=df_exp["impact"].round(3),
                        textposition="outside",
                        hovertemplate=(
                            "Feature: %{y}"
                            "<br>Impact: %{x:.3f}"
                            "<extra></extra>"
                        )
                    )
                ]
            )

            fig.update_layout(
                title="SHAP Feature Impact",
                xaxis_title=(
                    "Impact on Predicted Popularity"
                ),
                yaxis_title="Feature",
                height=450,
                showlegend=False
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    if label in [
        "Low Popularity",
        "Medium Popularity"
    ]:
        st.subheader(
            "🎯 Model-Based Suggestions"
        )

        st.caption(
            "Suggestions are based on model predictions "
            "and do not imply real-world causation."
        )

        try:
            suggestions = (
                recommend_feature_changes(
                    features_df,
                    explanation
                )
            )

            if suggestions:
                for i, suggestion in enumerate(
                    suggestions,
                    start=1
                ):
                    col1, col2 = st.columns(
                        [1, 10]
                    )

                    with col1:
                        st.markdown(
                            f"### {i}"
                        )

                    with col2:
                        st.info(
                            f"💡 **{suggestion['message']}**"
                        )

                        if suggestion.get(
                            "action"
                        ):
                            st.code(
                                suggestion["action"],
                                language=None
                            )

                    st.divider()

            else:
                st.info(
                    "No small audio feature adjustment "
                    "produced a meaningful improvement "
                    "in the model prediction."
                )

        except Exception as e:
            print(
                "Recommendation error:",
                e
            )

            st.info(
                "Suggestions are currently unavailable."
            )

    else:
        st.success(
            "🎉 The model already predicts a relatively "
            "high popularity score for this song."
        )

def show_simulation_ui():
    st.header(
        "🎛️ What-If Simulation"
    )

    song_name = st.session_state.get(
        "song_name_for_sim",
        "Unknown Song"
    )

    st.write(
        f"Simulating: **{song_name}**"
    )

    base = st.session_state.get(
        "sim_features",
        {}
    )

    if not base:
        st.warning(
            "No prediction data found."
        )

        if st.button(
            "⬅ Back to Prediction",
            use_container_width=True
        ):
            st.session_state[
                "show_simulation_mode"
            ] = False

            st.rerun()

        return

    genres = get_genres()

    current_genre = base.get(
        "track_genre",
        genres[0]
    )

    if current_genre in genres:
        genre_index = genres.index(
            current_genre
        )
    else:
        genre_index = 0

    st.subheader(
        "🎚️ Adjust Audio Features"
    )

    st.caption(
        "Modify the values to see how the model's "
        "predicted popularity changes."
    )

    col1, col2 = st.columns(2)

    input_features = {}

    with col1:
        input_features[
            "duration_ms"
        ] = st.slider(
            "📏 Duration (ms)",
            50000,
            600000,
            int(
                base.get(
                    "duration_ms",
                    200000
                )
            )
        )

        explicit_default = int(
            bool(
                base.get(
                    "explicit",
                    0
                )
            )
        )

        input_features[
            "explicit"
        ] = st.selectbox(
            "🔞 Explicit",
            [0, 1],
            index=explicit_default,
            format_func=lambda value: (
                "Yes"
                if value == 1
                else "No"
            )
        )

        input_features[
            "danceability"
        ] = st.slider(
            "💃 Danceability",
            0.0,
            1.0,
            float(
                base.get(
                    "danceability",
                    0.5
                )
            )
        )

        input_features[
            "energy"
        ] = st.slider(
            "⚡ Energy",
            0.0,
            1.0,
            float(
                base.get(
                    "energy",
                    0.5
                )
            )
        )

        input_features[
            "key"
        ] = st.selectbox(
            "🎼 Key",
            list(range(12)),
            index=int(
                base.get(
                    "key",
                    0
                )
            )
        )

        input_features[
            "loudness"
        ] = st.slider(
            "🔊 Loudness (dB)",
            -60.0,
            0.0,
            float(
                base.get(
                    "loudness",
                    -10.0
                )
            )
        )

        input_features[
            "mode"
        ] = st.selectbox(
            "🎵 Mode",
            [0, 1],
            index=int(
                base.get(
                    "mode",
                    1
                )
            ),
            format_func=lambda value: (
                "Major"
                if value == 1
                else "Minor"
            )
        )

    with col2:
        input_features[
            "speechiness"
        ] = st.slider(
            "🗣️ Speechiness",
            0.0,
            1.0,
            float(
                base.get(
                    "speechiness",
                    0.05
                )
            )
        )

        input_features[
            "acousticness"
        ] = st.slider(
            "🎸 Acousticness",
            0.0,
            1.0,
            float(
                base.get(
                    "acousticness",
                    0.5
                )
            )
        )

        input_features[
            "instrumentalness"
        ] = st.slider(
            "🎹 Instrumentalness",
            0.0,
            1.0,
            float(
                base.get(
                    "instrumentalness",
                    0.0
                )
            )
        )

        input_features[
            "liveness"
        ] = st.slider(
            "🎤 Liveness",
            0.0,
            1.0,
            float(
                base.get(
                    "liveness",
                    0.1
                )
            )
        )

        input_features[
            "valence"
        ] = st.slider(
            "😊 Valence",
            0.0,
            1.0,
            float(
                base.get(
                    "valence",
                    0.5
                )
            )
        )

        input_features[
            "tempo"
        ] = st.slider(
            "⏱️ Tempo (BPM)",
            40,
            220,
            int(
                base.get(
                    "tempo",
                    120
                )
            )
        )

        time_signature_options = [
            0,
            1,
            2,
            3,
            4,
            5
        ]

        current_time_signature = int(
            base.get(
                "time_signature",
                4
            )
        )

        if (
            current_time_signature
            in time_signature_options
        ):
            time_index = (
                time_signature_options.index(
                    current_time_signature
                )
            )
        else:
            time_index = 4

        input_features[
            "time_signature"
        ] = st.selectbox(
            "🥁 Time Signature",
            time_signature_options,
            index=time_index
        )

        input_features[
            "track_genre"
        ] = st.selectbox(
            "🎧 Track Genre",
            genres,
            index=genre_index
        )

    df_input = pd.DataFrame(
        [input_features]
    )[FEATURES]

    st.divider()

    if st.button(
        "🚀 Run Simulation",
        type="primary",
        use_container_width=True
    ):
        with st.spinner(
            "Running simulation..."
        ):
            result = predict(
                df_input
            )

            try:
                explanation = explain(
                    df_input
                )

            except Exception as e:
                print(
                    "Simulation SHAP error:",
                    e
                )

                explanation = []

        original_score = float(
            base.get(
                "score",
                0
            )
        )

        new_score = result["score"]

        delta = (
            new_score
            - original_score
        )

        changes = {}

        for feature in FEATURES:
            old_value = base.get(
                feature
            )

            new_value = input_features.get(
                feature
            )

            if old_value != new_value:
                changes[feature] = {
                    "old": old_value,
                    "new": new_value
                }

        user_id = get_logged_in_user_id()

        if user_id:
            simulation_result = (
                save_simulation(
                    user_id,
                    f"{song_name} (simulated)",
                    original_score,
                    new_score,
                    changes
                )
            )

            if not simulation_result.get(
                "success",
                False
            ):
                print(
                    "Simulation history not saved:",
                    simulation_result
                )

        st.subheader(
            "📊 Simulation Result"
        )

        label = result["label"]

        if label == "High Popularity":
            st.success(
                f"🟢 **{label}** — "
                f"{new_score:.1f}/100"
            )

        elif label == "Medium Popularity":
            st.warning(
                f"🟡 **{label}** — "
                f"{new_score:.1f}/100"
            )

        else:
            st.error(
                f"🔴 **{label}** — "
                f"{new_score:.1f}/100"
            )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Original Score",
                f"{original_score:.1f}"
            )

        with col2:
            st.metric(
                "New Score",
                f"{new_score:.1f}",
                delta=f"{delta:+.1f}"
            )

        st.caption(
            "The score difference represents a change "
            "in the model prediction, not a guaranteed "
            "change in real-world popularity."
        )

        if explanation:
            st.subheader(
                "📊 Feature Impact"
            )

            df_exp = pd.DataFrame(
                explanation
            )

            if (
                "feature"
                in df_exp.columns
                and "impact"
                in df_exp.columns
            ):
                df_exp = (
                    df_exp
                    .sort_values(
                        "impact",
                        ascending=False
                    )
                )

                st.bar_chart(
                    df_exp.set_index(
                        "feature"
                    )["impact"]
                )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🔄 Reset Simulation",
            use_container_width=True
        ):
            st.rerun()

    with col2:
        if st.button(
            "⬅ Back to Prediction",
            use_container_width=True
        ):
            st.session_state[
                "show_simulation_mode"
            ] = False

            st.session_state[
                "return_from_simulation"
            ] = True

            st.rerun()

def show_prediction():
    if st.session_state.get(
        "show_simulation_mode",
        False
    ):
        show_simulation_ui()
        return

    st.markdown(
        """
        <style>
        .prediction-title {
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
        """
        <p class="prediction-title">
            🎵 Song Popularity Predictor
        </p>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "AI-powered music popularity prediction "
        "using audio characteristics"
    )

    user_id = get_logged_in_user_id()

    if not user_id:
        st.info(
            "ℹ️ You can make predictions without logging in, "
            "but prediction and simulation history will only "
            "be saved when you are logged in."
        )

    if st.session_state.get(
        "return_from_simulation",
        False
    ):
        st.session_state[
            "return_from_simulation"
        ] = False

        st.session_state[
            "prediction_done"
        ] = True

    if (
        st.session_state.get(
            "prediction_done",
            False
        )
        and "last_prediction_result"
        in st.session_state
    ):
        result = st.session_state[
            "last_prediction_result"
        ]

        explanation = (
            st.session_state.get(
                "last_explanation",
                []
            )
        )

        features_df = st.session_state[
            "last_features_df"
        ]

        display_name = (
            st.session_state.get(
                "song_name",
                "Unknown Song"
            )
        )

        display_prediction_results(
            result,
            explanation,
            features_df
        )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🎛 Try What-if Simulation",
                key="sim_btn_results",
                use_container_width=True
            ):
                sim_data = (
                    features_df
                    .iloc[0]
                    .to_dict()
                )

                sim_data["score"] = (
                    result["score"]
                )

                st.session_state[
                    "sim_features"
                ] = sim_data

                st.session_state[
                    "song_name_for_sim"
                ] = display_name

                st.session_state[
                    "show_simulation_mode"
                ] = True

                st.rerun()

        with col2:
            if st.button(
                "🔍 Predict Another Song",
                key="new_prediction_btn_results",
                use_container_width=True
            ):
                clear_prediction_state()

                st.rerun()

        st.markdown("---")

        st.caption(
            "💡 Powered by Random Forest Regression "
            "| SHAP Explainability | Spotify API"
        )

        return

    input_mode = st.radio(
        "Select input method:",
        [
            "🔍 Search Spotify",
            "📁 Choose from Dataset",
            "✏️ Manual Input"
        ],
        horizontal=True
    )

    genres = get_genres()

    features_df = None
    song_name = None
    artist_name = None
    input_source = None

    if input_mode == "🔍 Search Spotify":
        st.markdown(
            "### 🔍 Search Spotify"
        )

        search_query = st.text_input(
            "Enter song name or artist:",
            placeholder=(
                "e.g. Blinding Lights, "
                "The Weeknd, Taylor Swift"
            )
        )

        if search_query:
            with st.spinner(
                "Searching Spotify..."
            ):
                results = (
                    spotify_service
                    .search_song(
                        search_query,
                        limit=10
                    )
                )

            if results:
                search_df = pd.DataFrame(
                    results
                )

                search_df["display"] = (
                    search_df["song"]
                    + " - "
                    + search_df["artist"]
                )

                selected_display = (
                    st.selectbox(
                        "Select a song:",
                        search_df[
                            "display"
                        ].tolist()
                    )
                )

                selected_row = (
                    search_df[
                        search_df["display"]
                        == selected_display
                    ]
                    .iloc[0]
                )

                track_id = (
                    selected_row[
                        "track_id"
                    ]
                )

                song_name = (
                    selected_row[
                        "song"
                    ]
                )

                artist_name = (
                    selected_row[
                        "artist"
                    ]
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.info(
                        f"🎤 **Artist:** "
                        f"{artist_name}"
                    )

                with col2:
                    spotify_popularity = (
                        selected_row.get(
                            "popularity"
                        )
                    )

                    if pd.notna(
                        spotify_popularity
                    ):
                        st.info(
                            "⭐ **Spotify Popularity:** "
                            f"{spotify_popularity}/100"
                        )

                    else:
                        st.info(
                            "⭐ Spotify popularity "
                            "score unavailable"
                        )

                st.caption(
                    "📀 **Album:** "
                    f"{selected_row.get('album_name', 'N/A')}"
                )

                spotify_genre = (
                    st.selectbox(
                        "🎧 Select Track Genre",
                        genres,
                        key="spotify_genre"
                    )
                )

                if st.button(
                    "🎵 Load Audio Features",
                    key="spotify_features",
                    type="primary"
                ):
                    with st.spinner(
                        "Checking SONGlytics dataset..."
                    ):
                        features_dict = (
                            spotify_service
                            .get_audio_features(
                                track_id
                            )
                        )

                    if features_dict:
                        features_dict[
                            "track_genre"
                        ] = spotify_genre

                        missing = [
                            feature
                            for feature
                            in FEATURES
                            if feature
                            not in features_dict
                        ]

                        if missing:
                            st.error(
                                "Missing features: "
                                + ", ".join(
                                    missing
                                )
                            )

                        else:
                            features_df = (
                                pd.DataFrame(
                                    [features_dict]
                                )[FEATURES]
                            )

                            st.session_state[
                                "temp_features_df"
                            ] = features_df

                            st.session_state[
                                "temp_song_name"
                            ] = song_name

                            st.session_state[
                                "temp_artist_name"
                            ] = artist_name

                            st.session_state[
                                "temp_input_source"
                            ] = "Spotify"

                            st.success(
                                "✅ Audio features loaded successfully."
                            )

                    else:
                        st.warning(
                            "This track was found on Spotify, "
                            "but its audio features are not "
                            "available in the SONGlytics dataset. "
                            "Please use Manual Input instead."
                        )

            else:
                st.warning(
                    "No Spotify results found."
                )

    elif input_mode == "📁 Choose from Dataset":
        st.markdown(
            "### 📁 Choose a Song from Dataset"
        )

        df = load_dataset()

        song_list = (
            df["song_artist"]
            .tolist()
        )

        col1, col2 = st.columns(
            [3, 1]
        )

        with col1:
            search_term = st.text_input(
                "🔍 Search song or artist:",
                placeholder=(
                    "e.g. Blinding Lights "
                    "or Taylor Swift"
                ),
                key="dataset_search"
            )

        with col2:
            st.write("")
            st.write("")

            browse_mode = st.toggle(
                "📋 Browse full list",
                key="browse_mode"
            )

        selected = None

        if browse_mode:
            selected = st.selectbox(
                "Choose a song:",
                song_list,
                key="dataset_browse"
            )

        elif search_term:
            search_lower = (
                search_term.lower()
            )

            filtered = [
                song
                for song
                in song_list
                if search_lower
                in song.lower()
            ]

            if filtered:
                selected = st.selectbox(
                    f"Found {len(filtered)} matches:",
                    filtered[:20],
                    key="dataset_result"
                )

                st.caption(
                    f"Showing "
                    f"{min(20, len(filtered))} "
                    f"of {len(filtered)} matches"
                )

            else:
                st.warning(
                    "No matching song found."
                )

        if selected:
            song_name, artist_name = (
                selected.split(
                    " - ",
                    1
                )
            )

            st.success(
                f"✅ Selected: "
                f"**{song_name}** "
                f"by **{artist_name}**"
            )

            if st.button(
                "🚀 Load Features",
                key="dataset_load",
                type="primary"
            ):
                row = df[
                    (
                        df["song"]
                        == song_name
                    )
                    &
                    (
                        df["artist"]
                        == artist_name
                    )
                ]

                if not row.empty:
                    features_df = (
                        row[FEATURES]
                        .iloc[[0]]
                        .copy()
                    )

                    st.session_state[
                        "temp_features_df"
                    ] = features_df

                    st.session_state[
                        "temp_song_name"
                    ] = song_name

                    st.session_state[
                        "temp_artist_name"
                    ] = artist_name

                    st.session_state[
                        "temp_input_source"
                    ] = "Dataset"

                    st.success(
                        "✅ Features loaded from dataset."
                    )

                else:
                    st.error(
                        "Unable to load this song."
                    )

    else:
        st.markdown(
            "### 🎚️ Enter Audio Features Manually"
        )

        st.caption(
            "Enter the song's audio characteristics below."
        )

        col1, col2 = st.columns(2)

        with col1:
            duration_ms = st.number_input(
                "📏 Duration (ms)",
                min_value=60000,
                max_value=600000,
                value=180000
            )

            danceability = st.slider(
                "💃 Danceability",
                0.0,
                1.0,
                0.6
            )

            energy = st.slider(
                "⚡ Energy",
                0.0,
                1.0,
                0.7
            )

            loudness = st.slider(
                "🔊 Loudness (dB)",
                -60.0,
                0.0,
                -6.0
            )

            speechiness = st.slider(
                "🗣️ Speechiness",
                0.0,
                1.0,
                0.05
            )

            key = st.selectbox(
                "🎼 Key",
                list(range(12))
            )

            mode = st.selectbox(
                "🎵 Mode",
                [0, 1],
                format_func=lambda value: (
                    "Major"
                    if value == 1
                    else "Minor"
                )
            )

        with col2:
            acousticness = st.slider(
                "🎸 Acousticness",
                0.0,
                1.0,
                0.3
            )

            instrumentalness = st.slider(
                "🎹 Instrumentalness",
                0.0,
                1.0,
                0.0
            )

            liveness = st.slider(
                "🎤 Liveness",
                0.0,
                1.0,
                0.1
            )

            valence = st.slider(
                "😊 Valence",
                0.0,
                1.0,
                0.6
            )

            tempo = st.number_input(
                "⏱️ Tempo (BPM)",
                min_value=40,
                max_value=220,
                value=120
            )

            explicit = st.selectbox(
                "🔞 Explicit",
                ["No", "Yes"]
            )

            time_signature = (
                st.selectbox(
                    "🥁 Time Signature",
                    [0, 1, 2, 3, 4, 5],
                    index=4
                )
            )

            track_genre = st.selectbox(
                "🎧 Track Genre",
                genres
            )

        song_name = st.text_input(
            "🎵 Song Name (optional)",
            placeholder="Custom Song"
        )

        artist_name = st.text_input(
            "🎤 Artist Name (optional)",
            placeholder="User Input"
        )

        if not song_name:
            song_name = "Custom Song"

        if not artist_name:
            artist_name = "User Input"

        if st.button(
            "✅ Set Features",
            key="manual_set",
            type="primary"
        ):
            features_dict = {
                "duration_ms":
                    duration_ms,

                "explicit":
                    1
                    if explicit == "Yes"
                    else 0,

                "danceability":
                    danceability,

                "energy":
                    energy,

                "key":
                    key,

                "loudness":
                    loudness,

                "mode":
                    mode,

                "speechiness":
                    speechiness,

                "acousticness":
                    acousticness,

                "instrumentalness":
                    instrumentalness,

                "liveness":
                    liveness,

                "valence":
                    valence,

                "tempo":
                    tempo,

                "time_signature":
                    time_signature,

                "track_genre":
                    track_genre
            }

            features_df = (
                pd.DataFrame(
                    [features_dict]
                )[FEATURES]
            )

            st.session_state[
                "temp_features_df"
            ] = features_df

            st.session_state[
                "temp_song_name"
            ] = song_name

            st.session_state[
                "temp_artist_name"
            ] = artist_name

            st.session_state[
                "temp_input_source"
            ] = "Manual"

            st.success(
                "✅ Manual features ready."
            )

    features_df = (
        st.session_state.get(
            "temp_features_df"
        )
    )

    song_name = (
        st.session_state.get(
            "temp_song_name"
        )
    )

    artist_name = (
        st.session_state.get(
            "temp_artist_name"
        )
    )

    input_source = (
        st.session_state.get(
            "temp_input_source"
        )
    )

    if features_df is not None:
        st.divider()

        col1, col2, col3 = (
            st.columns(
                [2, 1, 1]
            )
        )

        with col1:
            st.info(
                f"🎵 **Ready to predict:** "
                f"{song_name} - "
                f"{artist_name}"
            )

        with col2:
            predict_button = (
                st.button(
                    "🚀 Run Prediction",
                    key="run_prediction",
                    type="primary",
                    use_container_width=True
                )
            )

        with col3:
            if st.button(
                "🔄 Reset",
                key="reset_prediction",
                use_container_width=True
            ):
                clear_prediction_state()

                st.rerun()

        if predict_button:
            try:
                with st.spinner(
                    "🔮 Analyzing song features..."
                ):
                    result = predict(
                        features_df
                    )

                    explanation = explain(
                        features_df
                    )

                display_name = (
                    f"{song_name} - "
                    f"{artist_name}"
                )

                user_id = (
                    get_logged_in_user_id()
                )

                if user_id:
                    save_result = (
                        save_prediction(
                            user_id,
                            display_name,
                            result["label"],
                            result["score"],
                            input_source=input_source,
                            features=(
                                features_df
                                .iloc[0]
                                .to_dict()
                            )
                        )
                    )

                    if not save_result.get(
                        "success",
                        False
                    ):
                        print(
                            "Prediction history "
                            "was not saved:",
                            save_result
                        )

                st.session_state[
                    "last_prediction_result"
                ] = result

                st.session_state[
                    "last_features_df"
                ] = features_df

                st.session_state[
                    "last_explanation"
                ] = explanation

                st.session_state[
                    "prediction_done"
                ] = True

                st.session_state[
                    "song_name"
                ] = display_name

                sim_data = (
                    features_df
                    .iloc[0]
                    .to_dict()
                )

                sim_data[
                    "score"
                ] = result["score"]

                st.session_state[
                    "sim_features"
                ] = sim_data

                st.rerun()

            except Exception as e:
                st.error(
                    "Prediction failed. "
                    f"Please check the input data. "
                    f"Error: {e}"
                )

    else:
        st.info(
            "👆 Please select a song "
            "or enter features above "
            "to start prediction."
        )

    st.markdown("---")

    st.caption(
        "💡 Powered by Random Forest Regression "
        "| SHAP Explainability"
    )