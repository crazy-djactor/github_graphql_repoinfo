import errno

from constAPI import *
from recursive_tree import *
import json

# The GraphQL query (with a few additional bits included) itself defined as a multi-line string.

def get_all_respositories(user_name):
    query_format = """
    { 
      user(login: "%s") {
        name
        url
        repositories (first:10 %s) {
          totalCount
          pageInfo {
            hasNextPage,
            endCursor
          },
          nodes {
            name
            url
          }
        }
      }
    }
    """
    repository_list = []
    query = query_format % (user_name, "")
    result = run_query(query)  # Execute the query
    if result == "Err":
        return

    totalCount = result["user"]["repositories"]["totalCount"]
    if totalCount > 0:
        repository_list = result["user"]["repositories"]["nodes"]
        hasNextPage = result["user"]["repositories"]["pageInfo"]["hasNextPage"]  # Drill down the dictionary
        while hasNextPage:
            endCursor = result["user"]["repositories"]["pageInfo"]["endCursor"]
            after_str = ", after: \"{}\"".format(endCursor)
            query = query_format % (user_name, after_str)
            result = run_query(query)
            hasNextPage = result["user"]["repositories"]["pageInfo"]["hasNextPage"]  # Drill down the dictionary
            repository_list = repository_list + result["user"]["repositories"]["nodes"]

    return repository_list


def get_last_commit(owner, branch):
    query_commit = """
    {
        repository(owner: "%s", name: "%s") {
            ref(qualifiedName: "master") {
                target {
                    ... on Commit {
                        history(first: 1) {
                            nodes {
                                oid
                                messageHeadline
                                author {
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """

    query = query_commit % (owner, branch)
    result = run_query(query)  # Execute the query
    if result == 'Err':
        return
    try:
        last_commit = {
            "messageHeadline": result['repository']['ref']['target']['history']['nodes'][0]["messageHeadline"],
            "author": result['repository']['ref']['target']['history']['nodes'][0]["author"]["name"]
        }
        return last_commit
    except:
        return


if __name__ == '__main__':
    base_path = os.path.dirname(os.path.abspath(__file__))
    owner_respo_dir = os.path.join(base_path, owner)
    try:
        os.makedirs(owner_respo_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    # Get all repositories of owner
    repositories = get_all_respositories(owner)
    # Get last commit for master branch
    print("*****ALL REPOSITORIES AND LAST COMMIT*****\n")
    commit_file_path = os.path.join(owner_respo_dir, "repo_commit.txt")
    commit_file = open(commit_file_path, "a")
    content = ""
    for repository in repositories:
        content_ = "{}---{}".format(repository["name"], get_last_commit(owner, repository["name"]))
        print(content_)
        content = content + '\n' + content_
    commit_file.write(content)
    commit_file.close()

    # Get recursive tree of repository as jason
    for repository in repositories:
        tree = RecursiveTreeV3(owner, repository["name"])
        tree_entries = tree.get_recursive_tree()

        try:
            for str_ in tree_entries['tree']:
                print(str_)
            print("\n\n*****RECURSIVE TREE ENTRIES*****\n")

            file_name = repository["name"] + '.json'
            file_path = os.path.join(owner_respo_dir, file_name)
            with open(file_path, 'w') as outfile:
                json.dump(tree_entries, outfile)
        except:
            continue
