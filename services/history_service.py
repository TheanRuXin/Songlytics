from psycopg2.extras import Json

from services.db_service import db_cursor

def make_json_safe(value):
    if value is None:
        return None

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(val)
            for key, val in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            make_json_safe(item)
            for item in value
        ]

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return value

def validate_user_id(user_id):
    if user_id is None:
        raise ValueError("User must be logged in.")

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid user ID.")

    if user_id <= 0:
        raise ValueError("Invalid user ID.")

    return user_id

def save_prediction(
    user_id,
    display_name,
    label,
    predicted_score,
    input_source=None,
    features=None
):
    try:
        user_id = validate_user_id(user_id)

        display_name = str(display_name).strip()
        label = str(label).strip()
        predicted_score = float(predicted_score)

        if not display_name:
            raise ValueError(
                "Prediction display name cannot be empty."
            )

        if not 0 <= predicted_score <= 100:
            raise ValueError(
                "Predicted score must be between 0 and 100."
            )

        safe_features = (
            make_json_safe(features)
            if features is not None
            else None
        )

        with db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO prediction_history (
                    user_id,
                    display_name,
                    label,
                    predicted_score,
                    input_source,
                    features
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    user_id,
                    display_name,
                    label,
                    predicted_score,
                    input_source,
                    Json(safe_features)
                    if safe_features is not None
                    else None
                )
            )

            history_id = cursor.fetchone()[0]

        return {
            "success": True,
            "id": history_id
        }

    except Exception as e:
        print("Save prediction history error:", e)

        return {
            "success": False,
            "message": str(e)
        }

def save_simulation(
    user_id,
    display_name,
    original_score,
    new_score,
    changes=None
):
    try:
        user_id = validate_user_id(user_id)

        display_name = str(display_name).strip()
        original_score = float(original_score)
        new_score = float(new_score)

        if not display_name:
            raise ValueError(
                "Simulation display name cannot be empty."
            )

        if not 0 <= original_score <= 100:
            raise ValueError(
                "Original score must be between 0 and 100."
            )

        if not 0 <= new_score <= 100:
            raise ValueError(
                "New score must be between 0 and 100."
            )

        safe_changes = (
            make_json_safe(changes)
            if changes is not None
            else {}
        )

        with db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO simulation_history (
                    user_id,
                    display_name,
                    original_score,
                    new_score,
                    changes
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    user_id,
                    display_name,
                    original_score,
                    new_score,
                    Json(safe_changes)
                )
            )

            history_id = cursor.fetchone()[0]

        return {
            "success": True,
            "id": history_id
        }

    except Exception as e:
        print("Save simulation history error:", e)

        return {
            "success": False,
            "message": str(e)
        }

def get_prediction_history(
    user_id,
    limit=50
):
    try:
        user_id = validate_user_id(user_id)

        limit = int(limit)
        limit = max(1, min(limit, 200))

        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    display_name,
                    label,
                    predicted_score,
                    input_source,
                    features,
                    created_at
                FROM prediction_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (
                    user_id,
                    limit
                )
            )

            rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "display_name": row[1],
                "label": row[2],
                "predicted_score": float(row[3]),
                "input_source": row[4],
                "features": row[5],
                "created_at": row[6]
            }
            for row in rows
        ]

    except Exception as e:
        print("Get prediction history error:", e)
        return []

def get_simulation_history(
    user_id,
    limit=50
):
    try:
        user_id = validate_user_id(user_id)

        limit = int(limit)
        limit = max(1, min(limit, 200))

        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    display_name,
                    original_score,
                    new_score,
                    changes,
                    created_at
                FROM simulation_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (
                    user_id,
                    limit
                )
            )

            rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "display_name": row[1],
                "original_score": float(row[2]),
                "new_score": float(row[3]),
                "score_change": (
                    float(row[3])
                    - float(row[2])
                ),
                "changes": row[4],
                "created_at": row[5]
            }
            for row in rows
        ]

    except Exception as e:
        print("Get simulation history error:", e)
        return []

def delete_prediction(
    user_id,
    prediction_id
):
    try:
        user_id = validate_user_id(user_id)
        prediction_id = int(prediction_id)

        with db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                DELETE FROM prediction_history
                WHERE id = %s
                AND user_id = %s
                """,
                (
                    prediction_id,
                    user_id
                )
            )

            deleted = cursor.rowcount > 0

        return deleted

    except Exception as e:
        print("Delete prediction error:", e)
        return False

def delete_simulation(
    user_id,
    simulation_id
):
    try:
        user_id = validate_user_id(user_id)
        simulation_id = int(simulation_id)

        with db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                DELETE FROM simulation_history
                WHERE id = %s
                AND user_id = %s
                """,
                (
                    simulation_id,
                    user_id
                )
            )

            deleted = cursor.rowcount > 0

        return deleted

    except Exception as e:
        print("Delete simulation error:", e)
        return False

def clear_prediction_history(user_id):
    try:
        user_id = validate_user_id(user_id)

        with db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                DELETE FROM prediction_history
                WHERE user_id = %s
                """,
                (user_id,)
            )

        return True

    except Exception as e:
        print("Clear prediction history error:", e)
        return False

def clear_simulation_history(user_id):
    try:
        user_id = validate_user_id(user_id)

        with db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                DELETE FROM simulation_history
                WHERE user_id = %s
                """,
                (user_id,)
            )

        return True

    except Exception as e:
        print("Clear simulation history error:", e)
        return False

def clear_all_history(user_id):
    try:
        user_id = validate_user_id(user_id)

        with db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                DELETE FROM prediction_history
                WHERE user_id = %s
                """,
                (user_id,)
            )

            cursor.execute(
                """
                DELETE FROM simulation_history
                WHERE user_id = %s
                """,
                (user_id,)
            )

        return True

    except Exception as e:
        print("Clear all history error:", e)
        return False