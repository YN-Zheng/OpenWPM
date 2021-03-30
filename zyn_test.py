import unittest
import utils
import collections

har_path = "/home/yongnian/HttpArchive/Mar_1_2020"
wprgo_path = "/home/yongnian/Programs/catapult/web_page_replay_go"
wprgo = utils.Wprgo(wprgo_path, har_path)


class TestStringMethods(unittest.TestCase):
    # def test_replay(self):
    #     for n in range(wprgo.total_number):
    #         wprgo.replay(n)

    def test_log(self):
        responses = utils.read_replay_log("Mar_1_2019")
        for response in responses.most_common():
            print(response)
        success_index = utils.get_success_indexes("Mar_1_2020")
        print(len(success_index))


if __name__ == "__main__":
    unittest.main()