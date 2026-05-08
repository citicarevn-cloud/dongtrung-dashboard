import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# 1. CẤU HÌNH TRANG & GIAO DIỆN DARK MODE
st.set_page_config(page_title="Dashboard Đông Trùng Hạ Thảo", layout="wide", initial_sidebar_state="expanded")

# Thêm CSS tùy chỉnh để bo góc và làm đẹp các thẻ KPI (giống thiết kế)
st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: #262730;
        border: 1px solid #3f3f46;
        padding: 5% 10%;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="metric-container"] > div > div > div > div > p {
        color: #d97706 !important; /* Màu vàng Gold cho con số */
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. TẠO DỮ LIỆU MẪU (Mô phỏng file Google Sheets của sếp)
@st.cache_data
def get_mock_data():
    np.random.seed(42)
    dates = [datetime(2026, 5, 1) + timedelta(days=i) for i in range(31)]
    products = ['Nấm Đông trùng hạ thảo khô (15gr)', 'Nấm Đông trùng hạ thảo khô (60gr)', 
                'Bình rượu Đông trùng hạ thảo (3 lít)', 'Combo 1 (Quà tặng)', 'Nhộng Đông trùng (20 con)']
    methods = ['BANK', 'COD']
    
    data = []
    for _ in range(950): # Mô phỏng 950 đơn hàng
        date = np.random.choice(dates)
        product = np.random.choice(products, p=[0.3, 0.2, 0.15, 0.25, 0.1])
        method = np.random.choice(methods, p=[0.65, 0.35]) # 65% BANK, 35% COD
        revenue = np.random.randint(500000, 5000000)
        data.append([date, product, method, revenue, "DT" + str(np.random.randint(1000, 9999))])
        
    df = pd.DataFrame(data, columns=['Ngày', 'Sản phẩm', 'Hình thức TT', 'Thực thu', 'Mã đơn'])
    return df

df = get_mock_data()

# 3. SIDEBAR (CỘT BÊN TRÁI)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3061/3061341.png", width=100) # Logo giả định
    st.markdown("### Đông Trùng Hạ Thảo")
    st.markdown("#### Khally Dang")
    st.markdown("---")
    st.button("📊 Dashboard")
    st.button("💰 Sales")
    st.button("📦 Products")
    st.button("👥 Customers")

# 4. GIAO DIỆN CHÍNH (MAIN AREA)
st.title("Báo cáo phân tích kinh doanh")
st.markdown("Kỳ báo cáo: **Tháng 05/2026**")
st.markdown("---")

# TÍNH TOÁN CÁC CHỈ SỐ KPI
tong_doanh_thu = df['Thực thu'].sum()
tong_don = df['Mã đơn'].nunique()
aov = tong_doanh_thu / tong_don if tong_don > 0 else 0

# HÀNG 1: THẺ KPI (SCORECARDS)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Tổng doanh thu (Total Revenue)", value=f"{tong_doanh_thu:,.0f} đ", delta="15% vs tháng trước")
with col2:
    st.metric(label="Tổng số đơn hàng (Total Orders)", value=f"{tong_don:,}", delta="8%")
with col3:
    st.metric(label="Giá trị đơn trung bình (AOV)", value=f"{aov:,.0f} đ", delta="6%")
with col4:
    st.metric(label="Tỷ lệ chuyển đổi (Conversion Rate)", value="3.2%", delta="0.5%")

st.markdown("<br>", unsafe_allow_html=True)

# HÀNG 2: BIỂU ĐỒ XU HƯỚNG VÀ CƠ CẤU
col_chart1, col_chart2 = st.columns([2, 1]) # Tỷ lệ 2:1

with col_chart1:
    st.markdown("#### Xu hướng doanh số hàng ngày")
    df_trend = df.groupby('Ngày')['Thực thu'].sum().reset_index()
    # Vẽ biểu đồ Line mượt (spline) với Plotly
    fig_line = px.line(df_trend, x='Ngày', y='Thực thu', 
                       color_discrete_sequence=['#fbbf24']) # Màu vàng
    fig_line.update_traces(line_shape='spline', fill='tozeroy', fillcolor='rgba(251, 191, 36, 0.1)')
    fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#a1a1aa')
    st.plotly_chart(fig_line, use_container_width=True)

with col_chart2:
    st.markdown("#### Phương thức thanh toán")
    df_pie = df['Hình thức TT'].value_counts().reset_index()
    df_pie.columns = ['Hình thức TT', 'Số lượng']
    # Vẽ biểu đồ Donut
    fig_pie = px.pie(df_pie, values='Số lượng', names='Hình thức TT', hole=0.5,
                     color='Hình thức TT', color_discrete_map={'BANK':'#d97706', 'COD':'#b45309'})
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#a1a1aa')
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

# HÀNG 3: TOP SẢN PHẨM & INSIGHTS
col_chart3, col_chart4 = st.columns([2, 1])

with col_chart3:
    st.markdown("#### Top 5 Sản phẩm bán chạy nhất")
    df_prod = df['Sản phẩm'].value_counts().head(5).reset_index()
    df_prod.columns = ['Sản phẩm', 'Số lượng']
    # Vẽ biểu đồ Bar nằm ngang
    fig_bar = px.bar(df_prod, x='Số lượng', y='Sản phẩm', orientation='h',
                     color_discrete_sequence=['#d97706'])
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, 
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#a1a1aa')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_chart4:
    st.markdown("#### Customer Insights")
    st.info("👥 **30%**\n\nTỷ lệ khách hàng quay lại (Retention rate)")
    st.warning("💳 **1/3**\n\nTần suất mua hàng trung bình / Quý")
    st.success("🌟 **Đánh giá**\n\n98% khách hàng hài lòng về chất lượng hộp quà Combo.")