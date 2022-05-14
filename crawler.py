from itertools import count
from itertools import islice
import math
from pydoc import doc
import requests
import time
import csv
import os
from bs4 import BeautifulSoup
from typing import Counter
from asyncio.windows_events import NULL

report_info = []
disallowed_url_arr = []
seed_count = 0
word_count = {}
soup = None

# For indexing
indexed_words_dict = {}
document_length_dict = {}


# Check if the repository folder exists, if it doesnt make it
savePath = os.path.dirname(os.path.abspath(__file__)) + "\\repository\\"
if not os.path.exists(savePath):
    os.makedirs(savePath)

session = requests.Session()


def crawl(seed, count_seed):
    debug = True
    depth = 0
    maxDepth = 350
    visited = []

    # Check robots.txt for any restricted pages
    # Add url to the queue
    queue = []

    # Seeds
    # https://www.cpp.edu/index.shtml
    # https://ur.medeqipexp.com/
    # https://www.japscan.ws/

    domain = seed.split("/")[2]
    queue.append(seed)

    session.headers.update({'Host': domain,
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Connection': 'keep-alive',
                            'Pragma': 'no-cache',
                            'Cache-Control': 'no-cache'})

    while((depth < maxDepth) or (len(queue) == 0)):
        depth += 1
        num_outLinks = 0
        currentUrl = queue.pop(0)

        # Every 20 pages print show the depth in the console
        if(depth % 20 == 0):
            print("depth: " + str(depth) + "/" + str(maxDepth))
            # Every 100 pages show the size of the queue
            if(depth % 100 == 0):
                print("Queue length: " + str(len(queue)))

        if(debug):
            print("requesting: " + currentUrl)
        visited.append(currentUrl)

        try:
            # get the current page's html
            page = session.get(currentUrl, timeout=5)
            # save the current page's html to the repositroy folder
            completePath = os.path.normpath(savePath + str(depth) + ".html")
            with open(completePath, 'w', encoding="utf-8") as file:
                file.write(page.text)

        except requests.exceptions.Timeout:
            num_try = 0
            while(num_try < 5):
                time.sleep(5)
                page = session.get(currentUrl, timeout=25)
                if(page is not NULL):
                    break
                num_try += 1
        except requests.exceptions.TooManyRedirects:
            print('Bad url')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)


def cal_avg_docs_length():
    num_docs = len(document_length_dict.keys())
    total_word_count = 0

    for val in document_length_dict.values():
        total_word_count += val

    return (total_word_count / num_docs)


def get_ni(word):
    try:
        return len(indexed_words_dict[word].keys())
    except:
        return 0


def take(n, iterable):
    return list(islice(iterable, n))


def calculate_BMI(search_phrase_words):
    ri = 0
    R = 0
    k1 = 1.2
    k2 = float(100)
    b = 0.75
    N = len(document_length_dict.keys())    # total number of documents

    # calculate average document length
    avdl = cal_avg_docs_length()

    # get n for each term. The number of times each term appears accross all documents.
    # each list index corresponds to same index in search_phrase_words
    # documents_list is a list of sets. each set has the pages, word i appears in.
    n_list = list()
    documents_list = list()
    for word in search_phrase_words:
        try:
            n_list.append(len(indexed_words_dict[word].keys()))
            documents_list.append(set(indexed_words_dict[word].keys()))
        except:
            n_list.append(0)

    # create a set which is an intersection of all pages where all terms in search phrase appear.
    # we want to see which pages have all words in the search phrase
    pages_set = set()
    for i, item in enumerate(documents_list):
        if i == 0:
            pages_set = item
        else:
            pages_set.intersection(item)

    # calculate BMI of each page that has the search phrase (i.e. contains all words in search phrase).
    # we return bmi_results which is a dictionary with page names as keys and
    # BMI scores as values
    # we assume ri and R to be zero and qfi to be 1
    bmi_results = dict()
    k_cap = 0.0
    for page in pages_set:
        bmi = 0
        # calculate K for each doc
        dl = float(document_length_dict[page])
        k_cap = k1 * ((1 - b) + b * (dl / avdl))
        for i, word in enumerate(search_phrase_words):
            try:
                fi = indexed_words_dict[word][page]
            except:
                print('zero times appearing in {page}')
                fi = 0
            ni = get_ni(word)
            bmi += math.log10(((0.5)/(0.5)) / ((ni + 0.5) / (N - ni + 0.5))) * \
                (((k1 + 1) * fi) / (k_cap + fi)) * (((k2 + 1) * 1) / (k2 + 1))
        bmi_results[page] = bmi

    try:
        results = sorted(take(10, bmi_results.items()), reverse=True)
    except:
        results = sorted(take(len(bmi_results.keys()),
                         bmi_results.items()), reverse=True)
    return results


def index_webpages():
    # Create empty list for words that need to be cleaned
    word_list = []

    # loop through all .html files in repository folder. index the words and their frequencies
    path = os.path.dirname(os.path.abspath(__file__)) + "\\repository\\"
    files_list = os.listdir(path)
    for file_name in files_list:
        completePath = os.path.normpath(path + "\\" + file_name)
        with open(completePath, 'r', encoding="utf-8") as file:
            soup = BeautifulSoup(file, 'html.parser')
            tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span']
            # Get text from the page
            for each_text in soup.findAll(tags):
                content = each_text.text
                words = content.lower().split()
                # Append it to the wordlist and then clean the words of all symbols
                for each_word in words:
                    word_list.append(each_word)
            clean_index_words(word_list, file_name)
            word_list.clear()

def clean_index_words(words_list, file_name):
    cleaned_words_list = []

    # Clean the words from any symbols
    for word in words_list:
        symbols = '!@#$%^&*()_-+={[}]|\;:"<>?/., '
        for i in range(0, len(symbols)):
            word = word.replace(symbols[i], '')
        if len(word) > 0:
            cleaned_words_list.append(word)

    # add length of this document to the global dictionary
    document_length_dict[file_name] = len(cleaned_words_list)

    # index the words in this document
    for word in cleaned_words_list:
        # if word is there check if current page is recorded, if yes; increment it. If not, add the current page name
        # and set the count to 1
        if word in indexed_words_dict:
            if file_name in indexed_words_dict[word].keys():
                indexed_words_dict[word][file_name] += 1
            else:
                indexed_words_dict[word][file_name] = 1
        # if word is not indexed
        else:
            new_dict = dict()
            new_dict[file_name] = 1
            indexed_words_dict[word] = new_dict


def init_robot_info(link):
    disallowed_url_arr.clear()
    url = link + 'robots.txt'
    robot_txt = session.get(url, timeout=5).text

    robot_txt_lines = robot_txt.split('\n')
    if(len(robot_txt_lines) == 0):
        return

    for line in robot_txt_lines:
        line_arr = line.split(' ')
        if(len(line_arr) > 1):
            if((line_arr[0] == 'Disallow:') and (line_arr[1] is not NULL)):
                disallowed_url_arr.append(line_arr[1])


def isAllowed(link):
    for text in disallowed_url_arr:
        if(text in link):
            return False
    return True


def printMenu():
    print('\nSelect an option:')
    print('==================')
    print('1. Crawl')
    print('2. Index pages')
    print('3. Retrieval')
    print('4. Exit')


def RetrievePhrase():
    phrase = input("\nEnter a search phrase: ")
    phrase_arr = phrase.split(' ')
    bmi_results = calculate_BMI(phrase_arr)

    if(len(bmi_results) > 0):
        print('\nSearch phrase was found in the following page(s), in order of relevance:')
        for result in bmi_results:
            print(f'{result[0]} : {result[1]}')
    else:
        print('Not found.')


def main():
    count_seed = 0

    while(True):
        printMenu()
        user_input = input()
        if(user_input == '1'):
            while(True):
                seed = input('Enter seed URL (or \'done\' to end): \n')
                if(seed == 'done'):
                    break
                else:
                    count_seed = count_seed + 1
                    crawl(seed, count_seed)
        elif(user_input == '2'):
            index_webpages()
        elif(user_input == '3'):
            RetrievePhrase()
        elif(user_input == '4'):
            break
        else:
            print("Please enter valid menu option.")


if __name__ == '__main__':
    main()
