# services/history_service.py
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import json

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="songlytics",
        user="postgres",
        password="r2u0x0i5n", 
        port="5432"
    )

def save_prediction(user_id, song_name, prediction_label, probability):

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO prediction_history (user_id, song_name, prediction, probability, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, song_name, prediction_label, probability, datetime.now()))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving prediction: {e}")
        return False

def save_simulation(user_id, song_name, old_score, new_score, changes):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO simulation_history (user_id, song_name, old_score, new_score, changes, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, song_name, old_score, new_score, json.dumps(changes), datetime.now()))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving simulation: {e}")
        return False

def get_prediction_history(user_id, limit=50):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT song_name, prediction, probability, created_at
            FROM prediction_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                "song_name": row[0],
                "prediction": row[1],
                "probability": row[2],
                "created_at": row[3]
            }
            for row in rows
        ]
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

def get_user_predictions(user_id, filter_label="All", date_range="All time", sort_by="Newest first"):
    try:
        conn = get_connection()
        
        query = """
            SELECT id, song_name, prediction, probability, created_at 
            FROM prediction_history 
            WHERE user_id = %s
        """
        params = [user_id]
        
        if filter_label != "All":
            query += " AND prediction = %s"
            params.append(f"{filter_label} Popularity")
        
        # 日期范围
        if date_range == "Last 7 days":
            query += " AND created_at >= %s"
            params.append(datetime.now() - timedelta(days=7))
        elif date_range == "Last 30 days":
            query += " AND created_at >= %s"
            params.append(datetime.now() - timedelta(days=30))
        elif date_range == "Last 90 days":
            query += " AND created_at >= %s"
            params.append(datetime.now() - timedelta(days=90))
        
        # 排序
        if sort_by == "Newest first":
            query += " ORDER BY created_at DESC"
        elif sort_by == "Oldest first":
            query += " ORDER BY created_at ASC"
        elif sort_by == "Highest probability":
            query += " ORDER BY probability DESC"
        
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        print(f"Error in get_user_predictions: {e}")
        return pd.DataFrame()

def get_user_simulations(user_id, date_range="All time", sort_by="Newest first"):
    """获取用户模拟历史"""
    try:
        conn = get_connection()
        
        query = """
            SELECT id, song_name, old_score, new_score, changes, created_at 
            FROM simulation_history 
            WHERE user_id = %s
        """
        params = [user_id]
        
        # 日期范围
        if date_range == "Last 7 days":
            query += " AND created_at >= %s"
            params.append(datetime.now() - timedelta(days=7))
        elif date_range == "Last 30 days":
            query += " AND created_at >= %s"
            params.append(datetime.now() - timedelta(days=30))
        elif date_range == "Last 90 days":
            query += " AND created_at >= %s"
            params.append(datetime.now() - timedelta(days=90))
        
        # 排序
        if sort_by == "Newest first":
            query += " ORDER BY created_at DESC"
        elif sort_by == "Oldest first":
            query += " ORDER BY created_at ASC"
        elif sort_by == "Largest improvement":
            query += " ORDER BY (new_score - old_score) DESC"
        
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        print(f"Error in get_user_simulations: {e}")
        return pd.DataFrame()

def get_simulation_history(user_id, limit=50):
    """获取用户的历史模拟（简单版）"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT song_name, old_score, new_score, changes, created_at
            FROM simulation_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                "song_name": row[0],
                "old_score": row[1],
                "new_score": row[2],
                "changes": row[3],
                "created_at": row[4]
            }
            for row in rows
        ]
    except Exception as e:
        print(f"Error fetching simulation history: {e}")
        return []

# ==========================================
# 统计信息
# ==========================================

def get_prediction_stats(user_id):
    """获取用户预测统计信息"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 总预测数
        cursor.execute("SELECT COUNT(*) FROM prediction_history WHERE user_id = %s", (user_id,))
        total_predictions = cursor.fetchone()[0]
        
        # 总模拟数
        cursor.execute("SELECT COUNT(*) FROM simulation_history WHERE user_id = %s", (user_id,))
        total_simulations = cursor.fetchone()[0]
        
        # High 预测数
        cursor.execute(
            "SELECT COUNT(*) FROM prediction_history WHERE user_id = %s AND prediction = 'High Popularity'",
            (user_id,)
        )
        high_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        # 计算平均置信度（示例，实际需要从数据计算）
        avg_confidence = 65
        
        return {
            "total_predictions": total_predictions,
            "total_simulations": total_simulations,
            "high_count": high_count,
            "avg_confidence": avg_confidence
        }
    except Exception as e:
        print(f"Error in get_prediction_stats: {e}")
        return {
            "total_predictions": 0,
            "total_simulations": 0,
            "high_count": 0,
            "avg_confidence": 0
        }

# ==========================================
# 导出功能
# ==========================================

def export_history_to_csv(df, include_charts=True):
    """导出为 CSV"""
    if df.empty:
        return "No data available"
    return df.to_csv(index=False)

def export_history_to_pdf(df_pred, df_sim=None, report_type="Summary Report", include_charts=True):
    """导出为 PDF"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        import io
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # 标题
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea')
        )
        story.append(Paragraph(f"Songlytics Report - {report_type}", title_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # 统计信息
        story.append(Paragraph("Summary Statistics", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        if df_pred is not None and not df_pred.empty:
            story.append(Paragraph(f"Total Predictions: {len(df_pred)}", styles['Normal']))
            high_count = len(df_pred[df_pred['prediction'] == 'High Popularity']) if 'prediction' in df_pred.columns else 0
            story.append(Paragraph(f"High Popularity Predictions: {high_count}", styles['Normal']))
        
        if df_sim is not None and not df_sim.empty:
            story.append(Paragraph(f"Total Simulations: {len(df_sim)}", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except ImportError:
        # 如果没有 reportlab，返回简单文本
        return f"Report generated at {datetime.now()}".encode()
    except Exception as e:
        print(f"Error in export_history_to_pdf: {e}")
        return f"Error generating PDF: {e}".encode()

# ==========================================
# 删除功能
# ==========================================

def delete_prediction(prediction_id):
    """删除预测记录"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM prediction_history WHERE id = %s", (prediction_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting prediction: {e}")
        return False

def delete_simulation(simulation_id):
    """删除模拟记录"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM simulation_history WHERE id = %s", (simulation_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting simulation: {e}")
        return False

def clear_user_history(user_id):
    """清空用户历史记录"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM prediction_history WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM simulation_history WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error clearing history: {e}")
        return False