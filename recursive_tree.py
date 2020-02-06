from constAPI import *


class RecursiveTree:
    recursive_tree = []

    def __init__(self, owner, repo):
        self.owner = owner
        self.repo = repo

    def get_entries_byoid(self, oid):
        query_recursive = """
        {
            repository(owner: "%s", name: "%s") {
                object(oid: "%s") {
                    ... on Tree {
                        entries {
                            name
                            oid
                            type
                        }
                    }
                }
            }
        }
        """
        query = query_recursive % (self.owner, self.repo, oid)
        result = run_query(query)
        try:
            entries = result["repository"]["object"]["entries"]
            return entries
        except:
            pass
        return []

    # Call this function recursively, so make children tree elements get their own child
    def get_recursive(self, entries):
        for entry in entries:
            if ("type" in entry) and (entry["type"] == 'tree'):
                child_entries = self.get_entries_byoid(entry["oid"])
                entry['child'] = self.get_recursive(child_entries)
        return entries

    def get_tree(self):
        query_root = """
        {
            repository(owner: "%s", name: "%s") {
                defaultBranchRef {
                    target {
                    ... on Commit {
                            tree {
                                entries {
                                    name
                                    oid
                                    type
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        query = query_root % (self.owner, self.repo)
        result = run_query(query)
        entries = []
        try:
            entries = result["repository"]["defaultBranchRef"]["target"]["tree"]["entries"]
        except:
            return []
        entries = self.get_recursive(entries)
        return entries


class RecursiveTreeV3:
    def __init__(self, owner, repo):
        self.owner = owner
        self.repo = repo
        self.root_sha = ""

    def get_recursive_tree(self):
        query = "repos/%s/%s/branches/master" % (self.owner, self.repo)
        result = run_query_v3(query)
        self.root_sha = result["commit"]["sha"]
        return self.get_recursive()

    def get_recursive(self):
        query = "repos/%s/%s/git/trees/%s?recursive=1" % (self.owner, self.repo, self.root_sha)
        result = run_query_v3(query)
        return result


