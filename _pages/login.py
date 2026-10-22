import secrets
import time

import streamlit as st

from services.db_service import (
    initialize_database
)

from services.auth_service import (
    register_user,
    authenticate_user,
    get_user_by_email,
    reset_password_by_email
)

from services.email_service import (
    send_password_reset_otp
)

from _pages.profile import (
    show_profile
)

OTP_EXPIRY_SECONDS = 300

def setup_database():
    try:
        initialize_database()

    except Exception as e:
        print(
            "Database setup error:",
            e
        )

def initialize_auth_state():
    defaults = {
        "authenticated": False,
        "user_id": None,
        "username": None,
        "email": None,
        "show_forgot_password": False,
        "reset_email": None,
        "reset_otp": None,
        "reset_otp_expiry": None,
        "reset_otp_verified": False,
        "reset_otp_attempts": 0
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[
                key
            ] = value

def set_logged_in_user(
    user
):
    st.session_state[
        "authenticated"
    ] = True

    st.session_state[
        "user_id"
    ] = user[
        "id"
    ]

    st.session_state[
        "username"
    ] = user[
        "username"
    ]

    st.session_state[
        "email"
    ] = user[
        "email"
    ]

def clear_reset_state():
    reset_keys = [
        "reset_email",
        "reset_otp",
        "reset_otp_expiry",
        "reset_otp_verified",
        "reset_otp_attempts"
    ]

    for key in reset_keys:
        st.session_state[
            key
        ] = (
            False
            if key
            == "reset_otp_verified"
            else 0
            if key
            == "reset_otp_attempts"
            else None
        )

def logout_user():
    keys = [
        "authenticated",
        "user_id",
        "username",
        "email",
        "profile_success",
        "profile_error"
    ]

    for key in keys:
        st.session_state.pop(
            key,
            None
        )

    initialize_auth_state()

def generate_otp():
    return str(
        secrets.randbelow(
            900000
        )
        + 100000
    )

def show_forgot_password():
    st.subheader(
        "🔑 Forgot Password"
    )

    st.caption(
        "Enter your registered email address "
        "to receive a verification code."
    )

    if not st.session_state.get(
        "reset_email"
    ):
        with st.form(
            "forgot_password_email_form"
        ):
            email = st.text_input(
                "Registered Email",
                placeholder=(
                    "you@example.com"
                )
            )

            send_button = (
                st.form_submit_button(
                    "📧 Send Verification Code",
                    type="primary",
                    use_container_width=True
                )
            )

        if send_button:
            email = (
                str(email)
                .strip()
                .lower()
            )

            if not email:
                st.error(
                    "Please enter your email address."
                )

            else:
                user = get_user_by_email(
                    email
                )

                if not user:
                    st.error(
                        "No account was found "
                        "with this email address."
                    )

                else:
                    otp = generate_otp()

                    result = (
                        send_password_reset_otp(
                            email,
                            otp
                        )
                    )

                    if result.get(
                        "success"
                    ):
                        st.session_state[
                            "reset_email"
                        ] = email

                        st.session_state[
                            "reset_otp"
                        ] = otp

                        st.session_state[
                            "reset_otp_expiry"
                        ] = (
                            time.time()
                            + OTP_EXPIRY_SECONDS
                        )

                        st.session_state[
                            "reset_otp_verified"
                        ] = False

                        st.session_state[
                            "reset_otp_attempts"
                        ] = 0

                        st.rerun()

                    else:
                        st.error(
                            result.get(
                                "message",
                                "Unable to send OTP."
                            )
                        )

    elif not st.session_state.get(
        "reset_otp_verified",
        False
    ):
        st.success(
            "📧 A 6-digit verification code "
            f"was sent to "
            f"{st.session_state['reset_email']}."
        )

        st.caption(
            "The code will expire in 5 minutes."
        )

        with st.form(
            "verify_otp_form"
        ):
            entered_otp = (
                st.text_input(
                    "Verification Code",
                    max_chars=6,
                    placeholder="6-digit code"
                )
            )

            verify_button = (
                st.form_submit_button(
                    "✅ Verify Code",
                    type="primary",
                    use_container_width=True
                )
            )

        if verify_button:
            expiry = (
                st.session_state.get(
                    "reset_otp_expiry"
                )
            )

            if (
                not expiry
                or time.time() > expiry
            ):
                st.error(
                    "The verification code has expired. "
                    "Please request a new code."
                )

            elif (
                st.session_state.get(
                    "reset_otp_attempts",
                    0
                )
                >= 5
            ):
                st.error(
                    "Too many incorrect attempts. "
                    "Please request a new code."
                )

            elif (
                entered_otp
                == st.session_state.get(
                    "reset_otp"
                )
            ):
                st.session_state[
                    "reset_otp_verified"
                ] = True

                st.rerun()

            else:
                st.session_state[
                    "reset_otp_attempts"
                ] += 1

                remaining = (
                    5
                    - st.session_state[
                        "reset_otp_attempts"
                    ]
                )

                st.error(
                    "Incorrect verification code. "
                    f"{remaining} attempt(s) remaining."
                )

        col1, col2 = st.columns(
            2
        )

        with col1:
            if st.button(
                "📧 Resend Code",
                use_container_width=True
            ):
                otp = generate_otp()

                result = (
                    send_password_reset_otp(
                        st.session_state[
                            "reset_email"
                        ],
                        otp
                    )
                )

                if result.get(
                    "success"
                ):
                    st.session_state[
                        "reset_otp"
                    ] = otp

                    st.session_state[
                        "reset_otp_expiry"
                    ] = (
                        time.time()
                        + OTP_EXPIRY_SECONDS
                    )

                    st.session_state[
                        "reset_otp_attempts"
                    ] = 0

                    st.success(
                        "A new verification code "
                        "has been sent."
                    )

                else:
                    st.error(
                        result.get(
                            "message",
                            "Unable to resend code."
                        )
                    )

        with col2:
            if st.button(
                "✏️ Change Email",
                use_container_width=True
            ):
                clear_reset_state()

                st.rerun()

    else:
        st.success(
            "✅ Email verified successfully."
        )

        st.subheader(
            "Set New Password"
        )

        with st.form(
            "reset_password_form"
        ):
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
                "lowercase, and a number."
            )

            reset_button = (
                st.form_submit_button(
                    "🔐 Reset Password",
                    type="primary",
                    use_container_width=True
                )
            )

        if reset_button:
            result = (
                reset_password_by_email(
                    email=(
                        st.session_state[
                            "reset_email"
                        ]
                    ),
                    new_password=(
                        new_password
                    ),
                    confirm_password=(
                        confirm_password
                    )
                )
            )

            if result.get(
                "success"
            ):
                clear_reset_state()

                st.session_state[
                    "show_forgot_password"
                ] = False

                st.session_state[
                    "login_message"
                ] = (
                    "✅ Password reset successfully. "
                    "You can now log in using "
                    "your new password."
                )

                st.rerun()

            else:
                st.error(
                    result.get(
                        "message",
                        "Unable to reset password."
                    )
                )

    st.divider()

    if st.button(
        "⬅ Back to Login",
        use_container_width=True
    ):
        clear_reset_state()

        st.session_state[
            "show_forgot_password"
        ] = False

        st.rerun()

def show_login():
    setup_database()
    initialize_auth_state()

    if st.session_state.get(
        "authenticated",
        False
    ):
        show_profile()
        return

    if st.session_state.get(
        "show_forgot_password",
        False
    ):
        show_forgot_password()
        return

    st.title(
        "🎵 Songlytics"
    )

    st.caption(
        "Music analytics and popularity prediction platform"
    )

    if st.session_state.get(
        "login_message"
    ):
        st.success(
            st.session_state.pop(
                "login_message"
            )
        )

    login_tab, register_tab = st.tabs(
        [
            "🔐 Login",
            "📝 Register"
        ]
    )

    with login_tab:
        st.subheader(
            "Welcome Back"
        )

        with st.form(
            "login_form"
        ):
            login_email = (
                st.text_input(
                    "Email",
                    placeholder=(
                        "you@example.com"
                    )
                )
            )

            login_password = (
                st.text_input(
                    "Password",
                    type="password"
                )
            )

            login_button = (
                st.form_submit_button(
                    "Login",
                    type="primary",
                    use_container_width=True
                )
            )

        if login_button:
            if (
                not login_email
                or not login_password
            ):
                st.error(
                    "Please enter your email "
                    "and password."
                )

            else:
                result = (
                    authenticate_user(
                        login_email,
                        login_password
                    )
                )

                if result.get(
                    "success"
                ):
                    set_logged_in_user(
                        result["user"]
                    )

                    st.rerun()

                else:
                    st.error(
                        result.get(
                            "message",
                            "Unable to login."
                        )
                    )

        if st.button(
            "Forgot Password?",
            key="forgot_password_button"
        ):
            clear_reset_state()

            st.session_state[
                "show_forgot_password"
            ] = True

            st.rerun()

    with register_tab:
        st.subheader(
            "Create Account"
        )

        with st.form(
            "register_form"
        ):
            username = (
                st.text_input(
                    "Username",
                    key="register_username"
                )
            )

            email = (
                st.text_input(
                    "Email",
                    key="register_email"
                )
            )

            password = (
                st.text_input(
                    "Password",
                    type="password",
                    key="register_password"
                )
            )

            confirm_password = (
                st.text_input(
                    "Confirm Password",
                    type="password",
                    key="register_confirm_password"
                )
            )

            st.caption(
                "Password must contain at least "
                "8 characters, including uppercase, "
                "lowercase, and a number."
            )

            register_button = (
                st.form_submit_button(
                    "Create Account",
                    type="primary",
                    use_container_width=True
                )
            )

        if register_button:
            if password != confirm_password:
                st.error(
                    "Passwords do not match."
                )

            else:
                result = register_user(
                    username=username,
                    email=email,
                    password=password
                )

                if result.get(
                    "success"
                ):
                    st.success(
                        "✅ Account created successfully. "
                        "You can now login."
                    )

                else:
                    st.error(
                        result.get(
                            "message",
                            "Unable to create account."
                        )
                    )