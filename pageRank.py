import requests, time, csv, os
from bs4 import BeautifulSoup


savePath = os.path.dirname(os.path.abspath(__file__)) + "\\repository\\"
if not os.path.exists(savePath):
    os.makedirs(savePath)
session = requests.Session()

def main():        
    crawl('https://www.japscan.ws/', 0)
    
    #Seeds
        #https://www.cpp.edu/index.shtml
        #https://ameblo.jp/
        #https://www.japscan.ws/ 

def crawl(seed, count_seed):
    debug = False
    depth = 0
    maxDepth = 500
    visited = []
    
    #Check robots.txt for any restricted pages
    #Add url to the queue
    queue = []

    domain = seed.split("/")[2]
    queue.append(seed)
    
    session.headers.update({'Host': domain,
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Connection': 'keep-alive',
                            'Pragma': 'no-cache',
                            'Cache-Control': 'no-cache'})


    while((depth < maxDepth) or (len(queue) == 0)):
        depth += 1
        currentUrl = queue.pop(0)
        print('currentUrl: ' + currentUrl)

        if depth == 1:
            get_html = requests.get(currentUrl).content
            soup_lang = BeautifulSoup(get_html, 'html.parser')
            print("Language is: " + soup_lang.html["lang"])


        #Every 20 pages print show the depth in the console
        if(depth%20 == 0):
            print("depth: " + str(depth) + "/" + str(maxDepth))
            #Every 100 pages show the size of the queue
            if(depth%100 == 0):
                print("Queue length: " + str(len(queue)))
        
        if(debug):
            print("requesting: " + currentUrl)
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
        print('outlinks: ' + str(outlinks))
        for link in outlinks:
            if((link not in visited) and (link not in queue)):
                queue.append(link)
                
    if (debug):
        for link in queue:
            print(link)
        print("\n\nVISITED\n")
        for link in visited:
            print(link)
        print("\nQueue length: " + str(len(queue)) +
              "\tVisited length: " + str(len(visited)))


def getLinks(page):
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
        if link[0] == '/':
            link = currentUrl + link[1:]
        if link[0] != "#" and len(link) > len(domain):
            if link.split(":")[0] != "mailto":
                if link.split("/")[2] == domain:
                    if link[0:5] == "http:":
                        link = "https:" + link.split("http:")[1]
                    trueOutlinks.append(link)
                    print("Link " + str(i) + ": "+ link)

    return trueOutlinks

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

if __name__ == '__main__':
    main()
