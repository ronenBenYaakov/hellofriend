from textblob import TextBlob
from mongoModel import collection, object_id

def feelingsFetcher(chat_id):
    document = collection.find_one({"_id": object_id})
    average = 0

    for item in document["chatrooms"][f'{chat_id}']:
        blob = TextBlob(item)
        sentiment = blob.sentiment.polarity
        average += sentiment

    if len(document['chatrooms'][f'{chat_id}']) == 0:
        return 0

    average /= len(document["chatrooms"][f'{chat_id}'])
    res = (average + 2) * 2.5

    return f"{res} / 10"