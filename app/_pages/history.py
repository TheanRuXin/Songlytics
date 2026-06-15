# history.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import base64

from services.history_service import (
    get_user_predictions,
    get_user_simulations,
    get_prediction_stats,
    export_history_to_csv,
    export_history_to_pdf,
    delete_prediction,
    delete_simulation
)

def show_history():
    st.markdown("""
        <style>
        .history-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(120deg, #4ecdc4, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 20px;
            color: white;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<p class="history-title">📜 Activity History</p>', unsafe_allow_html=True)
    st.caption("Track all your predictions and simulations")
    
    user_id = st.session_state.get("user_id", 1)

    stats = get_prediction_stats(user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats['total_predictions']}</div>
                <div class="stat-label">Total Predictions</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats['total_simulations']}</div>
                <div class="stat-label">Total Simulations</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats['high_count']}</div>
                <div class="stat-label">High Popularity Predictions</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats.get('avg_confidence', 0)}%</div>
                <div class="stat-label">Avg Confidence</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📊 Predictions", "🎛 Simulations", "📈 Analytics & Reports"])
    

    with tab1:
        st.subheader("📊 Prediction History")
        
        # 过滤器
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_label = st.selectbox(
                "Filter by popularity:",
                ["All", "High", "Medium", "Low"],
                key="pred_filter"
            )
        with col2:
            date_range = st.selectbox(
                "Date range:",
                ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
                key="pred_date"
            )
        with col3:
            sort_by = st.selectbox(
                "Sort by:",
                ["Newest first", "Oldest first", "Highest probability"],
                key="pred_sort"
            )
        
        # 获取数据
        df_pred = get_user_predictions(user_id, filter_label, date_range, sort_by)
        
        if df_pred.empty:
            st.info("📭 No prediction history yet. Make your first prediction!")
        else:
            # 显示统计摘要
            st.caption(f"📊 Showing {len(df_pred)} predictions")
            
            # 高级表格
            for idx, row in df_pred.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    # 歌曲名
                    with col1:
                        st.markdown(f"**🎵 {row['song_name']}**")
                        
                    
                    # 预测结果
                    with col2:
                        if row['prediction'] == "High Popularity":
                            st.markdown("🟢 **High**")
                        elif row['prediction'] == "Medium Popularity":
                            st.markdown("🟡 **Medium**")
                        else:
                            st.markdown("🔴 **Low**")
                    
                    # 概率
                    with col3:
                        prob = row.get('probability', 0)
                        st.progress(prob / 100)
                        st.caption(f"{prob:.1f}% confidence")
                    
                    # 删除按钮
                    with col4:
                        if st.button("🗑️", key=f"del_pred_{row.get('id', idx)}"):
                            delete_prediction(row.get('id'))
                            st.rerun()
                    
                    st.divider()
            
            # 批量操作
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Export Predictions to CSV", use_container_width=True):
                    csv_data = export_history_to_csv(df_pred)
                    b64 = base64.b64encode(csv_data.encode()).decode()
                    href = f'<a href="data:text/csv;base64,{b64}" download="predictions_history.csv">Download CSV</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("✅ Ready to download!")
            
            with col2:
                if st.button("📄 Export to PDF", use_container_width=True):
                    pdf_data = export_history_to_pdf(df_pred, "predictions")
                    b64 = base64.b64encode(pdf_data).decode()
                    href = f'<a href="data:application/pdf;base64,{b64}" download="predictions_report.pdf">Download PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("✅ Ready to download!")

    with tab2:
        st.subheader("🎛 Simulation History")
        
        # 过滤器
        col1, col2 = st.columns(2)
        with col1:
            sim_date_range = st.selectbox(
                "Date range:",
                ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
                key="sim_date"
            )
        with col2:
            sim_sort = st.selectbox(
                "Sort by:",
                ["Newest first", "Oldest first", "Largest improvement"],
                key="sim_sort"
            )
        
        df_sim = get_user_simulations(user_id, sim_date_range, sim_sort)
        
        if df_sim.empty:
            st.info("🎛 No simulation history yet. Try the What-If Simulation feature!")
        else:
            st.caption(f"📊 Showing {len(df_sim)} simulations")
            
            # 改进图表
            if len(df_sim) > 0:
                fig_improvement = go.Figure()
                
                for idx, row in df_sim.iterrows():
                    improvement = row.get('new_score', 0) - row.get('old_score', 0)
                    color = '#48dbfb' if improvement > 0 else '#ff6b6b'
                    
                    fig_improvement.add_trace(go.Bar(
                        name=row['song_name'][:20],
                        x=[row['song_name'][:20]],
                        y=[improvement],
                        marker_color=color,
                        text=f"{improvement:+.1f}",
                        textposition='outside'
                    ))
                
                fig_improvement.update_layout(
                    title="Popularity Score Improvements",
                    xaxis_title="Song",
                    yaxis_title="Change in Popularity Score",
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig_improvement, use_container_width=True)
            
            # 模拟记录表格
            for idx, row in df_sim.iterrows():
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 1.5, 1.5, 1.5, 1])
                    
                    with col1:
                        st.markdown(f"**🎵 {row['song_name']}**")
                        st.caption(row.get('created_at', ''))
                    
                    with col2:
                        old_score = row.get('old_score', 0)
                        st.metric("Original", f"{old_score:.0f}")
                    
                    with col3:
                        new_score = row.get('new_score', 0)
                        delta = new_score - old_score
                        st.metric("New", f"{new_score:.0f}", delta=f"{delta:+.0f}")
                    
                    with col4:
                        changes = row.get('changes', '{}')
                        st.caption(f"Changed: {changes[:50]}...")
                    
                    with col5:
                        if st.button("🗑️", key=f"del_sim_{row.get('id', idx)}"):
                            delete_simulation(row.get('id'))
                            st.rerun()
                    
                    st.divider()
    
    with tab3:
        st.subheader("📈 History Analytics")
        
        # 获取数据用于分析
        df_pred_all = get_user_predictions(user_id, "All", "All time", "Newest first")
        df_sim_all = get_user_simulations(user_id, "All time", "Newest first")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 预测趋势图
            if not df_pred_all.empty:
                df_pred_all['date'] = pd.to_datetime(df_pred_all.get('created_at', datetime.now()))
                daily_counts = df_pred_all.groupby(df_pred_all['date'].dt.date).size().reset_index(name='count')
                
                fig_trend = px.line(
                    daily_counts,
                    x='date',
                    y='count',
                    title='Predictions Over Time',
                    markers=True
                )
                fig_trend.update_layout(height=350)
                st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # 流行度分布饼图
            if not df_pred_all.empty:
                dist = df_pred_all['prediction'].value_counts().reset_index()
                dist.columns = ['Prediction', 'Count']
                
                fig_dist = px.pie(
                    dist,
                    values='Count',
                    names='Prediction',
                    title='Your Prediction Distribution',
                    color_discrete_sequence=['#48dbfb', '#feca57', '#ff6b6b'],
                    hole=0.4
                )
                fig_dist.update_layout(height=350)
                st.plotly_chart(fig_dist, use_container_width=True)
        
        # 综合报告
        st.markdown("---")
        st.subheader("📄 Generate Comprehensive Report")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            report_type = st.selectbox(
                "Report Type:",
                ["Summary Report", "Detailed Analysis", "Performance Review"]
            )
        
        with col2:
            report_format = st.selectbox(
                "Format:",
                ["PDF", "CSV", "JSON"]
            )
        
        with col3:
            include_charts = st.checkbox("Include Charts", value=True)
        
        if st.button("📊 Generate Report", type="primary", use_container_width=True):
            with st.spinner("Generating report..."):
                if report_format == "CSV":
                    report_data = export_history_to_csv(df_pred_all, include_charts)
                    b64 = base64.b64encode(report_data.encode()).decode()
                    href = f'<a href="data:text/csv;base64,{b64}" download="songlytics_report.csv">Download CSV Report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                
                elif report_format == "PDF":
                    pdf_data = export_history_to_pdf(df_pred_all, df_sim_all, report_type, include_charts)
                    b64 = base64.b64encode(pdf_data).decode()
                    href = f'<a href="data:application/pdf;base64,{b64}" download="songlytics_report.pdf">Download PDF Report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                
                else:  # JSON
                    import json
                    report_json = {
                        "generated_at": datetime.now().isoformat(),
                        "user_id": user_id,
                        "report_type": report_type,
                        "predictions": df_pred_all.to_dict('records') if not df_pred_all.empty else [],
                        "simulations": df_sim_all.to_dict('records') if not df_sim_all.empty else [],
                        "stats": stats
                    }
                    json_str = json.dumps(report_json, indent=2, default=str)
                    b64 = base64.b64encode(json_str.encode()).decode()
                    href = f'<a href="data:application/json;base64,{b64}" download="songlytics_report.json">Download JSON Report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                
                st.success("✅ Report generated successfully!")
    
    # ==========================================
    # Footer
    # ==========================================
    st.markdown("---")
    st.caption("💡 Tip: Click the delete button (🗑️) to remove individual records. Export your data for offline analysis.")