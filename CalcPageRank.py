def main():
    #domains
    domain = "cpp"
    #domain = "ameblo"
    #domain = "japscan"

    linkDict = {}
    pageDict = {}

    #Load in all the pages visited(pageDict) and all the in-links(linkDict)
    with open("linkDict_" + domain + ".csv") as csvfile:
        lines = csvfile.read().split('\n')
        for line in lines:
            #Loop through the string array and convert it back to code
            inlinks = []
            #Remove first { from array
            #Delete last } from array
            if line:
                vals = line.replace("}","").replace("{","").replace("\'","").replace(" ","")
                vals = vals.split(",")
                for val in vals:
                    inlinks.append(val)
            linkDict[line.split(",")[0]] = inlinks
    with open("pageDict_" + domain + ".csv") as csvfile:
        lines = csvfile.read().split('\n')
        for line in lines:
            if line:
                pageDict[line.split(",")[0]] = (line.split(",")[1], 1/(len(lines) - 1))


    #First run of calculating page rank

    #Get the page from pageDict, loop through in-links from linkDict

    #Sum up the in-link prvalue/ in-link # of outlinks
    for i in range(10):
        for page in pageDict:
            inlinkSum = 0
            try:
                for inlink in linkDict[page]:
                    if pageDict[inlink][0] == "0":
                        inlinkSum += 0
                    else:
                        inlinkSum += pageDict[inlink][1]/int(pageDict[inlink][0])
                pageDict[page] = (pageDict[page][0], inlinkSum)
            except(KeyError):
                print("not found in linkDict" + page)
        print("CYCLE " + str(i) + " COMPLETE")
        for page in pageDict:
            #print(page + "/t" + str(pageDict[page]))
            print(pageDict[page][1])

if __name__ == "__main__":
    main()
