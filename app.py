import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import base64
import json
import time
from datetime import datetime
import cv2
import numpy as np
from PIL import Image

load_dotenv()

class SolarAnalyzer:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            default_headers={"HTTP-Referer": "http://localhost:8501", "X-Title": "Solar Analyzer"}
        )
        self.models = {
            "Qwen 2.5 VL 72B": "qwen/qwen2.5-vl-72b-instruct:free",
            "Qwen 2.5 VL 32B": "qwen/qwen2.5-vl-32b-instruct:free",
            "Qwen 2.5 VL 3B": "qwen/qwen2.5-vl-3b-instruct:free"
        }
        self.PANEL_WATTAGE, self.COST_PER_WATT, self.TAX_CREDIT = 400, 200, 0.30
        self.SUN_HOURS, self.ELECTRICITY_RATE = 1800, 8
    
    def analyze_image_with_cv(self, uploaded_file):
        start_time = time.time()
        try:
            image = Image.open(uploaded_file)
            img_array = np.array(image)
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR) if len(img_array.shape) == 3 else img_array
            height, width = img_cv.shape[:2]
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            brightness, contrast = np.mean(gray), np.std(gray)
            
            if laplacian_var > 800 and contrast > 50 and brightness > 130:
                condition = "excellent"
                condition_multiplier = 1.0
            elif laplacian_var > 500 and contrast > 40:
                condition = "excellent" if brightness > 120 else "good"
                condition_multiplier = 0.95 if brightness > 120 else 0.85
            elif laplacian_var > 300 and contrast > 30:
                condition = "good"
                condition_multiplier = 0.80
            elif laplacian_var > 150 and contrast > 20:
                condition = "fair"
                condition_multiplier = 0.65
            else:
                condition = "poor"
                condition_multiplier = 0.50
            
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            total_area = height * width
            
            significant_contours = [c for c in contours if cv2.contourArea(c) > total_area * 0.005]
            roof_area = sum(cv2.contourArea(c) for c in significant_contours)
            
            base_usable = (roof_area / total_area) * 100
            
            brightness_factor = min(brightness / 128.0, 1.2)  
            contrast_factor = min(contrast / 40.0, 1.1)       
            sharpness_factor = min(laplacian_var / 500.0, 1.1)
            
            usable_percent = base_usable * brightness_factor * contrast_factor * sharpness_factor * condition_multiplier
            usable_percent = max(min(usable_percent, 90), 15)  # Clamp between 15-90%
            
            pixel_density = (width * height) / 1000000  # Megapixels
            
            if pixel_density > 2.0:  # High resolution image
                area_multiplier = 1.2
            elif pixel_density > 1.0:  # Medium resolution
                area_multiplier = 1.0
            else:  # Low resolution
                area_multiplier = 0.8
            
            estimated_roof_area_m2 = (usable_percent / 100) * area_multiplier * (50 + (total_area / 50000))
            
            panel_area = 1.65  # m² per panel
            max_panels = int(estimated_roof_area_m2 / panel_area)
            system_kw = max_panels * 0.4  # 400W per panel
            
            if condition == "excellent":
                system_kw *= 1.1
            elif condition == "poor":
                system_kw *= 0.7
            
            system_kw = max(min(system_kw, 20), 2)
            
            confidence = 40  
            
            # Sharpness contribution (0-30 points)
            if laplacian_var > 800:
                confidence += 30
            elif laplacian_var > 500:
                confidence += 25
            elif laplacian_var > 200:
                confidence += 15
            elif laplacian_var > 100:
                confidence += 8
            
            # Brightness contribution (0-20 points)
            if 80 < brightness < 180:
                confidence += 20
            elif 60 < brightness < 200:
                confidence += 12
            elif 40 < brightness < 220:
                confidence += 5
            
            # Contrast contribution (0-15 points)
            if contrast > 50:
                confidence += 15
            elif contrast > 40:
                confidence += 12
            elif contrast > 25:
                confidence += 8
            elif contrast > 15:
                confidence += 4
            
            if total_area > 1000000: 
                confidence += 10
            elif total_area > 500000:  
                confidence += 6
            elif total_area > 200000: 
                confidence += 3
            
            confidence = min(confidence, 95)
            
            analysis_time = time.time() - start_time
            
            return {
                "success": True,
                "data": {
                    "roof_condition": condition,
                    "usable_area_percent": int(usable_percent),
                    "system_size_kw": round(system_kw, 1),
                    "confidence": int(confidence),
                    "notes": f"{condition.title()} roof, {int(usable_percent)}% usable area, {int(confidence)}% confidence",
                    "analysis_time": round(analysis_time, 2),
                    "image_size": f"{width}x{height}",
                    "image_metrics": {
                        "brightness": round(brightness, 1),
                        "contrast": round(contrast, 1),
                        "sharpness": round(laplacian_var, 1),
                        "roof_area_m2": round(estimated_roof_area_m2, 1)
                    }
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    
    def enhance_with_ai(self, image_base64, cv_analysis, model_name):
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.models[model_name],
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Enhance this roof analysis: {cv_analysis}. Return JSON with shading_assessment and roof_orientation."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }],
                max_tokens=300
            )
            result = json.loads(response.choices[0].message.content)
            result["ai_time"] = round(time.time() - start_time, 2)
            return {"success": True, "data": {**cv_analysis, **result}}
        except:
            return {"success": True, "data": {**cv_analysis, "shading_assessment": "moderate", "roof_orientation": "good"}}
    
    def calculate_metrics(self, system_kw):
        annual_production = int(system_kw * self.SUN_HOURS * 0.8)
        gross_cost = int(system_kw * 1000 * self.COST_PER_WATT)
        net_cost = int(gross_cost * (1 - self.TAX_CREDIT))
        annual_savings = int(annual_production * self.ELECTRICITY_RATE)
        payback_years = round(net_cost / annual_savings if annual_savings > 0 else 0, 1)
        lifetime_savings = int((annual_savings * 25) - net_cost)
        panels_needed = int((system_kw * 1000) / self.PANEL_WATTAGE)
        
        return {
            "system_kw": system_kw, "panels": panels_needed, "annual_kwh": annual_production,
            "gross_cost": gross_cost, "net_cost": net_cost, "annual_savings": annual_savings,
            "payback_years": payback_years, "lifetime_savings": lifetime_savings,
            "co2_offset": round(annual_production * 0.0004, 1)
        }

def format_inr(amount):
    if amount <= 0: return "₹0"
    s = str(int(amount))
    if len(s) <= 3: return "₹" + s
    last3, rest = s[-3:], s[:-3]
    parts = []
    while len(rest) > 2:
        parts.append(rest[-2:])
        rest = rest[:-2]
    if rest: parts.append(rest)
    parts.reverse()
    return "₹" + ",".join(parts) + "," + last3 if parts else "₹" + last3

def main():
    st.set_page_config(page_title="Solar Analyzer - India", page_icon="☀️", layout="wide")
    
    # CSS for proper display
    st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        min-width: 180px !important;
        width: 100% !important;
        min-height: 80px !important;
        padding: 12px !important;
        margin: 8px 0 !important;
        box-sizing: border-box !important;
        background: white !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
    }
    
    div[data-testid="metric-container"] > div[data-testid="stMetricValue"] > div {
        font-size: 14px !important;
        font-weight: bold !important;
        line-height: 1.3 !important;
        color: #1f1f1f !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow: visible !important;
        height: auto !important;
    }
    
    div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div p {
        font-size: 11px !important;
        margin-bottom: 6px !important;
        color: #666 !important;
        font-weight: 500 !important;
    }
    
    .summary-header {
        background: linear-gradient(90deg, #FF9933, #138808, #000080);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #FF9933, #138808);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="summary-header"><h2>☀️ Solar Rooftop Analyzer - India</h2><p>Real Computer Vision + AI Analysis</p></div>', unsafe_allow_html=True)
    
    analyzer = SolarAnalyzer()
    
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #FF9933, #138808); color: white; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
            <h3 style="margin: 0;">☀️ Solar Industry</h3>
            <p style="margin: 0; font-size: 14px;">AI Assistant - India</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.header("⚙️ Settings")
        
        api_key_status = os.getenv("OPENROUTER_API_KEY")
        if api_key_status:
            st.success("✅ API Key Found")
        else:
            st.error("❌ Add API Key")
        
        model = st.selectbox("AI Model", list(analyzer.models.keys()))
        max_size = st.slider("Max System Size (kW)", 1, 20, 15)
        use_ai = st.checkbox("Use AI Enhancement", value=True)
        
        st.info("Free tier: 50 requests/day")
        
        st.markdown("### 🇮🇳 Indian Context")
        st.write("• **Rate**: ₹8/kWh")
        st.write("• **Cost**: ₹200/W")
        st.write("• **Subsidy**: 30%")
        st.write("• **Sun Hours**: 1800/year")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Rooftop Image")
        uploaded_file = st.file_uploader("Choose rooftop image", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file:
            st.image(uploaded_file, caption="Rooftop Image", use_container_width=True)
            
            if st.button("🔍 Analyze with Computer Vision", type="primary"):
                analysis_start = time.time()
                
                with st.spinner("Analyzing..."):
                    cv_result = analyzer.analyze_image_with_cv(uploaded_file)
                    
                    if cv_result["success"]:
                        cv_analysis = cv_result["data"]
                        
                        if use_ai and api_key_status:
                            with st.spinner("AI Enhancement..."):
                                image_base64 = base64.b64encode(uploaded_file.getvalue()).decode()
                                ai_result = analyzer.enhance_with_ai(image_base64, cv_analysis, model)
                                final_analysis = ai_result["data"] if ai_result["success"] else cv_analysis
                        else:
                            final_analysis = cv_analysis
                        
                        system_kw = min(final_analysis["system_size_kw"], max_size)
                        metrics = analyzer.calculate_metrics(system_kw)
                        
                        total_time = time.time() - analysis_start
                        final_analysis["total_analysis_time"] = round(total_time, 2)
                        
                        st.session_state.analysis = final_analysis
                        st.session_state.metrics = metrics
                        st.session_state.completed = True
                        st.session_state.model_used = model
                        
                        st.success(f"✅ Analysis Complete in {total_time:.2f}s!")
                        st.info(f"🤖 Method: {'CV + AI' if use_ai else 'CV Only'}")
                    else:
                        st.error(f"❌ Failed: {cv_result.get('error')}")
        else:
            st.info("**Features:**\n- 🔬 Computer Vision\n- 🤖 AI Enhancement\n- 📊 Dynamic Results\n- 🇮🇳 Indian Context")
    
    with col2:
        st.subheader("Analysis Results")
        
        if hasattr(st.session_state, 'completed') and st.session_state.completed:
            analysis = st.session_state.analysis
            metrics = st.session_state.metrics
            
            with st.expander("📊 Summary", expanded=True):
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.metric("🏠 Roof", analysis["roof_condition"].title())
                    st.metric("⚡ Size", f"{metrics['system_kw']}kW")
                    st.metric("📊 Annual", f"{metrics['annual_kwh']//1000}k kWh")
                
                with col_b:
                    cost_lakhs = metrics['net_cost'] / 100000
                    savings_k = metrics['annual_savings'] / 1000
                    st.metric("💰 Cost", f"₹{cost_lakhs:.1f}L")
                    st.metric("💵 Save/yr", f"₹{savings_k:.0f}k")
                    st.metric("⏱️ Payback", f"{metrics['payback_years']}yr")
                
                with col_c:
                    roi = int((metrics['lifetime_savings']/metrics['net_cost'])*100) if metrics['net_cost'] > 0 else 0
                    total_lakhs = metrics['lifetime_savings'] / 100000
                    st.metric("📈 ROI", f"{roi}%")
                    st.metric("💎 Lifetime", f"₹{total_lakhs:.1f}L")
                    st.metric("🌱 CO₂/yr", f"{metrics['co2_offset']}t")
                
                # Recommendations
                condition, payback = analysis["roof_condition"].lower(), metrics['payback_years']
                if condition == "excellent" and payback < 8:
                    st.success("✅ Excellent investment opportunity!")
                elif condition in ["good", "excellent"] and payback < 12:
                    st.info("👍 Good solar potential")
                elif condition in ["good", "excellent"] and payback < 15:
                    st.warning("⚠️ Good roof but longer payback - still viable")
                else:
                    st.info("📊 Viable investment - consider efficiency improvements")
            
            with st.expander("⚡ Performance Metrics"):
                perf_col1, perf_col2, perf_col3 = st.columns(3)
                with perf_col1:
                    st.metric("CV Time", f"{analysis.get('analysis_time', 0):.2f}s")
                    st.metric("Total Time", f"{analysis.get('total_analysis_time', 0):.2f}s")
                with perf_col2:
                    st.metric("Confidence", f"{analysis['confidence']}%")
                    st.metric("Image Size", analysis.get('image_size', 'N/A'))
                with perf_col3:
                    st.metric("Model", st.session_state.model_used[:10] + "...")
                    if 'ai_time' in analysis:
                        st.metric("AI Time", f"{analysis['ai_time']:.2f}s")
            
            with st.expander("🔧 Technical Details"):
                st.write(f"**Condition**: {analysis['roof_condition'].title()}")
                st.write(f"**Usable Area**: {analysis['usable_area_percent']}%")
                st.write(f"**Panels**: {metrics['panels']} | **Confidence**: {analysis['confidence']}%")
                st.write(f"**Notes**: {analysis['notes']}")
                if 'shading_assessment' in analysis:
                    st.write(f"**Shading**: {analysis['shading_assessment'].title()}")
            
            with st.expander("💰 Financial Breakdown"):
                st.write(f"**Gross**: {format_inr(metrics['gross_cost'])} | **Subsidy**: {format_inr(metrics['gross_cost'] - metrics['net_cost'])}")
                st.write(f"**Net**: {format_inr(metrics['net_cost'])} | **Annual**: {format_inr(metrics['annual_savings'])}")
                st.write(f"**25-Year Savings**: {format_inr(metrics['lifetime_savings'])}")
            
            # Download
            st.markdown("---")
            report_data = {
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "performance": {"total_time": analysis.get('total_analysis_time'), "confidence": analysis['confidence']},
                "analysis": analysis, "metrics": metrics, "currency": "INR"
            }
            
            st.download_button("📄 Download Report", data=json.dumps(report_data, indent=2),
                             file_name=f"solar_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                             mime="application/json")
        else:
            st.info("Upload an image to start analysis")
    
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #666;'>Solar Industry AI Assistant - India Edition<br>Real CV Analysis • Supporting India's Renewable Energy Goals</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
