import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

@st.cache_data
def load_data():
    return pd.read_csv("anime_2020_2025_clustered.csv")

df = load_data()
df["genres_list"] = df["genres"].apply(lambda x: x.split(", ") if isinstance(x, str) else [])
df["studio_list"] = df["studios"].apply(lambda x: x.split(", ") if isinstance(x, str) else [])

st.title("Anime Trends Dashboard (2020–2025)")

tabs = st.tabs(["Genre Insights", "Studio Insights", "Anime Lookup"])

with tabs[0]:
    st.header("Genre Insights")
    
    genre_stats = []
    for _, row in df.iterrows():
        for genre in row["genres_list"]:
            genre_stats.append((genre, row["score"], row["members"]))

    genre_df = pd.DataFrame(genre_stats, columns=["genre", "score", "members"])

    avg_score = genre_df.groupby("genre")["score"].mean().sort_values(ascending=False).head(10)
    total_members = genre_df.groupby("genre")["members"].sum().sort_values(ascending=False).head(10)

    st.subheader("Top 10 Genres by Average Score")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=avg_score.values, y=avg_score.index, ax=ax, palette="crest")
    ax.set_xlabel("Average Score")
    st.pyplot(fig)

    st.subheader("👥 Top 10 Genres by Total Members")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=total_members.values, y=total_members.index, ax=ax, palette="rocket")
    ax.set_xlabel("Total Members")
    st.pyplot(fig)

with tabs[1]:
    st.header("Studio Insights")

    # Most productive studios
    all_studios = df.explode("studio_list")
    studio_counts = all_studios["studio_list"].value_counts().head(10)

    st.subheader("Top 10 Studios by Number of Anime Produced")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=studio_counts.values, y=studio_counts.index, ax=ax)
    ax.set_xlabel("Number of Anime")
    st.pyplot(fig)

    # Highest rated studios
    studio_scores = all_studios.groupby("studio_list")["score"].mean().sort_values(ascending=False).head(10)

    st.subheader("Top 10 Studios by Average Score")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=studio_scores.values, y=studio_scores.index, ax=ax)
    ax.set_xlabel("Average Score")
    st.pyplot(fig)

with tabs[2]:
    st.header("Search Anime Details")

    anime_name = st.text_input("Enter an anime title:")
    if anime_name:
        result = df[df["title"].str.contains(anime_name, case=False, na=False)]
        if not result.empty:
            for _, row in result.iterrows():
                st.subheader(row["title"])
                st.markdown(f"**Score**: {row['score']}  |  **Members**: {row['members']}")
                st.markdown(f"**Genres**: {row['genres']}")
                st.markdown(f"**Studio(s)**: {row['studios']}")
                st.markdown(f"**Episodes**: {row['episodes']}  |  **Type**: {row['type']}")
                st.markdown(f"**Aired**: {row['aired_from']} to {row['aired_to']}")
                st.divider()
        else:
            st.warning("No anime found with that title.")
