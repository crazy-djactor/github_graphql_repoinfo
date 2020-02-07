from findstring import *
from recursive_tree import *
from get_repo import *
import json

if __name__ == '__main__':

    base_path = os.path.dirname(os.path.abspath(__file__))
    owner_respo_dir = os.path.join(base_path, owner)

    # Get all repositories of owner
    repositories = get_all_respositories(owner)
    # Get recursive tree of repository as jason
    for repository in repositories:
        file_name = repository["name"] + '.json'
        file_path = os.path.join(owner_respo_dir, file_name)
        tree_entries = None
        try:
            with open(file_path, 'r') as infile:
                tree_entries = json.load(infile)
        except:
            continue
        print("====PROCESSING REPO '{}'=======".format(repository["name"]))
        print("\n\n   SEARCH FILES BY REGULAR EXPRESSION IN REPO '{}'   (Sample expresion is {})\n".format(repository["name"], sample_regex))
        find = FindStringV3(entries=tree_entries, owner=owner, repo=repository["name"])
        search_result = find.find_string_filename(sample_regex)
        for str_ in search_result:
            print(str_)

        print("\n\n   SEARCH STRING IN ALL FILES   (Sample string is {})\n".format(sample_search_string))
        search_str = find.search_string_content(string_to_search=sample_search_string)
        for str_ in search_str:
            print(str_)

        print("\n\n   SEARCH STRING IN FILTERED FILES IN REPO '{}'   Sample string is {})\n".format(repository["name"], sample_search_string))
        search_str = find.search_string_content(entries=search_result, string_to_search=sample_search_string)
        for str_ in search_str:
            print(str_)
