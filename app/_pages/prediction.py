# _pages/prediction.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from services.prediction_service import predict, FEATURES
from services.shap_service import explain
from services.history_service import save_prediction
from services.recommendation_service import recommend_feature_changes
from services.spotify_service import spotify_service

def display_prediction_results(result, explanation, features_df):
    
    label = result["label"]
    prob = result["probability"]
    confidence = result.get("confidence", "Medium")
    score = result.get("score", 0)
    if score < 0:
        score = prob * 100  
    elif score > 100:# 
        score = 100
    
    if label == "High Popularity":
        color = "#48dbfb"
        emoji = "🚀"
        status = "Excellent! This song has high hit potential!"
    elif label == "Medium Popularity":
        color = "#feca57"
        emoji = "📈"
        status = "Good potential! Some improvements could help."
    else:
        color = "#ff6b6b"
        emoji = "⚠️"
        status = "Needs improvement. Check suggestions below."
    
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, {color}, {color}dd); border-radius: 20px; padding: 25px; margin: 20px 0;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 1rem; opacity: 0.9;">AI Prediction Result</div>
                    <div style="font-size: 2.5rem; font-weight: bold;">{emoji} {label}</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">{status}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; opacity: 0.9;">Confidence</div>
                    <div style="font-size: 2rem; font-weight: bold;">{prob:.1%}</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">{confidence} Confidence</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.metric("Predicted Popularity Score", f"{score:.1f}/100")

    st.subheader("📊 Feature Impact Analysis")
    st.caption("Understanding what drives this prediction")
    
    df_exp = pd.DataFrame(explanation)
    df_exp = df_exp.sort_values("impact", ascending=True)
    
    fig = go.Figure(data=[
        go.Bar(
            x=df_exp['impact'],
            y=df_exp['feature'],
            orientation='h',
            marker_color=['#48dbfb' if x > 0 else '#ff6b6b' for x in df_exp['impact']],
            text=df_exp['impact'].round(3),
            textposition='outside',
            hovertemplate='Feature: %{y}<br>Impact: %{x:.3f}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="SHAP Feature Impact",
        xaxis_title="Impact on Prediction (Positive = Higher Popularity)",
        yaxis_title="Feature",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
 
    if label in ["Low Popularity", "Medium Popularity"]:
        st.subheader("🎯 Personalized Improvement Suggestions")
        
        suggestions = recommend_feature_changes(features_df, explanation)
        
        for i, s in enumerate(suggestions):
            with st.container():
                col1, col2 = st.columns([1, 10])
                with col1:
                    st.markdown(f"### {i+1}")
                with col2:
                    st.info(f"💡 **{s['message']}**")
                    if s.get("action"):
                        st.code(s["action"], language=None)
                st.divider()
    else:
        st.success("🎉 **Great audio features!** Your song has high popularity potential. Keep up the good work!")

def show_simulation_ui():
    
    st.header("🎛️ What-If Simulation")
    
    song_name = st.session_state.get("song_name_for_sim", "Unknown Song")
    st.write(f"Simulating: **{song_name}**")
    
    base = st.session_state.get("sim_features", {})
    
    if not base:
        st.warning("No data found. Please go back and make a prediction first.")
        if st.button("← Back to Prediction", use_container_width=True):
            st.session_state.show_simulation_mode = False
            st.rerun()
        return
    
    # 默认值
    default_values = {
        "duration_ms": base.get("duration_ms", 200000),
        "explicit": base.get("explicit", 0),
        "danceability": base.get("danceability", 0.5),
        "energy": base.get("energy", 0.5),
        "loudness": base.get("loudness", -10),
        "speechiness": base.get("speechiness", 0.05),
        "acousticness": base.get("acousticness", 0.5),
        "instrumentalness": base.get("instrumentalness", 0.0),
        "liveness": base.get("liveness", 0.1),
        "valence": base.get("valence", 0.5),
        "tempo": base.get("tempo", 120),
        "score": base.get("score", 0)  
    }
    
    st.subheader("🎚️ Adjust Audio Features")
    st.caption("Adjust the sliders below to see how popularity score changes")
    
    col1, col2 = st.columns(2)
    
    input_features = {}
    
    with col1:
        input_features["duration_ms"] = st.slider("📏 Duration (ms)", 50000, 600000, int(default_values["duration_ms"]))
        input_features["explicit"] = st.selectbox("🔞 Explicit", [0, 1], index=int(default_values["explicit"]), format_func=lambda x: "Yes" if x else "No")
        input_features["danceability"] = st.slider("💃 Danceability", 0.0, 1.0, float(default_values["danceability"]))
        input_features["energy"] = st.slider("⚡ Energy", 0.0, 1.0, float(default_values["energy"]))
        input_features["loudness"] = st.slider("🔊 Loudness (dB)", -60.0, 0.0, float(default_values["loudness"]))
        input_features["speechiness"] = st.slider("🗣️ Speechiness", 0.0, 1.0, float(default_values["speechiness"]))
    
    with col2:
        input_features["acousticness"] = st.slider("🎸 Acousticness", 0.0, 1.0, float(default_values["acousticness"]))
        input_features["instrumentalness"] = st.slider("🎹 Instrumentalness", 0.0, 1.0, float(default_values["instrumentalness"]))
        input_features["liveness"] = st.slider("🎤 Liveness", 0.0, 1.0, float(default_values["liveness"]))
        input_features["valence"] = st.slider("😊 Valence", 0.0, 1.0, float(default_values["valence"]))
        input_features["tempo"] = st.slider("⏱️ Tempo (BPM)", 40, 220, int(default_values["tempo"]))
    
    df_input = pd.DataFrame([input_features])[FEATURES]
    
    st.divider()
    
    if st.button("🚀 Run Simulation", type="primary", use_container_width=True):
        with st.spinner("Running simulation..."):
            result = predict(df_input)
            explanation = explain(df_input)

            score = result.get("score", result["probability"] * 100)
            if score < 0:
                score = result["probability"] * 100
            result["score"] = score
            original_score = default_values.get("score", 50)
            if original_score < 0:
                original_score = 50
            
            new_score = result.get("score", result["probability"] * 100)
            simulated_name = f"{song_name} (simulated)"
            # 记录变化
            changes = {}
            for key in FEATURES:
                if key in default_values and key in input_features:
                    old_val = default_values[key]
                    new_val = input_features[key]
                    if old_val != new_val:
                        changes[key] = {
                            "old": old_val,
                            "new": new_val
                        }
            
            try:
                from services.history_service import save_simulation
                save_success = save_simulation(
                    st.session_state.get("user_id", 1),
                    simulated_name,
                    original_score,
                    new_score,
                    changes
                )
                if save_success:
                    st.success(f"✅ Simulation saved to history: {simulated_name}")
                else:
                    st.warning("⚠️ Simulation completed but could not save to history")
            except Exception as e:
                st.error(f"Failed to save simulation: {e}")

            st.subheader("📊 Simulation Result")
            
            label = result["label"]
            if label == "High Popularity":
                st.success(f"🟢 **{label}** - {result['probability']:.1%}")
            elif label == "Medium Popularity":
                st.warning(f"🟡 **{label}** - {result['probability']:.1%}")
            else:
                st.error(f"🔴 **{label}** - {result['probability']:.1%}")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Original Score", f"{original_score:.1f}")
            with col2:
                delta = new_score - original_score
                st.metric("New Score", f"{new_score:.1f}", delta=f"{delta:+.1f}")

            # 显示特征影响
            st.subheader("📊 Feature Impact")
            df_exp = pd.DataFrame(explanation).sort_values("impact", ascending=False)
            st.bar_chart(df_exp.set_index("feature")["impact"])
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("⬅ Back to Prediction", use_container_width=True):
            st.session_state.show_simulation_mode = False
            st.session_state.return_from_simulation = True
            st.rerun()


def show_prediction():

    if st.session_state.get("show_simulation_mode", False):
        show_simulation_ui()
        return
    
    st.markdown("""
        <style>
        .prediction-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(120deg, #4ecdc4, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
        }
        
        .result-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 25px;
            color: white;
            text-align: center;
            margin: 20px 0;
        }
        
        .result-label {
            font-size: 2rem;
            font-weight: bold;
        }
        
        .result-prob {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        </style>
    """, unsafe_allow_html=True)
        
    st.markdown('<p class="prediction-title">🎵 Song Popularity Predictor</p>', unsafe_allow_html=True)
    st.caption("AI-powered music popularity prediction using advanced audio analysis")
    
    if st.session_state.get("return_from_simulation", False):
        st.session_state.return_from_simulation = False
        st.session_state.prediction_done = True

    # 3. View Switcher: If a prediction is already done, show the results panel
    if st.session_state.get("prediction_done", False) and "last_prediction_result" in st.session_state:
        result = st.session_state.last_prediction_result
        explanation = st.session_state.last_explanation
        features_df = st.session_state.last_features_df
        display_name = st.session_state.get("song_name", "Unknown Song")

        display_prediction_results(result, explanation, features_df)

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎛 Try What-if Simulation", key="sim_btn_results", use_container_width=True):
                st.session_state.show_simulation_mode = True
                st.session_state.sim_features = features_df.iloc[0].to_dict()
                st.session_state.song_name_for_sim = display_name
                st.rerun()
        with col2:
            if st.button("🔍 Predict Another Song", key="new_prediction_btn", use_container_width=True):
                # Clean up states to drop back to search inputs
                st.session_state.prediction_done = False
                st.session_state.temp_features_df = None
                st.rerun()
                
        st.markdown("---")
        st.caption("💡 Powered by XGBoost | SHAP Explainability | Real-time Spotify API")
        return

    input_mode = st.radio(
        "Select input method:",
        ["🔍 Search Spotify", "📁 Choose from Dataset", "✏️ Manual Input"],
        horizontal=True
    )
    
    features_df = None
    song_name = None
    artist_name = None

    if input_mode == "🔍 Search Spotify":
        st.markdown("### 🔍 Search any song on Spotify")
        
        search_query = st.text_input(
            "Enter song name or artist:",
            placeholder="e.g., Blinding Lights, The Weeknd, Taylor Swift"
        )
        
        if search_query:
            with st.spinner("Searching Spotify database..."):
                results = spotify_service.search_song(search_query, limit=15)
            
            if results:
                search_df = pd.DataFrame(results)
                search_df["display"] = search_df["song"] + " - " + search_df["artist"]
                
                selected_display = st.selectbox(
                    "Select a song from search results:",
                    search_df["display"].tolist()
                )
                
                selected_row = search_df[search_df["display"] == selected_display].iloc[0]
                track_id = selected_row["track_id"]
                song_name = selected_row["song"]
                artist_name = selected_row["artist"]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"🎤 **Artist:** {artist_name}")
                with col2:
                    st.info(f"⭐ **Spotify Popularity:** {selected_row.get('popularity', 'N/A')}/100")
                
                st.caption(f"📀 **Album:** {selected_row.get('album_name', 'N/A')}")
                
                if st.button("🎵 Get Audio Features & Predict", key="spotify_predict", type="primary"):
                    with st.spinner("Fetching audio features from Spotify API..."):
                        features_dict = spotify_service.get_audio_features(track_id)
                    
                    if features_dict:
                        features_df = pd.DataFrame([features_dict])
                        features_df = features_df[FEATURES]
                        
                        st.session_state.temp_features_df = features_df
                        st.session_state.temp_song_name = song_name
                        st.session_state.temp_artist_name = artist_name
                        st.session_state.prediction_ready = True
                        
                        st.success("✅ Audio features retrieved successfully!")
                    else:
                        st.error("❌ Could not retrieve audio features for this song.")
            else:
                st.warning("No results found. Try a different search term.")
    
    elif input_mode == "📁 Choose from Dataset":
        st.markdown("### 📁 Choose a song from our curated dataset")
        
        CSV_PATH = "C:/Users/ruxin/Documents/ruxin/FYP/Data/spotify_merged_cleaned.csv"
        
        @st.cache_data
        def load_dataset():
            df = pd.read_csv(CSV_PATH)
            df["song"] = df["song"].astype(str)
            df["artist"] = df["artist"].astype(str)
            df["song_artist"] = df["song"] + " - " + df["artist"]
            return df
        
        df = load_dataset()
        song_list = df["song_artist"].tolist()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_term = st.text_input(
                "🔍 Search or type song name:",
                placeholder="e.g., Blinding Lights, Taylor Swift...",
                key="dataset_search"
            )
        
        with col2:
            st.write("")
            st.write("")
            use_selectbox = st.toggle("📋 Or browse full list", key="browse_mode")
        
        selected = None
        
        if use_selectbox:
            selected = st.selectbox("Choose a song:", song_list, key="browse_select")
        else:
            if search_term:
                search_lower = search_term.lower()
                filtered_songs = [song for song in song_list if search_lower in song.lower()]
                
                if filtered_songs:
                    selected = st.selectbox(
                        f"Found {len(filtered_songs)} matching songs:",
                        filtered_songs[:20]
                    )
                    st.caption(f"💡 Showing top {min(20, len(filtered_songs))} of {len(filtered_songs)} matches")
                else:
                    st.warning(f"No matching songs found for '{search_term}'")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        custom_song = st.text_input("Song name:", value=search_term)
                    with col_b:
                        custom_artist = st.text_input("Artist name:", placeholder="Unknown Artist")
                    
                    if custom_song:
                        selected = f"{custom_song} - {custom_artist}" if custom_artist else custom_song
                        st.info(f"🎵 Using custom song: {selected}")
        
        if selected:
            if " - " in selected:
                song_name, artist_name = selected.split(" - ", 1)
            else:
                song_name = selected
                artist_name = "Unknown Artist"
            
            st.success(f"✅ Selected: **{song_name}** by **{artist_name}**")
            
            if st.button("🚀 Load Features & Predict", key="dataset_load", type="primary"):
                row = df[(df["song"] == song_name) & (df["artist"] == artist_name)]
                
                if not row.empty:
                    features_df = row[FEATURES].iloc[[0]].copy()
                    st.success("✅ Features loaded from dataset!")
                else:
                    st.warning("⚠️ This song is not in the dataset. Using average feature values.")
                    avg_features = df[FEATURES].mean()
                    features_df = pd.DataFrame([avg_features])[FEATURES].copy()
                    st.info("📊 Using average feature values from dataset")
                
                st.session_state.temp_features_df = features_df
                st.session_state.temp_song_name = song_name
                st.session_state.temp_artist_name = artist_name
                st.session_state.prediction_ready = True

    else:
        st.markdown("### 🎚️ Enter Audio Features Manually")
        st.caption("💡 If you know your song's audio features, enter them below")
        
        col1, col2 = st.columns(2)
        
        with col1:
            duration_ms = st.number_input("📏 Duration (ms)", 60000, 600000, 180000)
            danceability = st.slider("💃 Danceability", 0.0, 1.0, 0.6)
            energy = st.slider("⚡ Energy", 0.0, 1.0, 0.7)
            loudness = st.slider("🔊 Loudness (dB)", -60.0, 0.0, -6.0)
            speechiness = st.slider("🗣️ Speechiness", 0.0, 1.0, 0.05)
        
        with col2:
            acousticness = st.slider("🎸 Acousticness", 0.0, 1.0, 0.3)
            instrumentalness = st.slider("🎹 Instrumentalness", 0.0, 1.0, 0.0)
            liveness = st.slider("🎤 Liveness", 0.0, 1.0, 0.1)
            valence = st.slider("😊 Valence", 0.0, 1.0, 0.6)
            tempo = st.number_input("⏱️ Tempo (BPM)", 40, 220, 120)
            explicit = st.selectbox("🔞 Explicit", ["No", "Yes"])
        
        song_name = st.text_input("🎵 Song Name (optional)", placeholder="Custom Song")
        artist_name = st.text_input("🎤 Artist Name (optional)", placeholder="User Input")
        
        if not song_name:
            song_name = "Custom Song"
        if not artist_name:
            artist_name = "User Input"
        
        if st.button("✅ Set Features & Predict", key="manual_set", type="primary"):
            features_dict = {
                "duration_ms": duration_ms,
                "danceability": danceability,
                "energy": energy,
                "loudness": loudness,
                "speechiness": speechiness,
                "acousticness": acousticness,
                "instrumentalness": instrumentalness,
                "liveness": liveness,
                "valence": valence,
                "tempo": tempo,
                "explicit": 1 if explicit == "Yes" else 0
            }
            features_df = pd.DataFrame([features_dict])
            features_df = features_df[FEATURES]
            
            st.session_state.temp_features_df = features_df
            st.session_state.temp_song_name = song_name
            st.session_state.temp_artist_name = artist_name
            st.session_state.prediction_ready = True
            st.success("✅ Manual features set!")
  
    features_df = st.session_state.get("temp_features_df", None)
    song_name = st.session_state.get("temp_song_name", None)
    artist_name = st.session_state.get("temp_artist_name", None)
    
    if features_df is not None:
        st.divider()
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.info(f"🎵 **Ready to predict:** {song_name} - {artist_name}")
        
        with col2:
            predict_button = st.button("🚀 Run Prediction", key="run_prediction", type="primary", use_container_width=True)
        
        with col3:
            if st.button("🔄 Reset", key="reset_prediction", use_container_width=True):
                st.session_state.temp_features_df = None
                st.session_state.prediction_done = False
                st.rerun()
        
        if predict_button:
            with st.spinner("🔮 Analyzing song features with AI model..."):
                result = predict(features_df)
                explanation = explain(features_df)
            
            display_name = f"{song_name} - {artist_name}"
            save_prediction(
                st.session_state.get("user_id", 1),
                display_name,
                result["label"],
                result["probability"] * 100
            )
            
            st.session_state.last_prediction_result = result
            st.session_state.last_features_df = features_df
            st.session_state.last_explanation = explanation
            st.session_state.prediction_done = True
            st.session_state.sim_features = features_df.iloc[0].to_dict()
            st.session_state.song_name = display_name
            
            display_prediction_results(result, explanation, features_df)

            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎛 Try What-if Simulation", key="simulation_btn_main", use_container_width=True):
                    st.session_state.show_simulation_mode = True
                    st.session_state.sim_features = features_df.iloc[0].to_dict()
                    st.session_state.song_name_for_sim = display_name
                    st.rerun()
            with col2:
                if st.button("🔍 Predict Another", key="new_prediction_btn", use_container_width=True):

                    for key in ['prediction_done', 'temp_features_df', 'temp_song_name', 
                            'temp_artist_name', 'last_prediction_result', 'last_features_df', 
                            'last_explanation', 'sim_features', 'song_name']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        
    
    else:
        st.info("👆 Please select a song or enter features above to start prediction")
 
    st.markdown("---")
    st.caption("💡 Powered by XGBoost | SHAP Explainability")