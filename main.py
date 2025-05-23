from ordered_collection import OrderedCollection
import urllib.request
import json

if __name__ == "__main__":
    res = urllib.request.urlopen("https://iiif.bodleian.ox.ac.uk/iiif/activity/all-changes")

    coll = OrderedCollection(res.read())

    for page in coll.pages_rev():
        for act in page.activities():
            print(f"{act._type}: {act.obj}")
