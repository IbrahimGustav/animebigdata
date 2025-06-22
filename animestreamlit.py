import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Anime Trends Dashboard", layout="wide")
st.title("Anime Trends (2020–2025)")

data = pd.read_csv("anime_2020_2025.csv")

required_cols = ["score", "members", "episodes", "aired_from"]
existing_cols = [col for col in required_cols if col in data.columns]
if existing_cols:
    data = data.dropna(subset=existing_cols)

data = data[(data["score"] > 0) & (data["members"] > 0) & (data["episodes"] > 0)]
data["score"] = data["score"].astype(float)
data["members"] = data["members"].astype(int)
data["episodes"] = data["episodes"].astype(int)
data["aired_from"] = pd.to_datetime(data["aired_from"], errors="coerce")
data["year"] = data["aired_from"].dt.year
data["month"] = data["aired_from"].dt.month
data["genres_list"] = data["genres"].fillna("").apply(lambda x: x.split(", ") if x else [])

years = sorted(data["year"].dropna().unique())
genres = sorted(set(g for sublist in data["genres_list"] for g in sublist if g))
selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)
selected_genres = st.sidebar.multiselect("Select Genre(s)", genres, default=genres[:5] if genres else [])
score_min, score_max = st.sidebar.slider("Score Range", 0, 10, (0, 10), 1)

filtered = data[data["year"].isin(selected_years)]
if selected_genres:
    filtered = filtered[filtered["genres_list"].apply(lambda gl: any(g in gl for g in selected_genres))]
filtered = filtered[(filtered["score"] >= score_min) & (filtered["score"] <= score_max)]

st.subheader("Score vs Popularity (Members Count)")
fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=filtered, x="score", y="members", alpha=0.6, ax=ax1)
ax1.set_xticks(range(0, 11))
ax1.set_xlabel("Score")
ax1.set_ylabel("Members Count")
st.pyplot(fig1)

st.subheader("Score Distribution")
fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.histplot(filtered["score"], bins=20, kde=True, ax=ax2)
ax2.set_xticks(range(0, 11))
ax2.set_xlabel("Score")
ax2.set_ylabel("Count")
st.pyplot(fig2)

st.subheader("Members Trend Over Years")
members_trend = filtered.groupby("year")["members"].sum().reset_index()
fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.lineplot(data=members_trend, x="year", y="members", marker="o", ax=ax3)
ax3.set_xlabel("Year")
ax3.set_ylabel("Total Members")
st.pyplot(fig3)

st.subheader("Top Genres per Year")
genre_years = []
for _, row in filtered.iterrows():
    for g in row["genres_list"]:
        genre_years.append((row["year"], g))
genre_df = pd.DataFrame(genre_years, columns=["year", "genre"])
top_genres = genre_df["genre"].value_counts().head(10).index
filtered_genre = genre_df[genre_df["genre"].isin(top_genres)]
fig4, ax4 = plt.subplots(figsize=(12, 6))
sns.countplot(data=filtered_genre, x="year", hue="genre", ax=ax4)
ax4.set_title("Top Genre Frequencies per Year (2020–2025)")
ax4.set_xlabel("Year")
ax4.set_ylabel("Count")
ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
st.pyplot(fig4)

st.subheader("Top 20 Highest Rated Anime")
top_anime = filtered.sort_values(by="score", ascending=False).dropna(subset=["title", "score"]).head(20)
st.dataframe(top_anime[["title", "score", "members", "year"]].reset_index(drop=True))

st.subheader("K-means Clustering: Score vs Members")
try:
    clustered = pd.read_csv("anime_2020_2025_clustered.csv")
    clustered = clustered.dropna(subset=["score", "members", "prediction"])
    clustered["score"] = clustered["score"].astype(float)
    clustered["members"] = clustered["members"].astype(int)
    clustered["prediction"] = clustered["prediction"].astype(int)
    figc, axc = plt.subplots(figsize=(10, 6))
    scatter = axc.scatter(
        clustered["score"],
        clustered["members"],
        c=clustered["prediction"],
        cmap="tab10",
        alpha=0.7,
        edgecolor="k"
    )
    legend1 = axc.legend(*scatter.legend_elements(), title="Cluster")
    axc.add_artist(legend1)
    axc.set_xlabel("Score")
    axc.set_ylabel("Members")
    axc.set_title("K-means Clusters (Score vs Members)")
    st.pyplot(figc)
except Exception as e:
    st.warning(f"Could not load or plot clustering results: {e}")

st.sidebar.title("Anime Search")
search_option = st.sidebar.selectbox(
    "Search by:",
    ["Anime Title", "Studio", "Genre"]
)

if search_option == "Anime Title":
    anime_titles = sorted(data["title"].dropna().unique()) if "title" in data.columns else []
    selected_title = st.sidebar.selectbox("Select Anime Title", anime_titles)
    if selected_title:
        st.subheader(f"Stats for: {selected_title}")
        anime_stats = data[data["title"] == selected_title]
        st.dataframe(anime_stats)

if search_option == "Studio":
    studios = sorted(set(s for sublist in data["studios"].fillna("").apply(lambda x: x.split(", ") if x else []) for s in sublist if s)) if "studios" in data.columns else []
    selected_studio = st.sidebar.selectbox("Select Studio", studios)
    if selected_studio:
        st.subheader(f"Anime produced by: {selected_studio}")
        studio_anime = data[data["studios"].fillna("").apply(lambda x: selected_studio in x)]
        st.dataframe(studio_anime[[c for c in ["title", "score", "members", "year", "genres"] if c in studio_anime.columns]])

if search_option == "Genre":
    all_genres = sorted(set(g for sublist in data["genres_list"] for g in sublist if g))
    selected_genre = st.sidebar.selectbox("Select Genre", all_genres)
    if selected_genre:
        st.subheader(f"Anime in Genre: {selected_genre}")
        genre_anime = data[data["genres_list"].apply(lambda gl: selected_genre in gl)]
        st.dataframe(genre_anime[[c for c in ["title", "score", "members", "year", "studios"] if c in genre_anime.columns]])
