import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

from services.dashboard_service import (
    get_kpi,
    get_popularity_distribution,
    get_feature_by_popularity,
    get_correlation_matrix,
    get_feature_importance_from_model,
    get_source_distribution,
    get_tempo_distribution,
    get_explicit_distribution,
    get_top_songs_by_popularity,
    search_songs
)

def show_dashboard():
    
    st.markdown("""
        <style>
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .music-title {
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(120deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient 5s ease infinite;
            text-align: center;
            margin-bottom: 0;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        
        .kpi-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 20px;
            color: white;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }
        
        .kpi-card:hover {
            transform: translateY(-5px);
        }
        
        .kpi-value {
            font-size: 2rem;
            font-weight: bold;
        }
        
        .kpi-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .custom-divider {
            background: linear-gradient(90deg, transparent, #4ecdc4, #ff6b6b, transparent);
            height: 3px;
            margin: 20px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="music-title">🎵 Songlytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Professional Music Analytics Dashboard | AI-Powered Insights</p>', unsafe_allow_html=True)
    
    kpi = get_kpi()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📀 Total Songs", f"{kpi['total']:,}", 
                  delta="100%", delta_color="off")
    
    with col2:
        st.metric("🎧 High Popularity", f"{kpi['high_count']:,}", 
                  delta=f"{kpi['high_count']/kpi['total']*100:.1f}% of total",
                  delta_color="normal")
    
    with col3:
        st.metric("📊 Medium Popularity", f"{kpi['medium_count']:,}")
    
    with col4:
        st.metric("📉 Low Popularity", f"{kpi['low_count']:,}")
    
    with col5:
        st.metric("⭐ Avg Popularity", f"{kpi.get('avg_popularity', 'N/A')}")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### 📊 Popularity Distribution")
        
        pop_dist = get_popularity_distribution()
        

        fig_pie = go.Figure(data=[go.Pie(
            labels=pop_dist['label'],
            values=pop_dist['count'],
            hole=0.5,
            marker=dict(colors=['#ff6b6b', '#feca57', '#48dbfb']),
            textinfo='label+percent',
            textposition='auto',
            pull=[0, 0, 0.05],
            rotation=90
        )])
        
        fig_pie.update_layout(
            height=400,
            title={
                'text': 'Songs by Popularity Class',
                'font': {'size': 16, 'weight': 'bold'}
            },
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("### 📦 Data Sources")
        
        source_dist = get_source_distribution()
        
        if not source_dist.empty:
            fig_source = go.Figure(data=[go.Bar(
                x=source_dist['source'],
                y=source_dist['count'],
                marker_color=['#667eea', '#764ba2', '#f093fb', '#4ecdc4'],
                text=source_dist['count'],
                textposition='outside',
                hovertemplate='Source: %{x}<br>Songs: %{y}<extra></extra>'
            )])
            
            fig_source.update_layout(
                height=400,
                title='Songs by Data Source',
                xaxis_title="Data Source",
                yaxis_title="Number of Songs",
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_source, use_container_width=True)
        else:
            st.info("📁 Source information not available")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("### 🔗 Audio Features Correlation Matrix")
    st.caption("Understanding relationships between different audio characteristics")
    
    corr_matrix = get_correlation_matrix()
    
    if not corr_matrix.empty:
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdBu',
            zmin=-1,
            zmax=1,
            text=corr_matrix.round(2).values,
            texttemplate='%{text}',
            textfont={"size": 10},
            hovertemplate='%{x} ↔ %{y}<br>Correlation: %{z:.3f}<extra></extra>'
        ))
        
        fig_corr.update_layout(
            height=550,
            title='Feature Correlation Matrix',
            xaxis_title="Features",
            yaxis_title="Features",
            xaxis={'tickangle': 45}
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("### 📈 Feature Comparison by Popularity")
    
    features_to_compare = ['danceability', 'energy', 'valence', 'acousticness', 'loudness', 'speechiness', 'liveness']
    
    selected_features = st.multiselect(
        "Select features to analyze:",
        features_to_compare,
        default=['danceability', 'energy', 'valence'],
        help="Choose one or more audio features to compare across popularity classes"
    )
    
    if selected_features:
        comparison_data = []
        for feature in selected_features:
            feature_data = get_feature_by_popularity(feature)
            if not feature_data.empty:
                feature_data['feature'] = feature
                comparison_data.append(feature_data)
        
        if comparison_data:
            df_compare = pd.concat(comparison_data)
            
            fig_compare = go.Figure()
            
            colors = {'Low': '#ff6b6b', 'Medium': '#feca57', 'High': '#48dbfb'}
            
            for label in ['Low', 'Medium', 'High']:
                df_label = df_compare[df_compare['label'] == label]
                fig_compare.add_trace(go.Bar(
                    name=label,
                    x=df_label['feature'],
                    y=df_label['mean'],
                    error_y=dict(type='data', array=df_label['std'] if 'std' in df_label else None, visible=True),
                    marker_color=colors[label],
                    text=df_label['mean'].round(3),
                    textposition='outside',
                    hovertemplate='%{x}<br>Mean: %{y:.3f}<br>Class: ' + label + '<extra></extra>'
                ))
            
            fig_compare.update_layout(
                barmode='group',
                title='Audio Features Across Popularity Classes',
                xaxis_title="Audio Features",
                yaxis_title="Average Value (0-1 scale)",
                height=500,
                legend_title="Popularity Class",
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_compare, use_container_width=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 Feature Importance")
        st.caption("What drives popularity? Model insights")
        
        importance = get_feature_importance_from_model()
        
        if not importance.empty:
            fig_importance = go.Figure(data=[go.Bar(
                x=importance.head(10)['importance'],
                y=importance.head(10)['feature'],
                orientation='h',
                marker_color=importance.head(10)['importance'],
                marker_colorscale='Viridis',
                text=importance.head(10)['importance'].round(3),
                textposition='outside',
                hovertemplate='Feature: %{y}<br>Importance: %{x:.3f}<extra></extra>'
            )])
            
            fig_importance.update_layout(
                height=450,
                title='Top 10 Most Important Features',
                xaxis_title="Importance Score",
                yaxis_title="Feature",
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig_importance, use_container_width=True)
    
    with col2:
        st.markdown("### 🎚️ Tempo Distribution")
        
        tempo_dist = get_tempo_distribution()
        
        if not tempo_dist.empty:
            fig_tempo = go.Figure(data=[go.Pie(
                labels=tempo_dist['category'],
                values=tempo_dist['count'],
                hole=0.4,
                marker=dict(colors=px.colors.sequential.Plasma),
                textinfo='label+percent',
                textposition='auto'
            )])
            
            fig_tempo.update_layout(
                height=450,
                title='Song Distribution by Tempo',
                legend=dict(orientation="v")
            )
            
            st.plotly_chart(fig_tempo, use_container_width=True)
        else:
            st.info("🎚️ Tempo data not available")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔞 Explicit Content Analysis")
        
        explicit_dist = get_explicit_distribution()
        
        if not explicit_dist.empty:
            fig_explicit = go.Figure(data=[go.Pie(
                labels=explicit_dist['label'],
                values=explicit_dist['count'],
                hole=0.3,
                marker=dict(colors=['#4ecdc4', '#ff6b6b']),
                textinfo='label+percent',
                pull=[0, 0.05]
            )])
            
            fig_explicit.update_layout(
                height=400,
                title='Clean vs Explicit Songs'
            )
            
            st.plotly_chart(fig_explicit, use_container_width=True)
        else:
            st.info("🔞 Explicit data not available")
    
    with col2:
        st.markdown("### 📈 Genre Popularity")
        
        st.info("🎤 Genre analysis coming soon...")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.markdown("### 🎵 Song Explorer")
    
    tab1, tab2, tab3 = st.tabs(["🏆 Top Popular Songs", "🔍 Advanced Search", "🎯 Recommendations"])
    
    with tab1:
        top_songs = get_top_songs_by_popularity(20)
        if not top_songs.empty:
            top_songs.insert(0, 'rank', range(1, len(top_songs) + 1))
    
            def get_color(level):
                colors = {'High': '#48dbfb', 'Medium': '#feca57', 'Low': '#ff6b6b'}
                return colors.get(level, '#ccc')
            
            top_songs['color'] = top_songs['popularity_label'].apply(get_color)
            
            st.dataframe(
                top_songs[['rank', 'song', 'artist', 'popularity_label']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("🏆 No song data available")
    
    with tab2:
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("Enter song or artist name:", placeholder="e.g., Yummy, Justin Bieber")
        with col2:
            st.write("")
            st.write("")
            search_button = st.button("🔍 Search", type="primary")
        
        if search_term or search_button:
            results = search_songs(search_term)
            if not results.empty:
                st.success(f"✅ Found {len(results)} songs matching '{search_term}'")
                st.dataframe(results, use_container_width=True, hide_index=True)
            else:
                st.warning("No songs found. Try a different search term.")
    
    with tab3:
        st.info("🎯 Personalized recommendations will appear here based on your listening history and preferences.")
        st.caption("Feature coming soon - Connect your Spotify account for personalized insights!")
    
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center;">
            <p style="color: #666;">
                🎵 Songlytics - AI-Powered Music Analytics Platform<br>
                Built with Streamlit | XGBoost | SHAP | PostgreSQL<br>
                Data-driven insights for better music production
            </p>
            <p style="color: #999; font-size: 0.8rem;">
                Last updated: {} 
            </p>
        </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)