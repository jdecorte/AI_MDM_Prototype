import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from src.frontend.DatasetDisplayer.DatasetDisplayerComponent import DatasetDisplayerComponent
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.cluster import KMeans

class DataExtractorInitPage:
    def __init__(self, canvas, handler):
        self.canvas = canvas
        self.handler = handler

    @st.cache_resource
    def _kmeans_cluster(_self, n_clusters, _tfidf_vectorizer_vectors):
        return KMeans(n_clusters).fit(_tfidf_vectorizer_vectors)
    
    def show(self):

        # CODE VOOR AUTOREFRESH, TO LATER
        # count = st_autorefresh(interval=2000, limit=5, key="fizzbuzzcounter")
        # # The function returns a counter for number of refreshes. This allows the
        # # ability to make special requests at different intervals based on the count
        # if count == 0:
        #     st.write("Count is zero")
        # elif count % 2 == 0:
        #     st.write(f"Count: {count} is even")
        # else:
        #     st.write(f"Count: {count}" + " is odd")

        DatasetDisplayerComponent().show(st.session_state["dataframe"])

        st.subheader("Stap 1: Selecteer een kolom waarop je wil filteren")
        chosen_column = st.selectbox("Kies een kolom", st.session_state["dataframe"].columns)

        st.subheader("Stap 2: Maak voor elke waarde een vector-representatie aan, dit kan volgens verschillende methodes:")
        st.write("Syntactische methoden: TF-IDF, Levenstein, Afiine Gap, etc;")
        st.write("Semantische methoden: Word2Vec, FastText, etc;")

        colA1, colA2, colA3 = st.columns([1, 1, 1])

        with colA1:
            chosen_method = st.selectbox("Kies een methode", ["TF-IDF", "Word2Vec"])

        with colA2:
            if chosen_method == "TF-IDF":
                # keuze tussen character ngrams of word ngrams
                chosen_ngrams = st.selectbox("Kies een ngram", ["char", "word"])
        with colA3:
            if chosen_method == "TF-IDF":
                chosen_ngram_range = st.slider("Kies een ngram range", 1, 5, (1, 5))

        tfidf_vectorizer=TfidfVectorizer(use_idf=True, analyzer = chosen_ngrams, ngram_range=chosen_ngram_range) 
        tfidf_vectorizer_vectors = tfidf_vectorizer.fit_transform(st.session_state["dataframe"][chosen_column].to_list())

        st.write("Shape van de vector(Dus de output-shape van de TF-IDF vectorizer): " + str(tfidf_vectorizer_vectors.shape))

        st.subheader("Voorbeeldje van een waarde naar zo'n vector:")
        st.write("Voor de waarde: ")
        st.write(st.session_state["dataframe"][chosen_column][1])
        st.write("Vector: ")
        st.write(str(tfidf_vectorizer_vectors[1]))

        # count how many values in the vector are not 0
        st.write("Aantal niet nul waarden: " + str(tfidf_vectorizer_vectors[0].count_nonzero()))
            

        # Cluster the vectors using K-means clustering from sklearn
        st.subheader("Stap 3: Cluster de vectors met behulp een clustering algoritme") 
        # keuze tussen verschillende clustering algoritmes
        chosen_clustering_algorithm = st.selectbox("Kies een clustering algoritme", ["K-means", "DBSCAN", "Hierarchical Clustering"])
        if chosen_clustering_algorithm == "K-means":        
            # aantal clusters
            chosen_n_clusters = st.slider("Kies het aantal clusters", 1, 500, 200)

            # Create a dataframe with the cluster labels and the values of the column
            kmeans = self._kmeans_cluster(chosen_n_clusters, tfidf_vectorizer_vectors)
            df = pd.DataFrame({'cluster': kmeans.labels_, 'value': st.session_state["dataframe"][chosen_column].to_list()})
            st.write(df)
        



        
        # st.write("Stap 3: Bereken de Similarity tussen de verschillende waarden; gebruik hiervoor de Jaccard Similarity of Cosine Similarity")
        # chosen_similarity = st.selectbox("Kies een similarity", ["Jaccard Similarity", "Cosine Similarity"])

        # if chosen_similarity == "Jaccard Similarity":
        #     pass




        # SIMILARITYMATRIX OPSTELLEN OP BASIS VAN TF-IDF (Jaccard SIM)


    def _jaccard_similarity(self,list1, list2):
        s1 = set(list1)
        s2 = set(list2)
        return float(len(s1.intersection(s2)) / len(s1.union(s2)))
    
def _code_kobe():
    pd.read_csv("XXXXX.csv", delimiter=';')
    chosen_column = "Material Description EN"
    # keuze tussen char of word
    chosen_ngrams = "char"
    # Bepaalde range van ngrams
    chosen_ngram_range = (1, 5)

    chosen_n_clusters = 200

    tfidf_vectorizer=TfidfVectorizer(use_idf=True, analyzer = chosen_ngrams, ngram_range=chosen_ngram_range) 
    tfidf_vectorizer_vectors = tfidf_vectorizer.fit_transform(st.session_state["dataframe"][chosen_column].to_list())

    print("Shape van de vector(Dus de output-shape van de TF-IDF vectorizer): " + str(tfidf_vectorizer_vectors.shape))
    print("Voorbeeldje van een waarde naar zo'n vector:")
    print("Voor de waarde: " + st.session_state["dataframe"][chosen_column][1])
    print("Vector: ")
    print(str(tfidf_vectorizer_vectors[1]))
    print("Aantal niet 0 waarden: " + str(tfidf_vectorizer_vectors[0].count_nonzero()))

    print("Cluster de vectors met behulp een clustering algoritme, bijvoorbeeld K-means")
    kmeans = KMeans(chosen_n_clusters).fit(tfidf_vectorizer_vectors)
    df = pd.DataFrame({'cluster': kmeans.labels_, 'value': st.session_state["dataframe"][chosen_column].to_list()})
    df.to_csv("kobe.csv")


        



    