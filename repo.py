import requests
from constAPI import *
from recursive_tree import *
from findstring import *


# The GraphQL query (with a few aditional bits included) itself defined as a multi-line string.
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

    #Get all repositories of owner
    repositories = get_all_respositories(owner)

    # Get last commit for master branch
    print("*****ALL REPOSITORIES AND LAST COMMIT*****\n")
    for repository in repositories:
        print("{}---{}".format(repository["name"], get_last_commit(owner, repository["name"])))

    # Get recursive tree of repository as jason

    tree = RecursiveTree(owner, sample_repo)
    tree_entries = tree.get_tree()

    print("\n\n*****RECURSIVE TREE ENTRIES*****\n")
    for str_ in tree_entries:
        print(str_)

    print("\n\n*****SEARCH FILES BY REGULAR EXPRESSION*****(Sample expresion is {})\n".format(sample_regex))
    findString = FindString(owner, sample_repo, tree_entries, "repository:")
    search_regx = findString.search_byRegX(regX="^s")
    for str_ in search_regx:
        print(str_)

    print("\n\n*****SEARCH STRING IN FILES*****(Sample string is {})\n".format(sample_search_string))
    search_str = findString.search_string_in_file(sample_search_string)
    for str_ in search_str:
        print(str_)
