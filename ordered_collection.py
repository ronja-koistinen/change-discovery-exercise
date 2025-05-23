import json
import urllib
from dataclasses import dataclass
from enum import StrEnum
from typing import Dict, List, Optional, Iterator
from datetime import datetime

class OrderedCollectionType(StrEnum):
    ORDERED_COLLECTION = "OrderedCollection"

class OrderedCollectionPageType(StrEnum):
    ORDERED_COLLECTION_PAGE = "OrderedCollectionPage"

class ActivityType(StrEnum):
    CREATE = "Create"
    UPDATE = "Update"
    DELETE = "Delete"
    MOVE = "Move"
    ADD = "Add"
    REMOVE = "Remove"
    REFRESH = "Refresh"

@dataclass
class Resource:
    id: Optional[str]
    _type: str
    see_also: Optional[List[Dict]] = None
    canonical: Optional[str] = None
    provider: Optional[List[Dict]] = None

    def __init__(self, d):
        self.id = d["id"]
        self._type = d["type"]
        if "seeAlso" in d:
            self.see_also = d["seeAlso"]
        if "canonical" in d:
            self.canonical = d["canonical"]
        if "provider" in d:
            self.provider = d["provider"]

@dataclass
class ActorType(StrEnum):
    APPLICATION = "Application"
    ORGANIZATION = "Organization"
    PERSON = "Person"

@dataclass
class Activity:
    id: str
    _type: ActivityType
    obj: Resource
    target: Optional[Dict] = None
    summary: Optional[str] = None
    end_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    actor: Optional[Dict] = None

    def __init__(self, d):
        self.id = d["id"]
        self._type = ActivityType(d["type"])
        self.obj = Resource(d["object"])
        if "target" in d:
            self.target = d["target"]
        if "summary" in d:
            self.summary = d["summary"]
        if "endTime" in d:
            self.end_time = d["endTime"]
        if "startTime" in d:
            self.start_time = d["startTime"]
        if "actor" in d:
            self.actor = d["actor"]

@dataclass
class OrderedCollectionPage:
    id: str
    _type: OrderedCollectionPageType
    start_index: int
    partOf: str
    items: List[Activity]
    prev: Optional[str] = None
    next: Optional[str] = None

    def __init__(self, d):
        self.id = d["id"]
        self._type = OrderedCollectionPageType(d["type"])
        self.start_index = d["startIndex"]
        self.partOf = d["partOf"]
        if "prev" in d:
            self.prev = d["prev"]
        if "next" in d:
            self.next = d["next"]
        self.items = [Activity(item) for item in d["orderedItems"]]

    def activities(self) -> Iterator[Activity]:
        for x in self.items:
            yield x

@dataclass
class OrderedCollection:
    id: str
    context: str
    _type: OrderedCollectionType
    last: Dict
    first: Optional[Dict]
    total_items: Optional[int] = None

    def __init__(self, obj):
        d = json.loads(obj)
        self.id = d["id"]
        self.context = d["@context"]
        if "first" in d:
            self.first = d["first"]
        self.last = d["last"]
        self._type = OrderedCollectionType(d["type"])
        if "totalItems" in d:
            self.total_items = d["totalItems"]

    def pages_rev(self) -> Iterator[OrderedCollectionPage]:
        current_page_id = self.last["id"]
        while current_page_id:
            res = urllib.request.urlopen(current_page_id)
            current_page = json.load(res)
            if "prev" in current_page and current_page["prev"] is not None:
                current_page_id = current_page["prev"]["id"]
            else:
                current_page_id = None
            yield OrderedCollectionPage(current_page)

if __name__ == "__main__":
    import sys
    print("This is an importable module", file=sys.stderr)
