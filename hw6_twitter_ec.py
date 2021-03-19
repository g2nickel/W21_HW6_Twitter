#########################################
##### Name: Greg Nickel             #####
##### Uniqname: gnickel             #####
#########################################

from requests_oauthlib import OAuth1
import json
import requests

import secrets as secrets # file that contains your OAuth credentials

CACHE_FILENAME = "twitter_cache.json"
CACHE_DICT = {}

client_key = secrets.TWITTER_API_KEY
client_secret = secrets.TWITTER_API_SECRET
access_token = secrets.TWITTER_ACCESS_TOKEN
access_token_secret = secrets.TWITTER_ACCESS_TOKEN_SECRET

oauth = OAuth1(client_key,
            client_secret=client_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret)

def test_oauth():
    ''' Helper function that returns an HTTP 200 OK response code and a 
    representation of the requesting user if authentication was 
    successful; returns a 401 status code and an error message if 
    not. Only use this method to test if supplied user credentials are 
    valid. Not used to achieve the goal of this assignment.'''

    url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    auth = OAuth1(client_key, client_secret, access_token, access_token_secret)
    authentication_state = requests.get(url, auth=auth).json()
    return authentication_state

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params

    AUTOGRADER NOTES: To correctly test this using the autograder, use an underscore ("_") 
    to join your baseurl with the params and all the key-value pairs from params
    E.g., baseurl_key1_value1

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs

    Returns
    -------
    string
        the unique key as a string
    '''
    keystring = baseurl
    for key, val in params.items():
        keystring += f"_{key}_{val}"
    return keystring

def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs

    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    response = requests.get(baseurl,params,auth=oauth)
    return response.json()

def make_request_with_cache(baseurl, hashtag, count):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.

    AUTOGRADER NOTES: To test your use of caching in the autograder, please do the following:
    If the result is in your cache, print "fetching cached data"
    If you request a new result using make_request(), print "making new request"

    Do no include the print statements in your return statement. Just print them as appropriate.
    This, of course, does not ensure that you correctly retrieved that data from your cache, 
    but it will help us to see if you are appropriately attempting to use the cache.

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    hashtag: string
        The hashtag to search for
    count: integer
        The number of results you request from Twitter

    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    params = {
        "q" : hashtag,
        "count" : count
    }
    unique_key = construct_unique_key(baseurl,params)
    try:
        results = CACHE_DICT[unique_key]
    except KeyError:
        results = make_request(baseurl,params)
        CACHE_DICT[unique_key] = results
        save_cache(CACHE_DICT)
    return results

def key_count(dict_to_sort):
    """ Given a dictionary element, returns the value associated with count.
    used to assist in sorting
    Parameters
    ----------
    dict_to_sort: dict
        element to be sorted

    Returns
    -------
    dict_to_sort['count']: int
        element inside of dictionary to be sorted
    """
    return dict_to_sort["count"]

def find_most_common_cooccurring_hashtags(tweet_data, hashtag_to_ignore):
    ''' Finds the hashtag that most commonly co-occurs with the hashtag
    queried in make_request_with_cache().

    Parameters
    ----------
    tweet_data: dict
        Twitter data as a dictionary for a specific query
    hashtag_to_ignore: string
        the same hashtag that is queried in make_request_with_cache() 

    Returns
    -------
    most_popular_tags: list
        the top 3 hashtag that most commonly co-occurs with the hashtag 
        queried in make_request_with_cache()

    '''
    #remove # symbol from querry and make search_term lower_case
    if hashtag_to_ignore[0] == "#":
        ignore = hashtag_to_ignore.lower()[1:]
    else:
        ignore = hashtag_to_ignore.lower()

    list_of_tags = []
    # For each tweet, look at the list of hastags and add each hashtag, except the one to ignore to a list
    list_of_tweets = tweet_data["statuses"]
    for tweet in list_of_tweets:
        for tag in tweet["entities"]["hashtags"]:
            if tag["text"].lower() != ignore:
                list_of_tags.append(tag["text"].lower()) #Make all hashtags lower

    counts_of_hastags = {}
    #Loop of the list of tags, if the tag is new, add it to the dictionary
    #If the tag already is listed, increment it's count by 1.
    for tag in list_of_tags:
        if tag in counts_of_hastags.keys():
            counts_of_hastags[tag] += 1
        else:
            counts_of_hastags[tag] = 1

    list_of_tags_and_counts = []
    #Use the dictionary of tags and counts to create an easy to sort list
    for key, val in counts_of_hastags.items():
        pair = {"tag" : key, "count" : val}
        list_of_tags_and_counts.append(pair)
    list_of_tags_and_counts.sort(reverse=True,key=key_count)

    #Pull three most popular tags from sorted list. If there are less than three tags, return what is found
    most_popular_tags = []
    if len(list_of_tags_and_counts) < 3:
        words_to_return = len(list_of_tags_and_counts)
    else:
        words_to_return = 3

    for x in range(words_to_return):
        most_popular_tags.append(list_of_tags_and_counts[x]["tag"])
    return most_popular_tags

def find_most_common_appearing_words(tweet_data):
    """
    Finds the words that most commonly occurs for tweets with a hashtag
    queried in make_request_with_cache(). Ignores common English words/'stop words'
    The word 'i' was added to the list of stop words that was provided
    Ignores hashtags. For example in the tweet 'Michigan is awesome #Michigan', michigan would count once.

    Parameters
    ----------
    tweet_data: dict
        results of make_request_with_cashe()

    Returns
    -------
    top_ten_list_with_counts = list (of tuples)
        each word with it's associated word count
    '''
    """
    ignore_list = ("rt", "i", "a", "about", "above", "above", "across", "after", "afterwards", 
        "again", "against", "all", "almost", "alone", "along", "already", "also","although",
        "always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", 
        "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",
        "at", "back","be","became", "because","become","becomes", "becoming", "been",
        "before", "beforehand", "behind", "being", "below", "beside", "besides", "between",
        "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant",
        "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done",
        "down", "due", "during", "each", "eg", "eight", "either", "eleven","else",
        "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone",
        "everything", "everywhere", "except", "few", "fifteen", "fify", "fill",
        "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found",
        "four", "from", "front", "full", "further", "get", "give", "go", "had", "has",
        "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein",
        "hereupon", "hers", "herself", "him", "himself", "his", "how", "however",
        "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it",
        "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd",
        "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more",
        "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely",
        "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone",
        "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once",
        "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours",
        "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put",
        "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious",
        "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty",
        "so", "some", "somehow", "someone", "something", "sometime", "sometimes",
        "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the",
        "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby",
        "therefore", "therein", "thereupon", "these", "they", "thick", "thin", "third",
        "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to",
        "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un",
        "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were",
        "what", "whatever", "when", "whence", "whenever", "where", "whereafter",
        "whereas", "whereby", "wherein", "whereupon", "wherever", "whether",
        "which", "while", "whither", "who", "whoever", "whole", "whom", "whose",
        "why", "will", "with", "within", "without", "would", "yet", "you", "your",
        "yours", "yourself", "yourselves", "the")

    list_of_all_words = []
    # For each tweet, look at the list of words. Eliminate extraneous words
    list_of_tweets = tweet_data["statuses"]
    for tweet in list_of_tweets:
        list_of_tweet_words = tweet["text"].lower().split()
        for word in list_of_tweet_words:
            if word in ignore_list:
                break
            if word[0] in ("&","#","@"): #ignore special characters, hashtags and @'s
                break
            if word[:4] == "http": #ignore web urls
                break
            if word[-1] in (",",".","?","!"): #remove punctuation
                list_of_all_words.append(word[:-1])
                break
            if word[0] == word[-1] and word[0] in ("'",'"'): #remove quotation marks around words
                list_of_all_words.append(word[1:-1])
                break
            list_of_all_words.append(word) #If it passes everything else, add the word

    counts_of_words = {}
    #Loop of the list of all words, if the word is new, add it to the dictionary
    #If the word already is listed, increment it's count by 1.
    for word in list_of_all_words:
        if word in counts_of_words.keys():
            counts_of_words[word] += 1
        else:
            counts_of_words[word] = 1

    list_of_words_and_counts = []
    #Use the dictionary of words and counts to create an easy to sort list
    for key, val in counts_of_words.items():
        pair = {"word" : key, "count" : val}
        list_of_words_and_counts.append(pair)
    list_of_words_and_counts.sort(reverse=True,key=key_count)

    #Pull ten most popular words from sorted list. If there are less than ten words,
    # return what is found.
    most_popular_words = []
    if len(list_of_words_and_counts) < 10:
        words_to_return = len(list_of_words_and_counts)
    else:
        words_to_return = 10

    for x in range(words_to_return):
        most_popular_words.append((list_of_words_and_counts[x]["word"],list_of_words_and_counts[x]["count"]))

    return most_popular_words



if __name__ == "__main__":
    if not client_key or not client_secret:
        print("You need to fill in CLIENT_KEY and CLIENT_SECRET in secret_data.py.")
        exit()
    if not access_token or not access_token_secret:
        print("You need to fill in ACCESS_TOKEN and ACCESS_TOKEN_SECRET in secret_data.py.")
        exit()

    CACHE_DICT = open_cache()
    baseurl = "https://api.twitter.com/1.1/search/tweets.json"

    search_term = input("Enter a search term or type 'Exit' to quit: ")
    while True:
        if search_term.strip().lower() == "exit":
            print("Thanks you and have a nice day")
            break
        response = make_request_with_cache(baseurl,search_term,100)
        list_of_tags = find_most_common_cooccurring_hashtags(response,search_term)
        list_of_words = find_most_common_appearing_words(response)
        if len(list_of_tags) == 0:
            print("No cooccuring hashtags were found.")
        else:
            number_to_word = ["zero","one","two","three"]
            print(f"The {number_to_word[len(list_of_tags)]} hastags that most commonly occur with #{search_term} are:")
        for x in list_of_tags:
            print(f"#{x}")

        print(f"The most common words that appear in tweets using the #{search_term} hashtag are:")
        for x in list_of_words:
            print(f"{x[0]} ({x[1]} times),", end=" ")
        print()
        search_term = input("Enter a search term or type 'Exit' to quit: ")