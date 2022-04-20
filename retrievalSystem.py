import os


repoPath = os.path.dirname(os.path.abspath(__file__)) + "\\repository\\"
repos = os.listdir(repoPath)

def main():
    #Open every repository in the repository folder and loop through each of its files
    for i in range(len(repos)):
        print("Checking in repository for " + repos[i])
        files = os.listdir(repoPath + repos[i])
        #Loop through every file in the ith repository
        for j in range(len(files)):
            print(str(files[j]))
            #Open and then close each page in each repository
            currentPage = open(repoPath + repos[i] + "\\" + files[j], "r")
            currentPage.close()
        print('\n')
if __name__ == '__main__':
    main()
