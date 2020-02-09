import threading
from queue import Queue

from findstring import *
from recursive_tree import *
from get_repo import *
import json


class SearchThread(threading.Thread):

    def __init__(self, que, find_v4_in, entry, search_string, root_path):
        super().__init__()
        self.find_v4 = find_v4_in
        self.entry = entry
        self.search_string = search_string
        self.que = que
        self.root_path = root_path

    def run(self):
        file_save_name = os.path.join(self.root_path, self.entry["path"].replace('/', '_'))
        search_res = self.find_v4.save_search_string_in_fileod(fileoid=self.entry["sha"],
                                                               string_to_search=self.search_string,
                                                               file_name=file_save_name)
        if len(search_res) > 0:
            self.que.put({"path": self.entry["path"], "res": search_res})
        self.que.put('end')


def printLog(thread_count_, que_search_result, file_path):
    with open(file_path, 'w') as outfile:
        while thread_count_ > 0:
            try:
                each_res = que_search_result.get()
                if each_res == 'end':
                    thread_count_ = thread_count_ - 1
                    continue

                for res in each_res["res"]:
                    str_log = "       in {}   {}".format(each_res["path"], res)
                    print(str_log)
                    outfile.write(str_log + '\n')
            except:
                continue


def save_search_in_Entries(entries, search_string, findv4, que_, root_path):
    thread_count_ = 0
    for entry in entries:
        thread_count_ = thread_count_ + 1
        entry_thread = SearchThread(que=que_, find_v4_in=findv4, entry=entry, search_string=search_string,
                                    root_path=root_path)
        entry_thread.daemon = True
        entry_thread.start()
    return thread_count_


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

        print("\n\n====PROCESSING REPO '{}'=======".format(repository["name"]))
        repo_ex_dir = os.path.join(owner_respo_dir, repository["name"])
        try:
            os.makedirs(repo_ex_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        string_cap = "\n   SEARCH FILES BY REGULAR EXPRESSION IN REPO '{}'   (Sample expresion is {})\n".format(
            repository["name"], sample_regex)
        print(string_cap)
        find = FindStringV3(entries=tree_entries, owner=owner, repo=repository["name"])
        search_result = find.find_string_filename(sample_regex)

        file_path = os.path.join(repo_ex_dir, 'regx_file_list.log')
        with open(file_path, 'w') as outfile:
            outfile.write(string_cap)
            for str_ in search_result:
                print(str_)
                outfile.write("{}\n".format(str_))

        print("\n   SEARCH STRING IN FILTERED FILES IN REPO '{}'   (Sample string is {})\n".format(repository["name"],
                                                                                                   sample_search_string))
        find_v4 = FindString(owner, repository["name"], [], "")
        que_result = Queue()
        thread_count = save_search_in_Entries(entries=search_result, search_string=sample_search_string, findv4=find_v4,
                                              que_=que_result, root_path=repo_ex_dir)
        file_path = os.path.join(repo_ex_dir, 'search_string_info.log')

        printLog(thread_count_=thread_count, que_search_result=que_result, file_path=file_path)
