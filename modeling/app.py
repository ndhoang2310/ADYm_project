"""
=============================================================================
 app.py  –  Vietnam IT Salary Market Dashboard (Modern UI)
 Đồ án: Phân tích và Dự đoán Mức lương Thị trường Việc làm IT Việt Nam
 Framework : Streamlit + Plotly Express
=============================================================================
"""

import ast
import pandas as pd
import plotly.express as px
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# 0. PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Vietnam IT Salary Dashboard",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. MODERN GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ═══════════════════════════════════════════════════════════
       DARK GLASS THEME – Pure black + prismatic accents
       ═══════════════════════════════════════════════════════════ */
    .stApp {
        background-color: #000000;
    }

    /* Subtle prismatic light streak – decorative top glow */
    .stApp::before {
        content: '';
        position: fixed;
        top: -40%; right: -20%;
        width: 80vw; height: 80vh;
        background: radial-gradient(ellipse at center,
            rgba(56, 189, 248, 0.04) 0%,
            rgba(129, 140, 248, 0.02) 40%,
            transparent 70%);
        pointer-events: none;
        z-index: 0;
    }

    /* ── Sidebar – dark glass panel ───────────────────────── */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(30px) saturate(120%);
        -webkit-backdrop-filter: blur(30px) saturate(120%);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    [data-testid="stSidebar"] * {
        color: rgba(255, 255, 255, 0.80) !important;
    }

    /* ── Typography ────────────────────────────────────────── */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em;
    }
    p, span, label {
        color: rgba(255, 255, 255, 0.55) !important;
    }

    /* ── Metric Cards – dark glass ────────────────────────── */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.40);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        border-color: rgba(255, 255, 255, 0.12);
    }
    [data-testid="stMetricLabel"] p {
        font-size: 12px;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.40) !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }
    [data-testid="stMetricValue"] {
        font-size: 34px;
        font-weight: 800;
        color: #FFFFFF !important;
    }

    /* ── Plotly Chart Container – glass panel ──────────────── */
    [data-testid="stPlotlyChart"] {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.40);
    }

    /* ── Section Title ────────────────────────────────────── */
    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.90) !important;
        margin: 32px 0 16px 0;
        display: flex;
        align-items: center;
        gap: 10px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .section-title::before {
        content: '';
        display: inline-block;
        width: 4px;
        height: 20px;
        background: linear-gradient(180deg, #818CF8, #06B6D4);
        border-radius: 4px;
        box-shadow: 0 0 10px rgba(129, 140, 248, 0.4);
    }

    /* ── Insight Box ──────────────────────────────────────── */
    .insight-box {
        background: rgba(255, 255, 255, 0.03);
        border-left: 2px solid rgba(129, 140, 248, 0.4);
        border-radius: 0 12px 12px 0;
        padding: 14px 20px;
        font-size: 13px;
        color: rgba(255, 255, 255, 0.60) !important;
        margin-top: 12px;
        line-height: 1.7;
    }
    .insight-box b {
        color: rgba(255, 255, 255, 0.85) !important;
    }

    /* ── CTA Button – glass with prismatic edge ──────────── */
    .stButton > button {
        background: rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        border-radius: 14px !important;
        padding: 16px 32px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.30) !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.10) !important;
        border-color: rgba(129, 140, 248, 0.40) !important;
        box-shadow: 0 8px 32px rgba(129, 140, 248, 0.15),
                    0 0 60px rgba(56, 189, 248, 0.06) !important;
        transform: translateY(-2px) !important;
    }
    .stButton > button:active {
        transform: translateY(1px) scale(0.99) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.30) !important;
    }
    .stButton > button div, .stButton > button p, .stButton > button span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 0.08em !important;
    }

    /* ── Inputs & Selects – dark glass controls ───────────── */
    .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.25) !important;
        transition: all 0.3s ease;
    }
    .stSelectbox div[data-baseweb="select"]:hover, .stMultiSelect div[data-baseweb="select"]:hover {
        border-color: rgba(255, 255, 255, 0.15) !important;
        transform: translateY(-1px);
    }
    div[data-baseweb="select"] {
        color: rgba(255, 255, 255, 0.80) !important;
        font-weight: 600 !important;
    }

    /* ── Slider ────────────────────────────────────────────── */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 0 12px rgba(255, 255, 255, 0.20),
                    0 2px 6px rgba(0, 0, 0, 0.4) !important;
    }

    /* ── Multiselect Tags ─────────────────────────────────── */
    .stMultiSelect span[data-baseweb="tag"] {
        background: rgba(255, 255, 255, 0.08) !important;
        color: rgba(255, 255, 255, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stMultiSelect span[data-baseweb="tag"] span {
        color: rgba(255, 255, 255, 0.85) !important;
    }
    .stMultiSelect span[data-baseweb="tag"] svg {
        fill: rgba(255, 255, 255, 0.50) !important;
    }

    /* ── Prediction Result Card – premium glass ───────────── */
    .predict-result {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 48px 40px;
        text-align: center;
        margin-top: 24px;
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.50);
        position: relative;
        overflow: hidden;
    }
    .predict-result::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, #818CF8, #06B6D4, #34D399, transparent);
        opacity: 0.7;
    }
    .predict-result h2 {
        font-size: 52px;
        margin: 12px 0;
        font-weight: 800;
        color: #FFFFFF !important;
        text-shadow: 0 0 40px rgba(129, 140, 248, 0.25);
    }
    .predict-result p {
        font-size: 15px;
        color: rgba(255, 255, 255, 0.50) !important;
        margin: 4px 0;
    }

    /* ── Tabs – minimal dark strip ─────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        color: rgba(255, 255, 255, 0.45) !important;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.04);
        color: rgba(255, 255, 255, 0.80) !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #FFFFFF !important;
        border-bottom: 2px solid rgba(129, 140, 248, 0.6) !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* ── Scrollbar ─────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.15);
    }

    /* ── Checkbox ──────────────────────────────────────────── */
    .stCheckbox label span {
        color: rgba(255, 255, 255, 0.65) !important;
    }

    /* ── Hide Streamlit chrome ─────────────────────────────── */
    header { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. DATA LOADING & CACHING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data(path: str = "D:/học/ADYm/data/05_final_dataset.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    return df

@st.cache_data
def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def parse_list_col(val):
        if isinstance(val, list): return [str(v).strip() for v in val]
        if isinstance(val, str):
            val = val.strip()
            if val.startswith("["):
                try: return [str(v).strip() for v in ast.literal_eval(val)]
                except Exception: pass
            return [v.strip() for v in val.split(",") if v.strip()]
        return []

    df["tech_list"]  = df["tech_stack"].apply(parse_list_col)
    df["loc_list"]   = df["location"].apply(parse_list_col)

    main_cities = {"Hà Nội", "Hồ Chí Minh", "Đà Nẵng"}
    def first_main_city(locs):
        for loc in locs:
            if loc in main_cities: return loc
        if locs: return locs[0]
        return "Khác"

    df["location_label"] = df["loc_list"].apply(first_main_city)

    level_map = {
        0.0: "Intern", 1.0: "Fresher", 2.0: "Junior",
        3.0: "Middle", 4.0: "Senior", 5.0: "Manager/Exec",
    }
    df["level_label"] = df["job_level"].map(level_map).fillna("Unknown")

    return df

# Xử lý upload/đọc file
try:
    raw_df = load_data("D:/học/ADYm/data/05_final_dataset.csv")
except FileNotFoundError:
    uploaded = st.sidebar.file_uploader("📂 Tải lên tệp CSV", type=["csv"])
    if uploaded is None:
        st.info("👋 Vui lòng tải lên tệp ở Sidebar để bắt đầu.")
        st.stop()
    raw_df = pd.read_csv(uploaded)

df = preprocess(raw_df)
df_salary = df.dropna(subset=["salary_avg"]).copy()
df_salary = df_salary[df_salary["salary_avg"] <= 150]

# ─────────────────────────────────────────────────────────────────────────────
# 3. SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 👨‍💻 Vietnam IT Salary")
    st.caption("Dữ liệu cập nhật từ TopCV & ITviec")
    st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# 4. HELPER – MODERN PLOTLY THEME
# ─────────────────────────────────────────────────────────────────────────────
COLOR_PALETTE = ["#3B82F6", "#10B981", "#F59E0B", "#6366F1", "#EC4899", "#8B5CF6"]

def styled_fig(fig, height: int = 400):
    fig.update_layout(
        template="simple_white",
        height=height,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="Inter, sans-serif", size=13, color="rgba(200,215,240,0.85)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color="rgba(200,215,240,0.85)")
        ),
        title_text="",
        hoverlabel=dict(
            bgcolor="rgba(30,30,60,0.85)",
            font_size=13,
            font_family="Inter, sans-serif",
            font_color="#E2E8F0",
            bordercolor="rgba(129,140,248,0.4)"
        ),
    )
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.08)",
        griddash="dash", zeroline=False,
        color="rgba(200,215,240,0.85)",
        tickfont=dict(color="rgba(200,215,240,0.75)"),
        title_font=dict(color="rgba(200,215,240,0.85)", size=14, family="Inter, sans-serif"),
    )
    fig.update_xaxes(
        showgrid=False, zeroline=False,
        color="rgba(200,215,240,0.85)",
        tickfont=dict(color="rgba(200,215,240,0.75)"),
        title_font=dict(color="rgba(200,215,240,0.85)", size=14, family="Inter, sans-serif"),
    )
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# 5. PAGE 1 – MARKET INSIGHTS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Tổng quan Thị trường", "Ước tính Lương Cá nhân"])

with tab1:

    st.markdown(
        f"""
        <div style='margin-bottom: 24px;'>
            <h1 style='font-size: 36px; margin-bottom: 8px;'>Thị trường Việc làm IT Việt Nam</h1>
            <p style='font-size: 16px; color: rgba(180,200,230,0.75);'>Phân tích chi tiết dựa trên <b style='color:#7DD3FC;'>{len(df):,}</b> tin tuyển dụng trên toàn quốc.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Metrics
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Tổng tin tuyển dụng", f"{len(df):,}")
    k2.metric("Lương Trung bình", f"{df_salary['salary_avg'].mean():.1f} Tr")
    k3.metric("Lương Trung vị", f"{df_salary['salary_avg'].median():.1f} Tr")
    k4.metric("Kinh nghiệm TB", f"{df['exp_years'].mean():.1f} Năm")

    # Row 1
    st.markdown("<div class='section-title'>Phân phối Mức lương</div>", unsafe_allow_html=True)
    fig1 = px.histogram(
        df_salary[df_salary["salary_avg"] <= 100], x="salary_avg", nbins=45,
        color_discrete_sequence=["#3B82F6"], opacity=0.8,
        labels={"salary_avg": "Mức lương (Triệu VNĐ)", "count": "Số lượng"}
    )
    fig1.update_traces(marker_line_width=0)
    st.plotly_chart(styled_fig(fig1, 350), use_container_width=True)
    st.markdown(
        "<div class='insight-box'><b>Ghi chú:</b> Phân phối tập trung chủ yếu ở mức <b>10–30 triệu VNĐ</b>. Các vị trí cấp cao tạo ra độ lệch (skew) về bên phải.</div>",
        unsafe_allow_html=True
    )

    # Row 2
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-title'>Mức lương theo Cấp bậc</div>", unsafe_allow_html=True)
        level_order = ["Intern", "Fresher", "Junior", "Middle", "Senior", "Manager/Exec"]
        
        # Loại bỏ outlier chuẩn theo định nghĩa (thực hiện trên dữ liệu trước khi vẽ)
        df_box1 = pd.DataFrame()
        for name, group in df_salary.groupby("level_label"):
            q1 = group["salary_avg"].quantile(0.25)
            q3 = group["salary_avg"].quantile(0.75)
            iqr = q3 - q1
            low_bound = q1 - 1.5 * iqr
            high_bound = q3 + 1.5 * iqr
            df_box1 = pd.concat([df_box1, group[(group["salary_avg"] >= low_bound) & (group["salary_avg"] <= high_bound)]])

        fig2 = px.box(
            df_box1, x="level_label", y="salary_avg", color="level_label",
            category_orders={"level_label": level_order}, color_discrete_sequence=COLOR_PALETTE,
            labels={"level_label": "Cấp bậc", "salary_avg": "Lương (Triệu VNĐ)"},
            points=False
        )
        
        fig2.update_layout(showlegend=False)
        fig2.update_xaxes(title="")
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    with c2:
        st.markdown("<div class='section-title'>Theo Năm Kinh nghiệm</div>", unsafe_allow_html=True)
        exp_line = df_salary[df_salary["exp_years"] <= 15].groupby("exp_years", as_index=False)["salary_avg"].mean()
        fig3 = px.line(
            exp_line, x="exp_years", y="salary_avg", markers=True,
            color_discrete_sequence=["#10B981"],
            labels={"exp_years": "Năm kinh nghiệm", "salary_avg": "Lương (Triệu VNĐ)"}
        )
        fig3.update_traces(line=dict(width=3), marker=dict(size=8))
        st.plotly_chart(styled_fig(fig3), use_container_width=True)

    # Row 3
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("<div class='section-title'>Lương theo Địa điểm</div>", unsafe_allow_html=True)
        top_locs = ["Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Khác"]
        df_loc = df_salary[df_salary["location_label"].isin(top_locs)]
        
        # Loại bỏ outlier chuẩn theo định nghĩa (thực hiện trên dữ liệu trước khi vẽ)
        df_box2 = pd.DataFrame()
        for name, group in df_loc.groupby("location_label"):
            q1 = group["salary_avg"].quantile(0.25)
            q3 = group["salary_avg"].quantile(0.75)
            iqr = q3 - q1
            low_bound = q1 - 1.5 * iqr
            high_bound = q3 + 1.5 * iqr
            df_box2 = pd.concat([df_box2, group[(group["salary_avg"] >= low_bound) & (group["salary_avg"] <= high_bound)]])

        fig4 = px.box(
            df_box2, x="location_label", y="salary_avg",
            color="location_label", color_discrete_sequence=COLOR_PALETTE,
            category_orders={"location_label": top_locs}, labels={"location_label": "Địa điểm", "salary_avg": "Lương (Triệu VNĐ)"},
            points=False
        )

        fig4.update_layout(showlegend=False)
        fig4.update_xaxes(title="")
        st.plotly_chart(styled_fig(fig4), use_container_width=True)

    with c4:
        st.markdown("<div class='section-title'>Công nghệ Săn đón nhất</div>", unsafe_allow_html=True)
        all_skills = [skill for lst in df["tech_list"] for skill in lst]
        skill_df = pd.Series(all_skills).value_counts().head(10).reset_index()
        skill_df.columns = ["Kỹ năng", "Số lượng"]
        fig6 = px.bar(
            skill_df.sort_values("Số lượng"), x="Số lượng", y="Kỹ năng", orientation="h",
            color="Số lượng", color_continuous_scale="Blues", labels={"Số lượng": "Số lượng", "Kỹ năng": "Kỹ năng"}
        )
        fig6.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title="")
        st.plotly_chart(styled_fig(fig6), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# 6. PAGE 2 – SALARY PREDICTOR
# ─────────────────────────────────────────────────────────────────────────────
with tab2:

    st.markdown(
        """
        <div style='margin-bottom: 32px;'>
            <h1 style='font-size: 36px; margin-bottom: 8px;'>Ước tính Mức lương</h1>
            <p style='font-size: 16px; color: rgba(180,200,230,0.75);'>Công cụ hỗ trợ đánh giá giá trị thị trường dựa trên hồ sơ năng lực của bạn.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Khung nhập liệu (chia làm 2 cột rõ ràng)
    with st.container():
        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("<div style='font-weight:600; color:rgba(220,230,250,0.95); margin-bottom:12px; font-size:16px;'>Chuyên môn &amp; Cấp bậc</div>", unsafe_allow_html=True)
            job_category = st.selectbox("Nhóm ngành (Job Category)", ["Business Analyst", "Frontend Developer", "Backend Developer", "Fullstack Developer", "Data & AI", "Mobile Developer", "Management/Architect", "QA/Tester", "System/DevOps/Security", "Khác"])
            level_options = {"Intern": 0.0, "Fresher": 1.0, "Junior": 2.0, "Middle": 3.0, "Senior": 4.0, "Manager / Exec": 5.0}
            job_level_label = st.selectbox("Cấp bậc (Level)", list(level_options.keys()), index=2)
            exp_years = st.slider("Số năm kinh nghiệm", 0.0, 15.0, 2.0, 0.5)
            tech_stack = st.multiselect("Tech Stack nổi bật", ["Python", "Java", "JavaScript", "SQL", "React", "Node.js", "AWS", "Docker", "C#"], default=["Python", "SQL"])

        with col2:
            st.markdown("<div style='font-weight:600; color:rgba(220,230,250,0.95); margin-bottom:12px; font-size:16px;'>Điều kiện làm việc</div>", unsafe_allow_html=True)
            location = st.selectbox("Địa điểm làm việc", ["Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Khác"])
            work_method = st.selectbox("Hình thức", ["Onsite", "Remote", "Hybrid"])
            education_level = st.selectbox("Học vấn tối đa", ["Bachelor", "College", "Unknown"])
            language_req = st.checkbox("Có khả năng sử dụng Ngoại ngữ làm việc")

    st.markdown("<br>", unsafe_allow_html=True)

    # Nút bấm dự đoán
    if st.button("Tính toán Mức lương Đề xuất", use_container_width=True):
        with st.spinner("Đang phân tích dữ liệu thị trường..."):
            import time; time.sleep(0.5)

            # --- Dummy ML Logic (Giữ nguyên thuật toán mẫu) ---
            base = {0.0: 5.0, 1.0: 9.0, 2.0: 14.0, 3.0: 22.0, 4.0: 35.0, 5.0: 52.0}.get(level_options[job_level_label], 12.0)
            exp_bonus = min(exp_years, 15) * 1.5
            cat_mult = {"Management/Architect": 1.35, "Data & AI": 1.28, "Backend Developer": 1.12, "Fullstack Developer": 1.10}.get(job_category, 1.0)
            loc_bonus = {"Hồ Chí Minh": 2.5, "Hà Nội": 1.5}.get(location, -0.5)
            wm_bonus = {"Remote": 3.0, "Hybrid": 1.5}.get(work_method, 0.0)
            lang_bonus = 2.5 if language_req else 0.0
            tech_bonus = min(len([t for t in tech_stack if t in {"Python", "AWS", "Docker", "React", "Node.js"}]) * 0.8, 5.0)
            
            salary_mid = max((base + exp_bonus + loc_bonus + wm_bonus + lang_bonus + tech_bonus) * cat_mult, 4.0)
            salary_low, salary_high = salary_mid * 0.82, salary_mid * 1.20

            # Hiển thị kết quả
            st.markdown(
                f"""
                <div class="predict-result">
                    <p>MỨC LƯƠNG ƯỚC TÍNH (VNĐ/THÁNG)</p>
                    <h2>{salary_mid:.1f} Triệu</h2>
                    <p>Khoảng lương phổ biến: <span style='color:#6EE7B7; font-weight:600;'>{salary_low:.1f}</span> — <span style='color:#6EE7B7; font-weight:600;'>{salary_high:.1f}</span></p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # So sánh thị trường
            st.markdown("<div class='section-title'>Vị thế so với Thị trường</div>", unsafe_allow_html=True)
            market_mid = df_salary["salary_avg"].median()
            comp_df = pd.DataFrame({
                "Mục": ["Đề xuất cho bạn", "Trung vị Thị trường"],
                "Lương (Tr)": [salary_mid, market_mid]
            })
            fig_comp = px.bar(
                comp_df, x="Lương (Tr)", y="Mục", orientation="h",
                text="Lương (Tr)", color="Mục",
                color_discrete_map={"Đề xuất cho bạn": "#818CF8", "Trung vị Thị trường": "rgba(200,215,240,0.35)"}
            )
            fig_comp.update_traces(texttemplate='%{text:.1f} Tr', textposition='outside', width=0.4)
            fig_comp.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
            st.plotly_chart(styled_fig(fig_comp, 200), use_container_width=True)