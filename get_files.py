from findstring import *
from recursive_tree import *
import json

if __name__ == '__main__':
    # Get recursive tree of repository as jason
    # tree = RecursiveTreeV3(owner, sample_repo)
    # tree_entries = tree.get_recursive_tree()
    #
    # print("\n\n*****RECURSIVE TREE ENTRIES*****\n")
    # for str_ in tree_entries['tree']:
    #     print(str_)

    file_name = sample_repo + '.json'
    with open(file_name, 'w') as outfile:
        json.dump(tree_entries, outfile)

    print("\n\n*****SEARCH FILES BY REGULAR EXPRESSION*****(Sample expresion is {})\n".format(sample_regex))
    find = FindStringV3(entries=tree_entries, owner=owner, repo=sample_repo)

    search_result = find.find_string_filename(sample_regex)
    for str_ in search_result:
        print(str_)

    print("\n\n*****SEARCH STRING IN FILES*****(Sample string is {})\n".format(sample_search_string))
    search_str = find.search_string_content(sample_search_string)
    for str_ in search_str:
        print(str_)
