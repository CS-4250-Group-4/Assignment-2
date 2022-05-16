def main():
    global pageDict
    global linkDict
    
    #domains
    domain = "cpp"
    #domain = "ameblo"
    #domain = "japscan"

    linkDict = {}
    pageDict = {}

    #Load in all the pages visited(pageDict) and all the in-links(linkDict)
    with open(domain + "_linkDict" + ".csv") as csvfile:
        lines = csvfile.read().split('\n')
        for line in lines:
            #Loop through the string array and convert it back to code
            inlinks = []
            #Remove first { from array
            #Delete last } from array
            if line:
                vals = line.replace("[","").replace("]","").replace("\'","").replace(" ","")
                vals = vals.split(",")
                for val in vals:
                    inlinks.append(val)
            linkDict[line.split(",")[0]] = inlinks
    with open(domain + "_pageDict" + ".csv") as csvfile:
        lines = csvfile.read().split('\n')
        for line in lines:
            if line:
                pageDict[line.split(",")[0]] = (line.split(",")[1], 1/(len(lines) - 1))


    #First run of calculating page rank

    #Get the page from pageDict, loop through in-links from linkDict

    #Sum up the in-link prvalue/ in-link # of outlinks
    for i in range(10):
        maxRank = 0
        maxRank2 = 0
        maxRank3 = 0
        maxPage = ""
        maxPage2 = ""
        maxPage3 = ""
        #Sum of all pages page rank
        pageRankSum = 0.0
        #Remove any links that are just linking to themself
        try:
            for page in pageDict:
                for inlink in linkDict[page]:
                    if(inlink == page):
                        linkDict[page].remove(inlink)
                        pageDict[page] = (str(int(pageDict[page][0]) - 1), pageDict[page][1])
        except(KeyError):
            pass
            #print("KEYERROR: " + str(page) + ", ")

        
        for page in pageDict:
            inlinkSum = 0.0
            try:
                for inlink in linkDict[page]:
                    if pageDict[inlink][0] == "0":
                        inlinkSum += 0
                    else:
                        inlinkSum += pageDict[inlink][1]/int(pageDict[inlink][0])
                    pageDict[page] = (pageDict[page][0], inlinkSum)
            except(KeyError):
                #print("not found in linkDict" + page)
                pass
            pageRankSum += float(pageDict[page][1])
        #print("CYCLE " + str(i) + " COMPLETE")
        #print("Page Rank Sum: " + str(pageRankSum))
        for page in pageDict:
            #print(page + "/t" + str(pageDict[page]))
            #print(pageDict[page][1])
            pass
            if (pageDict[page][1] > maxRank):
                maxRank = pageDict[page][1]
                maxPage = page
            elif (pageDict[page][1] > maxRank2):
                maxRank2 = pageDict[page][1]
                maxPage2 = page
            elif (pageDict[page][1] > maxRank3):
                maxRank3 = pageDict[page][1]
                maxPage3 = page
    print("Results saved to " + domain + "_pageRank.csv")
    dictToCsv(domain + "_pageRank")
"""
        print(maxPage + ": " + str(maxRank))
        print(len(linkDict[maxPage]))
        print(maxPage2 + ": " + str(maxRank2))
        print(len(linkDict[maxPage2]))
        print(maxPage3 + ": " + str(maxRank3))
        print(len(linkDict[maxPage3]))
"""
        
def dictToCsv(filename):#, fields):
    global pageDict
    global linkDict
    #pageDict = {} #Page, # of outlinks
    #linkDict = {} # key Page, list of pages linking to key page
    filename += ".csv"

    # writing to csv if its just a regular dict without an array
    with open(filename, 'w') as csvfile:
        csvfile.write("Page,Inlinks,Outlinks,Page Rank\n")
        for entry in pageDict:
            entry = str(entry)
            csvfile.write(entry + ",")
            try:
                csvfile.write(str(len(linkDict[entry])) + ",")
            except KeyError:
                csvfile.write("0,")
            csvfile.write(str(pageDict[entry]).replace("(","").replace(")","").replace("\'","").replace(" ","") + "\n")
            
if __name__ == "__main__":
    
    main()
