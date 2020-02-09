import json
import re
from constAPI import *
import base64

class FindStringV3:
    def __init__(self, owner, repo, entries):
        self.owner = owner
        self.repo = repo
        self.entries = entries
        pass

    def find_string_filename(self, regex):
        search_result = []
        for str_ in self.entries['tree']:
            if str_["type"] != "blob":
                continue
            file_name = str_["path"].split('/')[-1]
            z = re.match(regex, file_name)
            if z:
                search_result.append(str_)
        return search_result

    def search_string_in_file(self, file_, string_to_search):
        sha = file_["sha"]
        query = "repos/%s/%s/git/blobs/%s" % (self.owner, self.repo, sha)
        response = run_query_v3(query)
        try:
            list_of_results = []
            text_content = base64.b64decode(response["content"]).decode()
            read_obj = text_content.split('\n')
            # Read all lines in the file one by one
            line_number = 0
            for line in read_obj:
                # For each line, check if line contains the string
                line_number += 1
                if string_to_search in line:
                    # If yes, then add the line number & line as a tuple in the list
                    list_of_results.append((file_["path"], line_number, line.rstrip()))
            return list_of_results
        except:
            return []

    def search_string_content(self, entries=None, string_to_search=""):
        """Search for the given string in file and return lines containing that string,
        along with line numbers"""
        list_of_results = []
        if entries is None:
            for file_ in self.entries['tree']:
                if file_["type"] == 'blob':
                    list_of_results = list_of_results + self.search_string_in_file(file_, string_to_search)
        else:
            for file_ in entries:
                if file_["type"] == 'blob':
                    list_of_results = list_of_results + self.search_string_in_file(file_, string_to_search)
        # Return list of tuples containing line numbers and lines where string is found
        return list_of_results

class FindString:
    def __init__(self, owner, repo, entries, path):
        self.entries = entries
        self.search_result = []
        self.path = path
        self.owner = owner
        self.repo = repo
        pass

    def search_byRegX(self, regX):
        self.search_result.clear()
        self.search_entries_byRegX(entries=self.entries, regex=regX, parent_path=self.path)
        return self.search_result

    def search_entries_byRegX(self, entries, regex, parent_path):
        """
        Search entries and sub entries recursively to find matched names

        :param entries: Target entries for search
        :param regex: Regular expression
        :param parent_path: It is now path which target entries involved, eg: repository:helloworld\src
        :return: Append matched items to search_result
        """

        for entry in entries:
            z = re.match(regex, entry["name"])
            if z:
                result_path = "%s\%s" % (parent_path, entry["name"])
                self.search_result.append(result_path)
            if entry["type"] == 'tree':
                new_path = "%s\%s" % (parent_path, entry["name"])
                self.search_entries_byRegX(entry["child"], regex, new_path)

    def search_string_in_file(self, string_to_search):
        """
        Search special string in files and return their file names and line numbers
        :param string_to_search:
        :return:
        """
        self.search_result.clear()
        self.search_string_entries(entries=self.entries, string_to_search=string_to_search,
                                   parent_path=self.path)
        return self.search_result

    def search_string_entries(self, entries, string_to_search, parent_path):
        for entry in entries:
            if entry["type"] == 'blob':
                file_name_save = entry["path"].replace('/', '_')
                search_s = self.save_search_string_in_fileod(fileoid=entry['oid'], string_to_search=string_to_search, file_name=file_name_save)
                if len(search_s):
                    new_path = "%s\%s" % (parent_path,entry["name"])
                    self.search_result.append((new_path, search_s))
            if entry["type"] == 'tree':
                new_path = "%s\%s" % (parent_path, entry["name"])
                self.search_string_entries(entries=entry["child"], string_to_search=string_to_search,
                                           parent_path=new_path)

    def save_search_string_in_fileod(self, fileoid, string_to_search, file_name):
        """
        Search string_to_search in given file_name
        :param fileoid: file object id in Git Object which is used for search
        :param string_to_search: Search string
        :return: line number as list
        """
        """Search for the given string in file and return lines containing that string,
        along with line numbers"""
        list_of_results = []
        query = """
        {
            repository(owner: "%s", name: "%s") {
                object(oid: "%s") {
                ... on Blob {
                        text
                    }
                }
            }
        }
        """
        query = query % (self.owner, self.repo, fileoid)
        try:
            result = run_query(query)
            if result["repository"]["object"]["text"] is None:
                return []
            with open(file_name, 'w') as outfile:
                outfile.write(result["repository"]["object"]["text"])

            read_obj = result["repository"]["object"]["text"].split('\n')
            list_of_results.clear()
            # Read all lines in the file one by one
            line_number = 0
            for line in read_obj:
                # For each line, check if line contains the string
                line_number += 1
                if string_to_search in line:
                    # If yes, then add the line number & line as a tuple in the list
                    list_of_results.append((line_number, line.rstrip()))
            # Return list of tuples containing line numbers and lines where string is found
            return list_of_results
        except:
            return []

