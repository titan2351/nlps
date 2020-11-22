import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def get_vader_sentiment_score(analyser: SentimentIntensityAnalyzer, sentence:str):
    score = analyser.polarity_scores(sentence)
    return score['compound']

def get_sentiment(df: pd.DataFrame, col: str):
    analyser = SentimentIntensityAnalyzer()
    df['score'] = df[col].apply(lambda x: get_vader_sentiment_score(analyser, str(x)))
    return df

