import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

st.set_page_config(page_title="Anime Trends Dashboard", layout="wide")
st.title("Anime Trends (2020–2025)")

data_path = Path(__file__).parent / "anime_2020_2025_clustered.csv"
data = pd.read_csv(data_path)

data = data.dropna(subset=["score", "members", "episodes", "aired_from"])
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

st.subheader("Search for an Anime and View Stats")
anime_query = st.text_input("Enter anime title (partial or full):")
if anime_query:
    search_results = filtered[filtered['title'].str.contains(anime_query, case=False, na=False)]
    if not search_results.empty:
        st.write(f"Found {len(search_results)} result(s):")
        st.dataframe(search_results[["title", "score", "members", "episodes", "year", "genres", "studios"]].reset_index(drop=True))
        selected = search_results.iloc[0]
        st.markdown(f"**Title:** {selected['title']}")
        st.markdown(f"**Score:** {selected['score']}")
        st.markdown(f"**Members:** {selected['members']}")
        st.markdown(f"**Episodes:** {selected['episodes']}")
        st.markdown(f"**Year:** {selected['year']}")
        st.markdown(f"**Genres:** {selected['genres']}")
        st.markdown(f"**Studios:** {selected['studios']}")
    else:
        st.warning("No anime found matching your search.")

st.subheader("Search Anime by Genre")
genre_search = st.text_input("Enter genre (partial or full) to list anime:")
if genre_search:
    genre_results = filtered[filtered["genres"].str.contains(genre_search, case=False, na=False)]
    genrestudio_results = studio_results.sort_values(by="score", ascending=False)_results = genre_results.sort_values(by="score", ascending=False)
    if not genre_results.empty:
        st.write(f"Found {len(genre_results)} anime in genre '{genre_search}':")
        st.dataframe(genre_results[["title", "score", "members", "episodes", "year", "genres", "studios"]].reset_index(drop=True))
    else:
        st.warning(f"No anime found for genre '{genre_search}'.")

st.subheader("Search Anime by Studio")
studio_search = st.text_input("Enter studio (partial or full) to list works:")
if studio_search:
    studio_results = filtered[filtered["studios"].str.contains(studio_search, case=False, na=False)]
    studio_results = studio_results.sort_values(by="score", ascending=False)
    if not studio_results.empty:
        st.write(f"Found {len(studio_results)} anime produced by studio '{studio_search}':")
        st.dataframe(studio_results[["title", "score", "members", "episodes", "year", "genres", "studios"]].reset_index(drop=True))
    else:
        st.warning(f"No anime found for studio '{studio_search}'.")
