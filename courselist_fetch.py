import requests
from bs4 import BeautifulSoup
from main import *
import sqlite3

print("Fetching course list from catalog.mst.edu")
# Making a GET request

#update class list file
r = requests.get(url='https://catalog.mst.edu/undergraduate/courselist/',headers={'Connection':'close'})
#clear file
f=open("courselist.txt", "w").close()
f=open("courselist.txt", "w")

# Parsing the HTML
soup = BeautifulSoup(r.content, 'html.parser')

s = soup.find('div', id='content')
content = s.find_all('li')
content=str(content).split('</li>')
for c in content:
    c = c[14:-4]
    c=c.split(">")
    try:
        link = c[0]
        link = link.replace('"', '')
        title = c[1]
        f.write(link + ', ' + title + "\n")
    except:
        continue
f.close()

# #break lines into easier to process txt file
def process_title(title):
        index = 0
        code = ''
        class_title = ''
        department = ''
        #split line into array of words with spaces included
        line_array= [i for j in title.split() for i in (j, ' ')][:-1]
        #get class code and index of class code to split the line
        for word in line_array:
            if word.isnumeric():
                code = word
                break
            index += 1
        #write department
        for word in line_array[:index]:
            department += word
        #write class title
        for word in line_array[index+1:]:
            class_title += word
        return(department.strip(), code.strip(), class_title.strip())

#go through each department
with open('courselist.txt', 'r') as file:
    conn = sqlite3.connect('MSTDatabase.db')
    cursor = conn.cursor()
    # Read each line in the file
    f=open("classes.txt", "w").close()
    f=open("classes.txt", "w")
    for line in file:
        #clear file
        link=line.split(',')[0]
        r = requests.get(url='https://catalog.mst.edu/'+link,headers={'Connection':'close'})
        soup = BeautifulSoup(r.content, 'html.parser')
        s = soup.find_all('div', class_='courseblock')
        #print(s)
        for item in s:
            class_title = item.find('p', class_='courseblocktitle')
            class_description = item.find('p', class_='courseblockdesc')
            department, code, class_title =process_title(class_title.text)
            class_description = (class_description.text.strip())
            cursor.execute("INSERT OR REPLACE INTO CLASS (ClassCode, ClassTitle, ClassDep, Description) VALUES (?, ?, ?, ?)", (code, class_title, department, class_description))
            
    conn.commit()    
    conn.close()
        #uncomment to test (prints out all classes to terminal)
        #with open('classes.txt', 'r') as file:
            # Read each line in the file
            #for line in file:
                #print(line)
    f.close()
    file.close()


        