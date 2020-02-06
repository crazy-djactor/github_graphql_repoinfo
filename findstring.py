import re
from constAPI import *


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
                search_s = self.search_string_in_fileod(fileoid=entry['oid'], string_to_search=string_to_search)
                if len(search_s):
                    new_path = "%s\%s" % (parent_path,entry["name"])
                    self.search_result.append((new_path, search_s))
            if entry["type"] == 'tree':
                new_path = "%s\%s" % (parent_path, entry["name"])
                self.search_string_entries(entries=entry["child"], string_to_search=string_to_search,
                                           parent_path=new_path)

    def search_string_in_fileod(self, fileoid, string_to_search):
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
            print("search string err")
            return []
