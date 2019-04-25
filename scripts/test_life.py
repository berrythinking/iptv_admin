#!/usr/bin/env python3
import argparse
import os
import sys
import re
import random
from mongoengine import connect

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.stream.stream_entry import make_test_life_stream
from app.service.service_settings import ServiceSettings

PROJECT_NAME = 'test_life'


class M3uParser:
    def __init__(self, logging):
        self.files = []
        self.logging = logging

    # Read the file from the given path
    def readM3u(self, filename):
        self.filename = filename
        self.readAllLines()
        self.parseFile()

    # Read all file lines
    def readAllLines(self):
        self.lines = [line.rstrip('\n') for line in open(self.filename)]
        return len(self.lines)

    def parseFile(self):
        numLine = len(self.lines)
        for n in range(numLine):
            line = self.lines[n]
            if line[0] == "#":
                # print("Letto carattere interessante")
                self.manageLine(n)

    def manageLine(self, n):
        lineInfo = self.lines[n]
        lineLink = self.lines[n + 1]
        if lineInfo != "#EXTM3U":
            m = re.search("tvg-name=\"(.*?)\"", lineInfo)
            name = m.group(1) if m else 'Unknown'
            m = re.search("tvg-ID=\"(.*?)\"", lineInfo)
            id = m.group(1) if m else 'Unknown'
            m = re.search("tvg-logo=\"(.*?)\"", lineInfo)
            logo = m.group(1) if m else 'Unknown'
            m = re.search("group-title=\"(.*?)\"", lineInfo)
            group = m.group(1) if m else 'Unknown'
            m = re.search("[,](?!.*[,])(.*?)$", lineInfo)
            title = m.group(1) if m else 'Unknown'
            # ~ print(name+"||"+id+"||"+logo+"||"+group+"||"+title)

            test = {
                "title": title,
                "tvg-name": name,
                "tvg-ID": id,
                "tvg-logo": logo,
                "tvg-group": group,
                "titleFile": os.path.basename(lineLink),
                "link": lineLink
            }
            self.files.append(test)

    # Remove files with a certain file extension
    def filterOutFilesEndingWith(self, extension):
        self.files = list(filter(lambda file: not file["titleFile"].endswith(extension), self.files))

    # Select only files with a certain file extension
    def filterInFilesEndingWith(self, extension):
        # Use the extension as list
        if not isinstance(extension, list):
            extension = [extension]
        if not len(extension):
            self.logging.info("No filter in based on extensions")
            return
        new = []
        # Iterate over all files and extensions
        for file in self.files:
            for ext in extension:
                if file["titleFile"].endswith(ext):
                    # Allowed extension - go to next file
                    new.append(file)
                    break
        self.logging.info("Filter in based on extension: [" + ",".join(extension) + "]")
        self.files = new

    # Remove files that contains a certain filterWord
    def filterOutFilesOfGroupsContaining(self, filterWord):
        self.files = list(filter(lambda file: filterWord not in file["tvg-group"], self.files))

    # Select only files that contais a certain filterWord
    def filterInFilesOfGroupsContaining(self, filterWord):
        # Use the filter words as list
        if not isinstance(filterWord, list):
            filterWord = [filterWord]
        if not len(filterWord):
            self.logging.info("No filter in based on groups")
            return
        new = []
        for file in self.files:
            for fw in filterWord:
                if fw in file["tvg-group"]:
                    # Allowed extension - go to next file
                    new.append(file)
                    break
        self.logging.info("Filter in based on groups: [" + ",".join(filterWord) + "]")
        self.files = new

    # Getter for the list
    def getList(self):
        return self.files

    # Return the info assciated to a certain file name
    def getCustomTitle(self, originalName):
        result = list(filter(lambda file: file["titleFile"] == originalName, self.files))
        if len(result):
            return result
        else:
            print("No file corresponding to: " + originalName)

    # Return a random element
    def getFile(self, randomShuffle):
        if randomShuffle:
            random.shuffle(self.files)
        if not len(self.files):
            self.logging.error("No files in the array, cannot extract anything")
            return None
        return self.files.pop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=PROJECT_NAME, usage='%(prog)s [options]')
    parser.add_argument('uri', help='Uri to m3u8 list')
    parser.add_argument('mongo_uri', help='MongoDB credentials')

    argv = parser.parse_args()

    mongo = connect(argv.mongo_uri)
    if mongo:
        service_settings = ServiceSettings.objects().first()
        m3u_parser = M3uParser(None)
        m3u_parser.readM3u(argv.uri)
        for file in m3u_parser.files:
            stream = make_test_life_stream(service_settings.feedback_directory)
            stream.input.urls[0].uri = file['link']
            stream.name = '{0}({1})'.format(file['tvg-group'], file['title'])
            service_settings.streams.append(stream)

        service_settings.save()
