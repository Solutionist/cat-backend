import html
import re
import string

from nltk import word_tokenize

try:
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words("english"))
except LookupError:
    import nltk
    nltk.download("stopwords", quite=True)
    stop_words = set(stopwords.words("english"))

__emoji_pattern = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"
    u"(\ud83c[\udf00-\uffff])|"
    u"(\ud83d[\u0000-\uddff])|"
    u"(\ud83d[\ude80-\udeff])|"
    u"(\ud83c[\udde0-\uddff])"
    "+", flags=re.UNICODE)
__emoticons_happy = {':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}', ':^)', ':-D', ':D',
                     '8-D',
                     '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D', '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*',
                     '>:P',
                     ':-P', ':P', 'X-P', 'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)', '<3'}
__emoticons_sad = {':L', ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<', ':-[', ':-<', '=\\', '=/',
                   '>:(', ':(', '>.<', ":'-(", ":'(", ':\\', ':-c', ':c', ':{', '>:\\', ';('}
__emoticons = __emoticons_happy.union(__emoticons_sad)
__hashtag = r'#\S+'
__email = r'[\w\d\._-]+@\w+(\.\w+){1,3}'
__website = r'http\S+|www\.\w+(\.\w+){1,3}'
__retweet = r'RT\s@\S+'
__mention = r'@[\w\d]+'
__punctual = r'[_\+-\.,!\?#$%^&*();\\/|<>"\':]+'
__weird = r'�+😌'
__newline = r'\n'
__spaces = r'\s{2,}'
__digits = r'\d+'
__combined_patterns = r'|'.join(
    (__hashtag, __email, __website, __retweet, __mention, __punctual, __weird, __newline, __digits))


def prep_for_translation(text):
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = html.unescape(text)
    text = re.sub(__mention, "", text)
    text = re.sub(__website, "", text)
    text = re.sub(__email, "", text)
    text = re.sub(__hashtag, "", text)
    text = re.sub(__spaces, "", text)
    text = __emoji_pattern.sub(r'', text)
    return text


def prep_for_sentiment(text):
    text = re.sub(r':', '', text)
    text = re.sub(r'‚Ä¶', '', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(__combined_patterns, ' ', text)
    text = re.sub(__spaces, ' ', text)
    text = text.strip()
    tokens = word_tokenize(text)
    filtered_tweet = []
    for w in tokens:
        if w not in __emoticons and w not in string.punctuation:
            filtered_tweet.append(w)
    return ' '.join(filtered_tweet)
