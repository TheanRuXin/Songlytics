import streamlit as st
import pandas as pd

from services.history_service import (
    get_prediction_history,
    get_simulation_history,
    delete_prediction,
    delete_simulation,
    clear_prediction_history,
    clear_simulation_history
)

def get_user_id():
    return st.session_state.get("user_id")

def format_datetime(value):
    if value is None:
        return ""

    try:
        return value.strftime("%d %b %Y %H:%M")
    except Exception:
        return str(value)

def show_prediction_history(user_id):
    st.subheader("🎵 Prediction History")

    predictions = get_prediction_history(
        user_id,
        limit=100
    )

    if not predictions:
        st.info(
            "No prediction history yet."
        )
        return

    df = pd.DataFrame(predictions)

    display_df = pd.DataFrame({
        "Song": df["display_name"],
        "Label": df["label"],
        "Predicted Score": df[
            "predicted_score"
        ].round(2),
        "Source": df[
            "input_source"
        ].fillna("Unknown"),
        "Date": df[
            "created_at"
        ].apply(
            format_datetime
        )
    })

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.markdown(
        "### 🔎 Prediction Details"
    )

    options = {
        f"{item['display_name']} | "
        f"{item['predicted_score']:.1f}/100 | "
        f"{format_datetime(item['created_at'])}":
        item
        for item in predictions
    }

    selected_key = st.selectbox(
        "Select prediction:",
        list(options.keys()),
        key="prediction_history_select"
    )

    selected = options[
        selected_key
    ]

    col1, col2, col3 = st.columns(
        [2, 1, 1]
    )

    with col1:
        st.metric(
            "Predicted Popularity",
            f"{selected['predicted_score']:.1f}/100"
        )

    with col2:
        st.metric(
            "Label",
            selected["label"]
        )

    with col3:
        st.metric(
            "Source",
            selected.get(
                "input_source"
            )
            or "Unknown"
        )

    features = selected.get(
        "features"
    )

    if features:
        st.markdown(
            "#### 🎚️ Input Features"
        )

        feature_df = pd.DataFrame(
            {
                "Feature":
                    list(
                        features.keys()
                    ),

                "Value":
                    list(
                        features.values()
                    )
            }
        )

        st.dataframe(
            feature_df,
            use_container_width=True,
            hide_index=True
        )

    st.caption(
        "Created: "
        + format_datetime(
            selected[
                "created_at"
            ]
        )
    )

    if st.button(
        "🗑️ Delete Selected Prediction",
        key="delete_prediction_button"
    ):
        success = delete_prediction(
            user_id,
            selected["id"]
        )

        if success:
            st.success(
                "Prediction deleted."
            )
            st.rerun()

        else:
            st.error(
                "Unable to delete prediction."
            )

def show_simulation_history(user_id):
    st.subheader(
        "🎛️ Simulation History"
    )

    simulations = get_simulation_history(
        user_id,
        limit=100
    )

    if not simulations:
        st.info(
            "No simulation history yet."
        )
        return

    df = pd.DataFrame(
        simulations
    )

    display_df = pd.DataFrame({
        "Simulation":
            df["display_name"],

        "Original":
            df["original_score"]
            .round(2),

        "New":
            df["new_score"]
            .round(2),

        "Change":
            df["score_change"]
            .round(2),

        "Date":
            df["created_at"]
            .apply(
                format_datetime
            )
    })

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.markdown(
        "### 🔎 Simulation Details"
    )

    options = {
        f"{item['display_name']} | "
        f"{item['original_score']:.1f} → "
        f"{item['new_score']:.1f} | "
        f"{format_datetime(item['created_at'])}":
        item
        for item in simulations
    }

    selected_key = st.selectbox(
        "Select simulation:",
        list(options.keys()),
        key="simulation_history_select"
    )

    selected = options[
        selected_key
    ]

    col1, col2, col3 = st.columns(
        3
    )

    with col1:
        st.metric(
            "Original Score",
            f"{selected['original_score']:.1f}"
        )

    with col2:
        st.metric(
            "New Score",
            f"{selected['new_score']:.1f}"
        )

    with col3:
        st.metric(
            "Score Change",
            f"{selected['score_change']:+.1f}"
        )

    changes = selected.get(
        "changes"
    )

    if changes:
        st.markdown(
            "#### 🎚️ Changed Features"
        )

        change_rows = []

        for feature, values in (
            changes.items()
        ):
            if isinstance(
                values,
                dict
            ):
                old_value = (
                    values.get(
                        "old"
                    )
                )

                new_value = (
                    values.get(
                        "new"
                    )
                )
            else:
                old_value = None
                new_value = values

            change_rows.append({
                "Feature":
                    feature,

                "Original":
                    old_value,

                "New":
                    new_value
            })

        change_df = pd.DataFrame(
            change_rows
        )

        st.dataframe(
            change_df,
            use_container_width=True,
            hide_index=True
        )

    st.caption(
        "Created: "
        + format_datetime(
            selected[
                "created_at"
            ]
        )
    )

    if st.button(
        "🗑️ Delete Selected Simulation",
        key="delete_simulation_button"
    ):
        success = delete_simulation(
            user_id,
            selected["id"]
        )

        if success:
            st.success(
                "Simulation deleted."
            )
            st.rerun()

        else:
            st.error(
                "Unable to delete simulation."
            )

def show_history():
    st.markdown(
        """
        <style>
        .history-title {
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
        <p class="history-title">
            📚 Prediction History
        </p>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Review your previous SONGlytics "
        "predictions and What-If simulations."
    )

    user_id = get_user_id()

    if not user_id:
        st.warning(
            "🔐 Please log in to view your history."
        )

        st.info(
            "Predictions made while logged out "
            "are not saved."
        )

        return

    tab1, tab2 = st.tabs(
        [
            "🎵 Predictions",
            "🎛️ Simulations"
        ]
    )

    with tab1:
        show_prediction_history(
            user_id
        )

        st.divider()

        with st.expander(
            "⚠️ Clear Prediction History"
        ):
            st.warning(
                "This action permanently deletes "
                "all of your saved predictions."
            )

            confirm = st.checkbox(
                "I understand that this cannot be undone.",
                key="confirm_clear_predictions"
            )

            if st.button(
                "Delete All Prediction History",
                disabled=not confirm,
                key="clear_predictions_button"
            ):
                success = (
                    clear_prediction_history(
                        user_id
                    )
                )

                if success:
                    st.success(
                        "Prediction history cleared."
                    )
                    st.rerun()

                else:
                    st.error(
                        "Unable to clear prediction history."
                    )

    with tab2:
        show_simulation_history(
            user_id
        )

        st.divider()

        with st.expander(
            "⚠️ Clear Simulation History"
        ):
            st.warning(
                "This action permanently deletes "
                "all of your saved simulations."
            )

            confirm = st.checkbox(
                "I understand that this cannot be undone.",
                key="confirm_clear_simulations"
            )

            if st.button(
                "Delete All Simulation History",
                disabled=not confirm,
                key="clear_simulations_button"
            ):
                success = (
                    clear_simulation_history(
                        user_id
                    )
                )

                if success:
                    st.success(
                        "Simulation history cleared."
                    )
                    st.rerun()

                else:
                    st.error(
                        "Unable to clear simulation history."
                    )

    st.markdown("---")

    st.caption(
        "🔒 History records are only retrieved "
        "for the currently authenticated user."
    )