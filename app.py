import streamlit as st
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt


kmeans_pipeline = pickle.load(open('kmeans_pipeline.pkl', 'rb'))
X_pca = pickle.load(open('X_pca.pkl', 'rb'))

st.title('YouTube Data Clustering :thumbsup:')

st.text('Enter your YouTube video metadata:')


category_id = st.text_input('Input category_id', '1234')
topic = st.text_input('Input video topic', 'cooking, learning, travel, technology')
definition = st.select_slider('Input video definition', ['hd', 'sd'])
view_count = st.slider('Input number of views', 0, 1000000)
like_count = st.slider('Input number of likes', 0, 1000000)
comment_count = st.slider('Input number of comments', 0, 1000000)
subscriber_count = st.number_input('Input number of subscribers', 10)
total_channel_views = st.number_input('Input total views in channel ', 10)
videoCount = st.number_input('Input number of videos of channel', 10)
number_of_words_in_title = st.number_input('Input number of words in title', 10)
number_of_words_in_channel_description = st.number_input('Input number of words in channel description', 10)
number_of_tags = st.number_input('Input number of tags', 10)
duration_seconds = st.number_input('Input duration seconds', 10)
days_since_published = st.number_input('Input days since published', 10)
days_since_channel_published = st.number_input('Input days since channel published', 10)

features = np.array([category_id, topic, definition, view_count, like_count, comment_count,
                     subscriber_count, total_channel_views, videoCount, number_of_words_in_title,
                     number_of_words_in_channel_description, number_of_tags, duration_seconds, days_since_published,
                     days_since_channel_published])


def predict_and_plot(features):
    # Create a DataFrame from user inputs
    user_sample = pd.DataFrame([features],
                               columns=['category_id', 'topic', 'definition', 'view_count', 'like_count', 'comment_count',
                                        'subscriber_count', 'total_channel_views', 'videoCount', 'number_of_words_in_title',
                                        'number_of_words_in_channel_description', 'number_of_tags','duration_seconds',
                                        'days_since_published', 'days_since_channel_published'])

    # Preprocess the user sample
    preprocessed_sample = kmeans_pipeline.named_steps['preprocessor'].transform(user_sample)

    # Use the PCA from pipeline to transform the preprocessed sample to PCA components
    pca_user_sample = kmeans_pipeline.named_steps['pca'].transform(preprocessed_sample)

    # Use the pipeline to predict the cluster
    cluster = kmeans_pipeline.predict(user_sample)[0]

    # Plotting
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the entire dataset
    ax.scatter(X_pca[:, 0], X_pca[:, 1], X_pca[:, 2], alpha=0.5)

    # Plot the user's sample in the plot with a different color and larger size
    ax.scatter(pca_user_sample[0][0], pca_user_sample[0][1], pca_user_sample[0][2], color='r', s=100,
               label=f'User Sample (Cluster {cluster})')
    ax.legend()

    plt.close()
    st.pyplot(fig)

st.button('Cluster and visualize', on_click=predict_and_plot(features))



