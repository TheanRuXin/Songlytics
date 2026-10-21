from datetime import datetime

import streamlit as st

from services.auth_service import (
    get_user_by_id,
    update_user_profile,
    change_password
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

def show_profile():
    st.title(
        "👤 My Profile"
    )

    if not st.session_state.get(
        "authenticated",
        False
    ):
        st.warning(
            "Please login to view your profile."
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

    user = get_user_by_id(
        user_id
    )

    if not user:
        st.error(
            "Unable to load account information."
        )
        return

    if st.session_state.get(
        "profile_success"
    ):
        st.success(
            st.session_state[
                "profile_success"
            ]
        )

    if st.session_state.get(
        "profile_error"
    ):
        st.error(
            st.session_state[
                "profile_error"
            ]
        )

    username = user[
        "username"
    ]

    email = user[
        "email"
    ]

    created_at = user.get(
        "created_at"
    )

    last_login = user.get(
        "last_login"
    )

    st.subheader(
        "📋 Account Information"
    )

    with st.container(
        border=True
    ):
        col1, col2 = st.columns(
            [
                1,
                2
            ]
        )

        with col1:
            st.markdown(
                "**👤 Username**"
            )

        with col2:
            st.write(
                username
            )

        st.divider()

        col1, col2 = st.columns(
            [
                1,
                2
            ]
        )

        with col1:
            st.markdown(
                "**📧 Email**"
            )

        with col2:
            st.write(
                email
            )

        st.divider()

        col1, col2 = st.columns(
            [
                1,
                2
            ]
        )

        with col1:
            st.markdown(
                "**📅 Member Since**"
            )

        with col2:
            st.write(
                format_datetime(
                    created_at
                )
            )

        st.divider()

        col1, col2 = st.columns(
            [
                1,
                2
            ]
        )

        with col1:
            st.markdown(
                "**🕐 Last Login**"
            )

        with col2:
            st.write(
                format_datetime(
                    last_login
                )
            )

    st.divider()

    if "profile_mode" not in st.session_state:
        st.session_state["profile_mode"] = None


    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "✏️ Edit Profile",
            use_container_width=True
        ):
            if (
                st.session_state[
                    "profile_mode"
                ] == "edit"
            ):
                st.session_state[
                    "profile_mode"
                ] = None
            else:
                st.session_state[
                    "profile_mode"
                ] = "edit"

            st.rerun()


    with col2:
        if st.button(
            "🔐 Change Password",
            use_container_width=True
        ):
            if (
                st.session_state[
                    "profile_mode"
                ] == "password"
            ):
                st.session_state[
                    "profile_mode"
                ] = None
            else:
                st.session_state[
                    "profile_mode"
                ] = "password"

            st.rerun()


    if (
        st.session_state[
            "profile_mode"
        ] == "edit"
    ):

        st.subheader(
            "✏️ Edit Profile"
        )

        with st.form(
            "edit_profile_form"
        ):

            col1, col2 = st.columns(2)

            with col1:
                new_username = st.text_input(
                    "Username",
                    value=user[
                        "username"
                    ]
                )

            with col2:
                new_email = st.text_input(
                    "Email",
                    value=user[
                        "email"
                    ]
                )

            save_col, cancel_col = (
                st.columns(2)
            )

            with save_col:
                save_profile = (
                    st.form_submit_button(
                        "💾 Save Changes",
                        type="primary",
                        use_container_width=True
                    )
                )

            with cancel_col:
                cancel_edit = (
                    st.form_submit_button(
                        "Cancel",
                        use_container_width=True
                    )
                )

            if save_profile:

                result = (
                    update_user_profile(
                        user_id,
                        new_username,
                        new_email
                    )
                )

                if result.get(
                    "success",
                    False
                ):
                    st.session_state[
                        "profile_success"
                    ] = result[
                        "message"
                    ]

                    st.session_state[
                        "profile_mode"
                    ] = None

                    updated_user = (
                        result.get(
                            "user"
                        )
                    )

                    if updated_user:
                        st.session_state[
                            "username"
                        ] = (
                            updated_user.get(
                                "username"
                            )
                        )

                        st.session_state[
                            "email"
                        ] = (
                            updated_user.get(
                                "email"
                            )
                        )

                    st.rerun()

                else:
                    st.error(
                        result.get(
                            "message",
                            "Unable to update profile."
                        )
                    )

            if cancel_edit:
                st.session_state[
                    "profile_mode"
                ] = None

                st.rerun()


    elif (
        st.session_state[
            "profile_mode"
        ] == "password"
    ):

        st.subheader(
            "🔐 Change Password"
        )

        with st.form(
            "change_password_form"
        ):

            current_password = (
                st.text_input(
                    "Current Password",
                    type="password"
                )
            )

            new_password = (
                st.text_input(
                    "New Password",
                    type="password"
                )
            )

            confirm_password = (
                st.text_input(
                    "Confirm New Password",
                    type="password"
                )
            )

            st.caption(
                "Password must contain at least "
                "8 characters, including uppercase, "
                "lowercase and a number."
            )

            save_col, cancel_col = (
                st.columns(2)
            )

            with save_col:
                change_button = (
                    st.form_submit_button(
                        "🔐 Change Password",
                        type="primary",
                        use_container_width=True
                    )
                )

            with cancel_col:
                cancel_password = (
                    st.form_submit_button(
                        "Cancel",
                        use_container_width=True
                    )
                )

            if change_button:

                result = change_password(
                    user_id,
                    current_password,
                    new_password,
                    confirm_password
                )

                if result.get(
                    "success",
                    False
                ):
                    st.session_state[
                        "profile_success"
                    ] = result[
                        "message"
                    ]

                    st.session_state[
                        "profile_mode"
                    ] = None

                    st.rerun()

                else:
                    st.error(
                        result.get(
                            "message",
                            "Unable to change password."
                        )
                    )

            if cancel_password:
                st.session_state[
                    "profile_mode"
                ] = None

                st.rerun()