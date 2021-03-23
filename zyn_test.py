import unittest
import utils
import collections

har_path = "/home/yongnian/HttpArchive/Mar_1_2020"
wprgo_path = "/home/yongnian/Programs/catapult/web_page_replay_go"
wprgo = utils.Wprgo(wprgo_path, har_path)


class TestStringMethods(unittest.TestCase):
    def test_replay(self):
        for n in range(wprgo.total_number):
            wprgo.replay(n)

    def test_duplicate_sites(self):
        c = set()
        a = set()
        for n in range(wprgo.total_number):
            sites = wprgo.get_hostnames(n)
            print("list len: %d" % len(sites))
            c = c.union(
                {
                    item
                    for item, count in collections.Counter(sites).items()
                    if count > 1
                }
            )
            a = a.union(set(sites))
        print(len(a))
        if len(a) != 10000:
            print("Duplicate hostnames:%s" % c)

    def test_log(self):
        sites = set(wprgo.get_hostnames(0))
        sites_success, sites_unsuccess = read_log()
        print("\nTotal sites:%d" % len(sites))
        print("Total success in the log:%d" % len(sites_success))
        print("Total unsuccess in the log:%d" % len(sites_unsuccess))
        s = sites - sites_unsuccess - sites_success
        print("Not in the log: %d" % len(s))
        print(s)
        total_difference = (sites_success | sites_unsuccess) - sites
        s = sites_success & total_difference
        print("Success but not in the list: %d" % len(s))
        print(s)
        s = sites_unsuccess & total_difference
        print("Unsuccess but not in the list: %d" % len(s))
        print(s)
        s = sites_unsuccess & sites_success
        print("Unsuccess and success: %d" % len(s))
        print(s)


def read_log():
    with open("nohup.out") as file_in:
        sites_success = set()
        sites_unsuccess = set()

        for line in file_in:
            if line.startswith("CommandSequence for "):
                end_index = line.rfind(" ran ")
                if line[end_index + 5] == "s":
                    sites_success.add(line[20:end_index])
                else:
                    sites_unsuccess.add(line[20:end_index])

    return sites_success, sites_unsuccess


if __name__ == "__main__":
    unittest.main()