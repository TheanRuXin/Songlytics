import json
from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

import pandas as pd
import streamlit as st

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from services.history_service import (
    get_prediction_history,
    get_simulation_history,
    delete_prediction,
    delete_simulation
)

def format_datetime(value):
    if not value:
        return "N/A"

    if isinstance(
        value,
        datetime
    ):
        return value.strftime(
            "%d %b %Y %H:%M"
        )

    try:
        parsed = datetime.fromisoformat(
            str(value)
        )

        return parsed.strftime(
            "%d %b %Y %H:%M"
        )

    except Exception:
        return str(value)


def format_short_date(value):
    if not value:
        return "N/A"

    if isinstance(
        value,
        datetime
    ):
        return value.strftime(
            "%d %b %Y"
        )

    try:
        parsed = datetime.fromisoformat(
            str(value)
        )

        return parsed.strftime(
            "%d %b %Y"
        )

    except Exception:
        return str(value)


def parse_json_field(value):
    if value is None:
        return {}

    if isinstance(
        value,
        dict
    ):
        return value

    if isinstance(
        value,
        str
    ):
        try:
            return json.loads(
                value
            )

        except Exception:
            return {}

    return {}


def normalise_history_result(
    result
):
    if result is None:
        return []

    if isinstance(
        result,
        list
    ):
        return result

    if isinstance(
        result,
        tuple
    ):
        return list(
            result
        )

    if isinstance(
        result,
        dict
    ):
        for key in [
            "data",
            "records",
            "history",
            "results"
        ]:
            value = result.get(
                key
            )

            if isinstance(
                value,
                list
            ):
                return value

    return []


def value_to_text(value):
    if value is None:
        return "N/A"

    if isinstance(
        value,
        float
    ):
        return f"{value:.4f}"

    return str(value)


def create_prediction_pdf(
    record
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
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=14
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=10,
        spaceAfter=8
    )

    body_style = (
        styles["BodyText"]
    )

    elements = []

    elements.append(
        Paragraph(
            "Songlytics Prediction Report",
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
            "Prediction Information",
            heading_style
        )
    )

    score = float(
        record.get(
            "predicted_score",
            0
        )
        or 0
    )

    info_data = [
        [
            "Song",
            str(
                record.get(
                    "display_name",
                    "Unknown"
                )
            )
        ],
        [
            "Prediction",
            str(
                record.get(
                    "label",
                    "N/A"
                )
            )
        ],
        [
            "Predicted Score",
            f"{score:.2f} / 100"
        ],
        [
            "Input Method",
            str(
                record.get(
                    "input_source",
                    "N/A"
                )
            )
        ],
        [
            "Prediction Date",
            format_datetime(
                record.get(
                    "created_at"
                )
            )
        ]
    ]

    info_table = Table(
        info_data,
        colWidths=[
            5 * cm,
            11 * cm
        ]
    )

    info_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
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
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
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
        info_table
    )

    features = parse_json_field(
        record.get(
            "features"
        )
    )

    if features:
        elements.append(
            Paragraph(
                "Audio Features",
                heading_style
            )
        )

        feature_data = [
            [
                "Feature",
                "Value"
            ]
        ]

        for feature, value in features.items():
            feature_data.append([
                str(feature),
                value_to_text(
                    value
                )
            ])

        feature_table = Table(
            feature_data,
            colWidths=[
                8 * cm,
                8 * cm
            ]
        )

        feature_table.setStyle(
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
            feature_table
        )

    elements.append(
        Spacer(
            1,
            12
        )
    )

    elements.append(
        Paragraph(
            (
                "Note: The predicted popularity score "
                "is generated by the Songlytics machine "
                "learning model and should be interpreted "
                "as a model estimate."
            ),
            body_style
        )
    )

    document.build(
        elements
    )

    buffer.seek(0)

    return buffer.getvalue()


def create_simulation_pdf(
    record
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
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=14
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=10,
        spaceAfter=8
    )

    body_style = (
        styles["BodyText"]
    )

    elements = []

    elements.append(
        Paragraph(
            "Songlytics Simulation Report",
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

    original_score = float(
        record.get(
            "original_score",
            0
        )
        or 0
    )

    new_score = float(
        record.get(
            "new_score",
            0
        )
        or 0
    )

    difference = (
        new_score
        - original_score
    )

    elements.append(
        Paragraph(
            "Simulation Information",
            heading_style
        )
    )

    info_data = [
        [
            "Song",
            str(
                record.get(
                    "display_name",
                    "Unknown"
                )
            )
        ],
        [
            "Original Score",
            f"{original_score:.2f}"
        ],
        [
            "New Score",
            f"{new_score:.2f}"
        ],
        [
            "Score Difference",
            f"{difference:+.2f}"
        ],
        [
            "Simulation Date",
            format_datetime(
                record.get(
                    "created_at"
                )
            )
        ]
    ]

    info_table = Table(
        info_data,
        colWidths=[
            5 * cm,
            11 * cm
        ]
    )

    info_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
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
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
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
        info_table
    )

    changes = parse_json_field(
        record.get(
            "changes"
        )
    )

    if changes:
        elements.append(
            Paragraph(
                "Changed Audio Features",
                heading_style
            )
        )

        change_data = [
            [
                "Feature",
                "Original",
                "New"
            ]
        ]

        for feature, values in changes.items():

            if isinstance(
                values,
                dict
            ):
                old_value = (
                    values.get(
                        "old",
                        "N/A"
                    )
                )

                new_value = (
                    values.get(
                        "new",
                        "N/A"
                    )
                )

            else:
                old_value = "N/A"
                new_value = values

            change_data.append([
                str(feature),
                value_to_text(
                    old_value
                ),
                value_to_text(
                    new_value
                )
            ])

        change_table = Table(
            change_data,
            colWidths=[
                6 * cm,
                5 * cm,
                5 * cm
            ]
        )

        change_table.setStyle(
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
            change_table
        )

    else:
        elements.append(
            Paragraph(
                "No audio features were changed.",
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
            (
                "Note: The score difference represents "
                "a change in the model prediction and "
                "does not guarantee a change in "
                "real-world song popularity."
            ),
            body_style
        )
    )

    document.build(
        elements
    )

    buffer.seek(0)

    return buffer.getvalue()


def show_prediction_detail(
    record,
    user_id
):
    st.markdown(
        "### Prediction Details"
    )

    display_name = record.get(
        "display_name",
        "Unknown Song"
    )

    score = float(
        record.get(
            "predicted_score",
            0
        )
        or 0
    )

    label = record.get(
        "label",
        "N/A"
    )

    input_source = record.get(
        "input_source",
        "N/A"
    )

    col1, col2 = st.columns(
        2
    )

    with col1:
        st.markdown(
            "**Song**"
        )

        st.write(
            display_name
        )

        st.markdown(
            "**Prediction**"
        )

        st.write(
            label
        )

    with col2:
        st.markdown(
            "**Predicted Score**"
        )

        st.write(
            f"{score:.1f} / 100"
        )

        st.markdown(
            "**Input Method**"
        )

        st.write(
            input_source
        )

    st.markdown(
        "**Prediction Date**"
    )

    st.write(
        format_datetime(
            record.get(
                "created_at"
            )
        )
    )

    features = parse_json_field(
        record.get(
            "features"
        )
    )

    if features:
        st.markdown(
            "#### 🎚️ Audio Features"
        )

        feature_df = pd.DataFrame(
            [
                {
                    "Feature": feature,
                    "Value": value_to_text(
                        value
                    )
                }
                for feature, value
                in features.items()
            ]
        )

        st.dataframe(
            feature_df,
            hide_index=True,
            use_container_width=True
        )

    col1, col2 = st.columns(
        2
    )

    with col1:
        pdf_data = (
            create_prediction_pdf(
                record
            )
        )

        st.download_button(
            "📄 Generate PDF Report",
            data=pdf_data,
            file_name=(
                "Songlytics_"
                f"Prediction_{record['id']}.pdf"
            ),
            mime="application/pdf",
            key=(
                "prediction_pdf_"
                f"{record['id']}"
            ),
            use_container_width=True
        )

    with col2:
        if st.button(
            "🗑 Delete Record",
            key=(
                "delete_prediction_"
                f"{record['id']}"
            ),
            use_container_width=True
        ):
            try:
                deleted = delete_prediction(
                    user_id,
                    record["id"]
                )

                if deleted:
                    print("Deleted prediction record:", record["id"])
                    st.session_state[
                        "selected_prediction_history"
                    ] = None

                    st.success(
                        "Prediction record deleted."
                    )

                    st.rerun()

                else:
                    st.error(
                        "Unable to delete prediction record."
                    )

            except Exception as e:
                st.error(
                    f"Unable to delete record: {e}"
                )


def show_simulation_detail(
    record,
    user_id
):
    st.markdown(
        "### Simulation Details"
    )

    display_name = record.get(
        "display_name",
        "Unknown Song"
    )

    original_score = float(
        record.get(
            "original_score",
            0
        )
        or 0
    )

    new_score = float(
        record.get(
            "new_score",
            0
        )
        or 0
    )

    difference = (
        new_score
        - original_score
    )

    st.markdown(
        "**Song**"
    )

    st.write(
        display_name
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:
        st.metric(
            "Original Score",
            f"{original_score:.1f}"
        )

    with col2:
        st.metric(
            "New Score",
            f"{new_score:.1f}"
        )

    with col3:
        st.metric(
            "Difference",
            f"{difference:+.1f}"
        )

    st.markdown(
        "**Simulation Date**"
    )

    st.write(
        format_datetime(
            record.get(
                "created_at"
            )
        )
    )

    changes = parse_json_field(
        record.get(
            "changes"
        )
    )

    st.markdown(
        "#### 🎚️ Changed Audio Features"
    )

    if changes:
        change_rows = []

        for feature, values in changes.items():

            if isinstance(
                values,
                dict
            ):
                old_value = (
                    values.get(
                        "old",
                        "N/A"
                    )
                )

                new_value = (
                    values.get(
                        "new",
                        "N/A"
                    )
                )

            else:
                old_value = "N/A"
                new_value = values

            change_rows.append({
                "Feature": feature,
                "Original": value_to_text(
                    old_value
                ),
                "New": value_to_text(
                    new_value
                )
            })

        changes_df = pd.DataFrame(
            change_rows
        )

        st.dataframe(
            changes_df,
            hide_index=True,
            use_container_width=True
        )

    else:
        st.info(
            "No audio features were changed."
        )

    st.caption(
        "The score difference represents a change "
        "in the model prediction, not a guaranteed "
        "change in real-world popularity."
    )

    col1, col2 = st.columns(
        2
    )

    with col1:
        pdf_data = (
            create_simulation_pdf(
                record
            )
        )

        st.download_button(
            "📄 Generate PDF Report",
            data=pdf_data,
            file_name=(
                "Songlytics_"
                f"Simulation_{record['id']}.pdf"
            ),
            mime="application/pdf",
            key=(
                "simulation_pdf_"
                f"{record['id']}"
            ),
            use_container_width=True
        )

    with col2:
        if st.button(
            "🗑 Delete Record",
            key=(
                "delete_simulation_"
                f"{record['id']}"
            ),
            use_container_width=True
        ):
            try:
                deleted = delete_simulation(
                    user_id,
                    record["id"]
                )

                if deleted:
                    print("Deleted simulation record:", record["id"])
                    st.session_state[
                        "selected_simulation_history"
                    ] = None

                    st.success(
                        "Simulation record deleted."
                    )

                    st.rerun()

                else:
                    st.error(
                        "Unable to delete simulation record."
                    )

            except Exception as e:
                st.error(
                    f"Unable to delete record: {e}"
                )


def show_prediction_history(
    user_id
):
    try:
        result = (
            get_prediction_history(
                user_id,
                limit=50
            )
        )

        records = (
            normalise_history_result(
                result
            )
        )

    except Exception as e:
        st.error(
            f"Unable to load prediction history: {e}"
        )
        return

    if not records:
        st.info(
            "No prediction history yet."
        )
        return

    selected_id = (
        st.session_state.get(
            "selected_prediction_history"
        )
    )

    for record in records:
        record_id = record.get(
            "id"
        )

        display_name = (
            record.get(
                "display_name",
                "Unknown Song"
            )
        )

        label = record.get(
            "label",
            "N/A"
        )

        score = float(
            record.get(
                "predicted_score",
                0
            )
            or 0
        )

        created_at = (
            format_short_date(
                record.get(
                    "created_at"
                )
            )
        )

        with st.container(
            border=True
        ):
            col1, col2 = (
                st.columns(
                    [
                        4,
                        1
                    ]
                )
            )

            with col1:
                st.markdown(
                    f"**🎵 {display_name}**"
                )

                st.caption(
                    f"{label} · "
                    f"{score:.1f}/100 · "
                    f"{created_at}"
                )

            with col2:
                button_text = (
                    "Close"
                    if selected_id
                    == record_id
                    else "View Details"
                )

                if st.button(
                    button_text,
                    key=(
                        "view_prediction_"
                        f"{record_id}"
                    ),
                    use_container_width=True
                ):
                    if (
                        selected_id
                        == record_id
                    ):
                        st.session_state[
                            "selected_prediction_history"
                        ] = None

                    else:
                        st.session_state[
                            "selected_prediction_history"
                        ] = record_id

                    st.rerun()

            if (
                selected_id
                == record_id
            ):
                st.divider()

                show_prediction_detail(
                    record,
                    user_id
                )

def show_simulation_history(
    user_id
):
    try:
        result = (
            get_simulation_history(
                user_id,
                limit=50
            )
        )

        records = (
            normalise_history_result(
                result
            )
        )

    except Exception as e:
        st.error(
            f"Unable to load simulation history: {e}"
        )
        return

    if not records:
        st.info(
            "No simulation history yet."
        )
        return

    selected_id = (
        st.session_state.get(
            "selected_simulation_history"
        )
    )

    for record in records:
        record_id = record.get(
            "id"
        )

        display_name = (
            record.get(
                "display_name",
                "Unknown Song"
            )
        )

        original_score = float(
            record.get(
                "original_score",
                0
            )
            or 0
        )

        new_score = float(
            record.get(
                "new_score",
                0
            )
            or 0
        )

        difference = (
            new_score
            - original_score
        )

        created_at = (
            format_short_date(
                record.get(
                    "created_at"
                )
            )
        )

        with st.container(
            border=True
        ):
            col1, col2 = (
                st.columns(
                    [
                        4,
                        1
                    ]
                )
            )

            with col1:
                st.markdown(
                    f"**🎛️ {display_name}**"
                )

                st.caption(
                    f"{original_score:.1f} → "
                    f"{new_score:.1f} "
                    f"({difference:+.1f}) · "
                    f"{created_at}"
                )

            with col2:
                button_text = (
                    "Close"
                    if selected_id
                    == record_id
                    else "View Details"
                )

                if st.button(
                    button_text,
                    key=(
                        "view_simulation_"
                        f"{record_id}"
                    ),
                    use_container_width=True
                ):
                    if (
                        selected_id
                        == record_id
                    ):
                        st.session_state[
                            "selected_simulation_history"
                        ] = None

                    else:
                        st.session_state[
                            "selected_simulation_history"
                        ] = record_id

                    st.rerun()

            if (
                selected_id
                == record_id
            ):
                st.divider()

                show_simulation_detail(
                    record,
                    user_id
                )

def show_history():
    st.title(
        "📚 History"
    )

    st.caption(
        "Review your previous predictions "
        "and what-if simulations."
    )

    if not st.session_state.get(
        "authenticated",
        False
    ):
        st.warning(
            "Please login to view your history."
        )
        return

    user_id = (
        st.session_state.get(
            "user_id"
        )
    )

    if not user_id:
        st.error(
            "Unable to identify the current user."
        )
        return

    if (
        "selected_prediction_history"
        not in st.session_state
    ):
        st.session_state[
            "selected_prediction_history"
        ] = None

    if (
        "selected_simulation_history"
        not in st.session_state
    ):
        st.session_state[
            "selected_simulation_history"
        ] = None

    prediction_tab, simulation_tab = (
        st.tabs([
            "🔮 Prediction History",
            "🎛️ Simulation History"
        ])
    )

    with prediction_tab:
        show_prediction_history(
            user_id
        )

    with simulation_tab:
        show_simulation_history(
            user_id
        )