import requests, time, csv, os
from bs4 import BeautifulSoup


savePath = os.path.dirname(os.path.abspath(__file__)) + "\\repository\\"
if not os.path.exists(savePath):
    os.makedirs(savePath)
session = requests.Session()

#Dictionaries to calc page rank
pageDict = {} #Page, # of outlinks
linkDict = {} # key Page, list of pages linking to key page

disallowed_url_arr = [] # array of disallowed pages from robots.txt
def main():
    global pageDict
    global linkDict
    #crawl('https://www.cpp.edu/index.shtml', 0)
    #crawl('https://ameblo.jp/', 0)
    crawl('https://www.japscan.ws/ ', 0)

    print("\n\n\npageDict, len: " + str(len(pageDict)))
    printDict(pageDict)
    
    linkDict = cleanLinkDict(linkDict)
    print("\n\n\nlinkDict, len: " + str(len(linkDict)))
    printDict(linkDict)
    
    #Seeds
        #https://www.cpp.edu/index.shtml
        #https://ameblo.jp/
        #https://www.japscan.ws/ 

def crawl(seed, count_seed):
    debug = True
    depth = 0
    maxDepth = 500
    visited = []
    
    #Check robots.txt for any restricted pages
    #Add url to the queue
    queue = []

    domain = seed.split("/")[2]
    queue.append(seed)
    init_robot_info("https://" + domain + "/")
    
    session.headers.update({'Host': domain,
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Connection': 'keep-alive',
                            'Pragma': 'no-cache',
                            'Cache-Control': 'no-cache'})


    while((depth < maxDepth) or (len(queue) == 0)):
        depth += 1
        currentUrl = queue.pop(0)
        if (not isAllowed(currentUrl)):
            break;

        if depth == 1:
            get_html = requests.get(currentUrl).content
            soup_lang = BeautifulSoup(get_html, 'html.parser')
            print("Language is: " + soup_lang.html["lang"])

        if debug:
            #Every 20 pages print show the depth in the console
            if(depth%20 == 0):
                print("depth: " + str(depth) + "/" + str(maxDepth))
                #Every 100 pages show the size of the queue
                if(depth%100 == 0):
                    print("Queue length: " + str(len(queue)))
                    print("pageDict length: " + str(len(pageDict)))
                    print("linkDict length: " + str(len(linkDict)))
            print('currentUrl: ' + currentUrl)
        visited.append(currentUrl)

        try:
            #get the current page's html
            page = session.get(currentUrl, timeout=5)
                
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

        outlinks = getLinks(page)
        
        # call split on link for # and only check first half
        # ex https://docs.python-requests.org/en/latest/#the-contributor-guide
        # ignore #the-contributor-guide and just go to https://docs.python-requests.org/en/latest/
        for link in outlinks:
            if((link not in visited) and (link not in queue)):
                queue.append(link)
        #Add the page and its number of outlinks to pageDict
        #Add the page to each outlink's linkDict list value
        addToDict(page, outlinks)
                
    if (debug and False):
        for link in queue:
            print(link)
        print("\n\nVISITED\n")
        for link in visited:
            print(link)
        print("\nQueue length: " + str(len(queue)) +
              "\tVisited length: " + str(len(visited)))

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
            if((line_arr[0] == 'Disallow:') and (line_arr[1])):
                disallowed_url_arr.append(line_arr[1])

def isAllowed(link):
    for text in disallowed_url_arr:
        if(text in link):
            return False
    return True

def getLinks(page):
    debug = False
    currentUrl = str(page.url)
    domain = currentUrl.split("/")[2]
    #Go through the html page passed as page and collect any valid
    #links, modifying some of them to have a similar format throughout
    soup = BeautifulSoup(page.text, 'html.parser')
    outlinks = soup.find_all("a", href=True)
    
    trueOutlinks = []    
    #Go through each a tag and filter out the good links
    for i in range(len(outlinks)):
        link = (outlinks[i]["href"])
        #only accept links that start with http, www, or /
        if link:
            if (link[0] == "/" or ( len(link) > 4 and (link[0:3] == "www" or link[0:4] == "http"))):
                #strip any %20 at the end of a link
                if(currentUrl[-3:] == "%20"):
                    currentUrl = currentUrl[:-3]
                if link[0] == '/':
                    if len(link) > 1:
                        link = currentUrl + link[1:]
                        trueOutlinks.append(link)
                    else:
                        pass        
                elif link[0:3] == "www":
                    link = "https://" + link
                    trueOutlinks.append(link)
                else:
                    #print("split link at /  link: " + link + "\nfrom " + page.url)
                    if link.split(":")[0] != "mailto":
                        if link.split("/")[2] == domain:
                            if link[0:5] == "http:":
                                link = "https:" + link.split("http:")[1]
                            trueOutlinks.append(link)
                            if debug:
                                print("Link " + str(i) + ": "+ link)

    return trueOutlinks


def addToDict(page, outlinks):
    global pageDict
    global linkDict
    debug = False
    currentUrl = str(page.url)
    #pageDict = {} #Page, # of outlinks
    #linkDict = {} # key Page, list of pages linking to key page

    #Add the page as a key if it isnt in PageDict yet
    if (currentUrl not in pageDict):
        pageDict[currentUrl] = len(outlinks)
    #Add the page to all of it's outlink's linkDict entries
    for link in outlinks:
        if debug:
            print("\n\n\nlinkDict\n")
            printDict(linkDict)
        if (link not in linkDict):
            if debug:
                print("add " + currentUrl + " to " + link)
            linkDict[link] = {currentUrl}
        else:
            if debug:
                print(link + " in linkDict already.\nContains: " + str(linkDict[link]))
            linkDict[link].add(currentUrl)
    if debug:
        print("pageDict length is " + str(len(pageDict)))
        print("linkDict length is " + str(len(linkDict)))

#Used to remove any pages from linkDict that arent in the first (max depth) pages
def cleanLinkDict(linkDict):
    cleanDict = {}
    for link in pageDict.keys():
        if link in linkDict:
            cleanDict[link] = linkDict[link]
    return cleanDict
    

def save_inlink_csv():
    global seed_count
    fields = ['URL', '# of in Links', 'in Links']
    report_info.insert(0, fields)
    filename = "report" + str(seed_count) + ".csv"

    # writing to csv file
    with open(filename, 'w', ) as csvfile:
        csvwriter = csv.writer(csvfile, lineterminator='\n')
        csvwriter.writerows(report_info)
    report_info.clear()


def printDict(dictionary):
    for key in dictionary.keys():
        print(str(key) + ": " + str(dictionary[key]))


if __name__ == '__main__':
    main()
