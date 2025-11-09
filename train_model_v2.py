import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import joblib
import os


# ---------------------------
# 🔧 Setup
# ---------------------------
st.set_page_config(page_title="SEO Domain Classifier", layout="wide")
st.title("🧠 Sistem Deteksi Domain Berbahaya")
st.markdown("Klasifikasi domain berdasarkan konten judul dan deskripsi menggunakan **SVM, Naive Bayes, dan Random Forest** dengan TF-IDF + Stemming Bahasa Indonesia.")

# ---------------------------
# 🔤 Stemming Setup
# ---------------------------
factory = StemmerFactory()
stemmer = factory.create_stemmer()

@st.cache_data
def stem_text(text):
    return stemmer.stem(text)

# ---------------------------
# 📂 Sidebar: Upload File
# ---------------------------
st.sidebar.header("📁 Upload Dataset")
uploaded_file = st.sidebar.file_uploader("Pilih file CSV", type=["csv"])
default_file = 'labeling_judol_dan_aman-26.csv'

# ---------------------------
# 🚀 Proses Training & Evaluasi
# ---------------------------
def process_and_train(file_path):
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        st.error(f"❌ Gagal membaca file: {e}")
        return None, None, None

    # Gabungkan kolom teks
    df['text'] = df['title'].fillna('') + ' ' + df['description'].fillna('')
    df = df[df['text'].str.strip() != ''].copy()

    st.write(f"📄 Jumlah data setelah filter: `{len(df)}`")

    # Terapkan stemming
    with st.spinner("🔄 Melakukan stemming Bahasa Indonesia..."):
        df['text_stemmed'] = df['text'].apply(stem_text)

    # Mapping label
    label_mapping = {'aman': 0, 'hack judol': 1, 'pornografi': 2, 'hacked': 3}
    df = df[df['label_status'].isin(label_mapping.keys())].copy()
    df['label'] = df['label_status'].map(label_mapping)

    st.write("📊 Distribusi Label:")
    st.bar_chart(df['label_status'].value_counts())

    # Split data
    X = df['text_stemmed']
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

    # =============================
    # 🔁 Perbandingan Model
    # =============================
    models = {
        "SVM (Linear)": SVC(kernel='linear', C=1.0, class_weight='balanced'),
        "Naive Bayes": MultinomialNB(),
        "Random Forest": RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
    }

    results = []

    with st.spinner("🧠 Melatih dan membandingkan semua model..."):
        for name, clf in models.items():
            pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
                ('clf', clf)
            ])
            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)

            acc = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, target_names=label_mapping.keys(), output_dict=True)
            f1_macro = report["macro avg"]["f1-score"]
            results.append({
                "Model": name,
                "Akurasi": acc,
                "F1-Score (Macro Avg)": f1_macro,
                "Pipeline": pipeline,
                "Report": report,
                "Confusion": confusion_matrix(y_test, y_pred)
            })

    # =============================
    # 📊 Tampilkan Perbandingan
    # =============================
    st.subheader("📊 Perbandingan Model")
    df_results = pd.DataFrame(results).drop(columns=["Pipeline", "Report", "Confusion"])
    st.dataframe(df_results.set_index("Model").style.format({
        "Akurasi": "{:.2%}",
        "F1-Score (Macro Avg)": "{:.2%}"
    }))

    # 📉 Grafik
    st.subheader("📉 Grafik Performa Model")
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=df_results, x="Model", y="Akurasi", color="skyblue", label="Akurasi")
    sns.barplot(data=df_results, x="Model", y="F1-Score (Macro Avg)", color="orange", label="F1-Score")
    plt.ylim(0, 1)
    plt.legend()
    plt.ylabel("Skor")
    st.pyplot(fig)

    # =============================
    # 🏆 Tampilkan Model Terbaik
    # =============================
    best_model = max(results, key=lambda x: x["F1-Score (Macro Avg)"])
    st.success(f"🏆 **Model terbaik berdasarkan F1-Score Macro:** {best_model['Model']} ({best_model['F1-Score (Macro Avg)']:.2%})")

    # Laporan Klasifikasi
    st.subheader(f"📈 Laporan Klasifikasi: {best_model['Model']}")
    st.dataframe(pd.DataFrame(best_model["Report"]).transpose().round(2))

    # Confusion Matrix
    st.subheader("🧩 Confusion Matrix")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(best_model["Confusion"], annot=True, fmt="d", cmap="Blues",
                xticklabels=label_mapping.keys(),
                yticklabels=label_mapping.keys())
    plt.xlabel("Prediksi")
    plt.ylabel("Aktual")
    st.pyplot(fig)

    # Simpan model
    model_data = {
        'model': best_model["Pipeline"],
        'label_mapping': label_mapping,
        'version': f"streamlit_best_{best_model['Model'].lower().replace(' ', '_')}"
    }
    model_filename = 'seo_poisoning_best_model.joblib'
    joblib.dump(model_data, model_filename)
    st.success(f"📦 Model terbaik disimpan ke file: `{model_filename}`")

    return df, best_model["Pipeline"], best_model["Akurasi"]

# ---------------------------
# ▶️ Jalankan Jika Ada File
# ---------------------------
if uploaded_file is not None:
    df, model, acc = process_and_train(uploaded_file)
elif os.path.exists(default_file):
    st.info(f"🔎 Tidak ada file di-upload, menggunakan file default: `{default_file}`")
    df, model, acc = process_and_train(default_file)
else:
    st.warning("⚠️ Upload file CSV berisi kolom `title`, `description`, dan `label_status` untuk mulai.")
