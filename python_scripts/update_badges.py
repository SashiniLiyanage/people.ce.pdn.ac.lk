import requests
import os
import json

# Where the data is available
studentSource = 'https://api.ce.pdn.ac.lk/people/v1/students/all/'

def getStud_profile(data):
    # TODO: Check the name options
    if(data['name_with_initials'] != ""):
        name = data["name_with_initials"]
    elif(data['preferred_long_name'] != ""):
        name = data["preferred_long_name"]
    elif(data['full_name'] != ""):
        name = data["full_name"]
    else:
        # Name not found
        return {}

    if (data["honorific"] != ""):
        name = data["honorific"] + " " + name

    profile_img = "/assets/images/profile_default.jpg" if (data["profile_image"] == "") else data["profile_image"]

    return {
        "name": name,
        "affiliation": data["current_affiliation"],
        "profile_url": data["profile_page"],
        "profile_image": profile_img
    }

def create_page(data):
    # print(_data)

    page_url = '../pages/badges/{0}.md'.format(data['tag'])
    os.makedirs(os.path.dirname(page_url), exist_ok=True)

    student_list = ""

    for s in data['students']:
        student_eNumber = s['eNumber']
        print(student_eNumber)
        print(students[student_eNumber])
        student = getStud_profile(students[student_eNumber])

        student_list += "\n - { eNumber: \""+ student_eNumber + "\", name: \""+ student['name'] +"\", position: \"" + s['position'] + "\", profile_url: \"" + student['profile_url'] +"\", profile_image: \"" + student['profile_image'] +"\" }"

    page_content = """---
layout: badge_page
title: """ + data['title'] + """
permalink: \"/badges/""" + data['tag'] + """\"
badge_image: \"""" + data['image'] + """\"
badge_description: \"""" + data['description'] + """\"

students: """ + student_list + """
---
"""

    print(page_content)
    with open(page_url, "w") as f:
        f.write(page_content)


# All student details
r = requests.get(studentSource)

# Fetch data from the people.ce.pdn.ac.lk
if r.status_code == 200:
    students = json.loads(r.text)


# Read the /batch folder and generate the file, _data/badges.json
path = "../badges/"
directory_list = os.listdir(path)

badges_file = { "badges": {}, "members": {}}

for filename in directory_list:
    badge_data = json.load(open(path + filename, "r"))

    tag = badge_data['tag']
    page_url = "/badges/{0}/".format(tag)

    # Append the badge details
    badges_file['badges'][tag] = {
        "title": badge_data['title'],
        "image": badge_data['image'],
        "description": badge_data['description'],
        "page": page_url
    }

    # Append the student details
    for stud in badge_data['students']:
        eNumber = stud['eNumber']
        position = stud['position']

        if eNumber not in badges_file['members']: badges_file['members'][eNumber] = []
        badges_file['members'][eNumber].append({"tag": tag, "position": position})

    # Create a page for the badge
    create_page(badge_data)

# Generate the '_data/badges.json'
filename = "../_data/badges.json"
os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, "w") as f:
    f.write(json.dumps(badges_file, indent = 4))