import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# 1. تحميل النموذج المحفوظ
try:
    model = joblib.load('purchase_model.pkl')
except:
    st.error("تنبيه: تأكد من وجود ملف purchase_model.pkl في نفس المجلد")

# إعدادات الصفحة
st.set_page_config(page_title="نظام التنبؤ بسلوك المشتري", layout="centered")

# كود CSS لضبط الاتجاه وتنسيق الواجهة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, .main, .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Tajawal', sans-serif;
        /* تثبيت مكان خط التبويبات النشط ومنع القفزة */
    div[data-baseweb="tab-highlight"] {
        right: 0 !important;
        left: auto !important;
    }
    
    .stMarkdown, .stHeader, .stSelectbox, .stNumberInput, .stRadio, .stTabs {
        direction: rtl;
        text-align: right;
    }

    /* === إصلاح مشكلة السلايدر === */
    .stSlider {
        direction: rtl;
        text-align: right;
    }
    div[data-baseweb="slider"] {
        direction: ltr !important; 
    }

    label {
        font-weight: bold !important;
        font-size: 1.1em !important;
        margin-bottom: 2px !important;
    }

    /* تنسيق أزرار التحليل والتحميل */
    .stButton>button, .stDownloadButton>button {
        width: 100%;
        font-family: 'Tajawal', sans-serif;
        background-color: #4CAF50;
        color: white;
        height: 3em;
        font-size: 1.2em;
        margin-top: 15px;
        border: none !important;
        border-radius: 5px;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #388E3C;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- الواجهة الرئيسية ---
st.markdown("<h1 style='text-align: center;'>نظام التنبؤ بسلوك المشتري</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>اختر طريقة الإدخال المناسبة لتحليل احتمالية الشراء</p>", unsafe_allow_html=True)

st.divider()

# --- تقسيم الواجهة لتبويبات (Tabs) ---
tab1, tab2 = st.tabs(["إدخال يدوي (عميل واحد)", "تحليل ملف (عملاء متعددين)"])

# ==========================================
# التبويب الأول: الإدخال اليدوي 
# ==========================================
with tab1:
    col1, col2 = st.columns(2, gap="large")

    with col1:
        age = st.number_input("العمر", 18, 80, 30)
        st.caption("عمر المشتري بالسنوات.")
        
        income = st.number_input("الدخل السنوي ($)", 10000, 200000, 50000)
        st.caption("الدخل السنوي للعميل مقدراً بالدولار.")
        
        time_spent = st.slider("الوقت المستغرق على الموقع (بالدقائق)", 1, 60, 10)
        st.caption("الوقت الذي قضاه الزائر على الموقع.")
        
        purchases = st.number_input("عدد المشتريات السابقة", 0, 50, 2)
        st.caption("إجمالي العمليات الشرائية السابقة.")

    with col2:
        gender_input = st.selectbox("النوع", options=[("ذكر", 0), ("أنثى", 1)], format_func=lambda x: x[0])
        st.caption("(0: ذكر، 1: أنثى)")
        
        category_input = st.selectbox("فئة المنتج المهتم به", 
                                      options=[("إلكترونيات", 0), ("ملابس", 1), ("أدوات منزلية", 2), ("تجميل", 3), ("رياضة", 4)], 
                                      format_func=lambda x: x[0])
        st.caption("(0: إلكترونيات، 1: ملابس، 2: منزلية، 3: تجميل، 4: رياضة)")
        
        loyalty_input = st.radio("مشترك في برنامج الولاء؟", options=[("لا", 0), ("نعم", 1)], format_func=lambda x: x[0])
        st.caption("0 (غير مشترك)، 1 (مشترك).")
        
        discounts = st.slider("عدد الخصومات المستخدمة سابقا", 0, 5, 1)
        st.caption("عدد الكوبونات أو العروض (النطاق: 0-5).")

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        single_predict_btn = st.button("تحليل السلوك واتخاذ قرار", key="single_predict", use_container_width=True)

    if single_predict_btn:
        features = [[age, gender_input[1], income, purchases, category_input[1], time_spent, loyalty_input[1], discounts]]
        prediction = model.predict(features)
        
        st.divider()
        if prediction[0] == 1:
            st.success("النتيجة: هذا العميل لديه احتمالية عالية للشراء! (1)")
            st.info("اقتراح تسويقي: أظهر له عرضاً محدوداً الآن لضمان التحويل.")
        else:
            st.warning("النتيجة: من المتوقع عدم إتمام عملية الشراء (0)")
            st.info("اقتراح تسويقي: العميل لا يزال يتصفح، ركز على تحسين تجربة التصفح بدون إزعاجه.")

# ==========================================
# التبويب الثاني: رفع وتحليل ملف (النسخة الصارمة للتنظيف)
# ==========================================
with tab2:
    st.markdown("<h3 style='text-align: right;'>تحليل بيانات العملاء دفعة واحدة</h3>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: right;'>قم برفع ملف (CSV أو Excel) يحتوي على بيانات العملاء للحصول على التنبؤات والرسومات البيانية فوراً.</p>", unsafe_allow_html=True)
    
    st.info("""
    تنبيه: يجب أن يحتوي الملف على الأعمدة التالية بالترتيب:
    Age, Gender, AnnualIncome, NumberOfPurchases, ProductCategory, TimeSpentOnWebsite, LoyaltyProgram, DiscountsAvailed
    علماً بأنه سوف يتم معالجة الملف لتهيئته وضمان قابليته للمعالجة بنجاح.
    """)
    
    # 1. خيار الرفع من الجهاز
    uploaded_file = st.file_uploader("اختر ملف البيانات من جهازك", type=['csv', 'xlsx'])
    
    # 2. زر توليد الملف التجريبي
    sample_data = pd.DataFrame({
        'Age': np.random.randint(18, 80, 1000),
        'Gender': np.random.choice([0, 1], 1000),
        'AnnualIncome': np.random.randint(10000, 200000, 1000),
        'NumberOfPurchases': np.random.randint(0, 50, 1000),
        'ProductCategory': np.random.choice([0, 1, 2, 3, 4], 1000),
        'TimeSpentOnWebsite': np.random.randint(1, 60, 1000),
        'LoyaltyProgram': np.random.choice([0, 1], 1000),
        'DiscountsAvailed': np.random.randint(0, 6, 1000)
    })
    sample_csv = sample_data.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="تحميل ملف بيانات تجريبي لاختبار النظام (1000 عميل)",
        data=sample_csv,
        file_name='sample_test_data.csv',
        mime='text/csv',
        use_container_width=True
    )
    
    st.divider()

    # 3. خيار التحميل من ملفات GitHub المحفوظة
    st.markdown("<p style='text-align: right; font-weight: bold;'>أو اختر ملفاً جاهزاً من المستودع:</p>", unsafe_allow_html=True)
    
    # قائمة بالملفات الموجودة في جيت هاب بناءً على الصورة
    github_files = {
        "اختر ملفاً...": None,
        "بيانات العملاء (customer_purchase_data)": "customer_purchase_data.csv",
        "بيانات العملاء الجاهزة (ready_customerData)": "ready_customerData.csv"
    }
    
    selected_github_file = st.selectbox("الملفات المتاحة في النظام:", options=list(github_files.keys()))

    # --- تحديد مصدر البيانات (من الرفع أو من جيت هاب) ---
    df = None
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
    elif github_files[selected_github_file] is not None:
        file_path = github_files[selected_github_file]
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        except Exception as e:
            st.error(f"لم يتم العثور على الملف '{file_path}' في المستودع. تأكد من رفعه إلى GitHub بجانب ملف app.py")

    # --- استكمال المعالجة والتحليل إذا تم العثور على بيانات ---
    if df is not None:
        try:
            # ---------------------------------------------------------
            # دالة المعالجة والتنظيف التلقائي
            # ---------------------------------------------------------
            def clean_and_prepare_data(data):
                data.columns = data.columns.str.strip()
                if 'Gender' in data.columns:
                    data['Gender'] = data['Gender'].astype(str).str.strip().str.lower()
                    gender_map = {'male': 0, 'female': 1, 'ذكر': 0, 'أنثى': 1, '0': 0, '1': 1, '0.0': 0, '1.0': 1}
                    data['Gender'] = data['Gender'].map(gender_map).fillna(0).astype(int)
                if 'ProductCategory' in data.columns:
                    data['ProductCategory'] = data['ProductCategory'].astype(str).str.strip().str.lower()
                    cat_map = {
                        'electronics': 0, 'إلكترونيات': 0,
                        'fashion': 1, 'clothing': 1, 'ملابس': 1,
                        'furniture': 2, 'kitchen': 2, 'home goods': 2, 'أدوات منزلية': 2,
                        'groceries': 3, 'beauty': 3, 'تجميل': 3,
                        'sports': 4, 'رياضة': 4,
                        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '0.0': 0, '1.0': 1, '2.0': 2, '3.0': 3, '4.0': 4
                    }
                    data['ProductCategory'] = data['ProductCategory'].map(cat_map).fillna(4).astype(int)
                if 'LoyaltyProgram' in data.columns:
                    data['LoyaltyProgram'] = data['LoyaltyProgram'].astype(str).str.strip().str.lower()
                    loyalty_map = {'yes': 1, 'no': 0, 'نعم': 1, 'لا': 0, '1': 1, '0': 0, '1.0': 1, '0.0': 0}
                    data['LoyaltyProgram'] = data['LoyaltyProgram'].map(loyalty_map).fillna(0).astype(int)
                data = data.fillna(0)
                return data

            df = clean_and_prepare_data(df)
            
            st.write("معاينة سريعة للبيانات بعد المعالجة التلقائية:")
            st.dataframe(df.head()) 
            
            col_bulk1, col_bulk2, col_bulk3 = st.columns([1, 2, 1])
            with col_bulk2:
                bulk_predict_btn = st.button("بدء تحليل الملف بالكامل", key="bulk_predict", use_container_width=True)

            if bulk_predict_btn:
                expected_cols = ['Age', 'Gender', 'AnnualIncome', 'NumberOfPurchases', 'ProductCategory', 'TimeSpentOnWebsite', 'LoyaltyProgram', 'DiscountsAvailed']
                missing_cols = [col for col in expected_cols if col not in df.columns]
                
                if missing_cols:
                    st.error(f"الملف المرفوع ينقصه الأعمدة التالية لكي يعمل النموذج: {', '.join(missing_cols)}")
                else:
                    with st.spinner('جاري تحليل البيانات وإنشاء الرسومات البيانية...'):
                        predictions = model.predict(df[expected_cols])
                        df['Purchase_Prediction'] = predictions
                        df['Decision'] = df['Purchase_Prediction'].apply(lambda x: 'سيشتري (1)' if x == 1 else 'لن يشتري (0)')
                        
                        st.success("تم تحليل جميع العملاء بنجاح!")
                        
                        st.markdown("<h3 style='text-align: center; margin-top: 30px;'>لوحة التحليل المرئي للبيانات</h3>", unsafe_allow_html=True)
                        st.divider()

                        col_chart1, col_chart2 = st.columns(2)

                        with col_chart1:
                            st.markdown("<p style='text-align:center; font-weight:bold;'>1. توزيع احتمالية الشراء</p>", unsafe_allow_html=True)
                            fig1, ax1 = plt.subplots(figsize=(6, 4))
                            sns.countplot(x='Purchase_Prediction', data=df, palette=['#e74c3c', '#2ecc71'], ax=ax1)
                            ax1.set_title("Purchase Probability Distribution", pad=10)
                            ax1.set_xlabel("Prediction")
                            ax1.set_ylabel("Number of Customers")
                            ax1.set_xticklabels(['No Purchase (0)', 'Purchase (1)'])
                            st.pyplot(fig1)

                        with col_chart2:
                            st.markdown("<p style='text-align:center; font-weight:bold;'>2. أهمية المتغيرات في اتخاذ القرار</p>", unsafe_allow_html=True)
                            fig2, ax2 = plt.subplots(figsize=(6, 4))
                            importances = pd.Series(model.feature_importances_, index=expected_cols).sort_values(ascending=True)
                            importances.plot(kind='barh', color='#3498db', ax=ax2)
                            ax2.set_title("Feature Importance in Decision Making", pad=10)
                            ax2.set_xlabel("Importance Score")
                            ax2.set_ylabel("Features")
                            st.pyplot(fig2)

                        st.markdown("<br><p style='text-align:center; font-weight:bold;'>3. مصفوفة الارتباط (Correlation Matrix) للبيانات المرفوعة</p>", unsafe_allow_html=True)
                        fig3, ax3 = plt.subplots(figsize=(10, 6))
                        sns.heatmap(df[expected_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5, ax=ax3)
                        ax3.set_title("Correlation Matrix", fontsize=14, pad=15)
                        st.pyplot(fig3)

                        st.divider()
                        st.write("البيانات النهائية بعد التحليل:")
                        st.dataframe(df) 
                        
                        csv = df.to_csv(index=False).encode('utf-8')
                        col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                        with col_dl2:
                            st.download_button(
                                label="تحميل النتائج كملف CSV",
                                data=csv,
                                file_name='predictions_results.csv',
                                mime='text/csv',
                                use_container_width=True
                            )
        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة البيانات. تفاصيل الخطأ: {e}")