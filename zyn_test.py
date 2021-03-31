from typing import Counter
import unittest
from urllib.parse import urlparse
import utils
import collections

har_path = "/home/yongnian/HttpArchive/Mar_1_2020"
wprgo_path = "/home/yongnian/Programs/catapult/web_page_replay_go"
wprgo = utils.Wprgo(wprgo_path, har_path)


class TestStringMethods(unittest.TestCase):
    # def test_replay(self):
    #     for n in range(wprgo.total_number):
    #         wprgo.replay(n)

    # def test_replay_log(self):
    #     responses = utils.read_replay_log("Mar_1_2018")
    #     for response in responses.most_common():
    #         print(response)
    #     print("\n Unfound sites:")

    # success_index, group_num = utils.get_success_indexes("Jan_1_2018")

    # print(len(success_index))
    # for item in sorted(group_num.items()):
    #     print(item)

    def test_filename(self):
        print(utils.get_filename("Jan_1_2018", "hnsmall", 0))

    def test_requests(self):

        i = 0
        count = 0
        unfound, good, bad = utils.get_requests_by_status("Mar_1_2018")
        total_unfound = sum(unfound.values())
        total_good = sum(good.values())
        total_bad = sum(bad.values())
        total_count = total_unfound + total_bad + total_good
        print("----Count----")
        print("total_request:   %5d" % total_count)
        print("total_good:      %5d" % total_good)
        print("total_bad:       %5d" % total_bad)
        print("total_unfound:   %5d" % total_unfound)
        threshold = 0.9
        for r, c in unfound.most_common(300):
            count += c
            # found_rate = 1.0 * (total_count - total_unfound + count) / total_count
            found_rate = 1.0 * (count) / total_unfound
            print("%3d--%5d--%.2f--%s" % (i, c, found_rate, r))
            i += 1
            if found_rate > threshold:
                break
        print(
            "%.2f found-rate could be obtained by ignoring %d unfound request"
            % (found_rate, i)
        )
        print("----Set----")
        total_differnt_count = len(unfound) + len(good) + len(bad)
        print("total_different_request:   %5d" % total_differnt_count)
        print("total_different_good:      %5d" % len(good))
        print("total_different_bad:       %5d" % len(bad))
        print("total_different_unfound:   %5d" % len(unfound))
        # type of request path
        request_file_type = Counter()
        for r, c in unfound.items():
            if not isinstance(r, str):
                raise ValueError("Str!")

            if contains_tuple(r, (".png", ".jpg", ".gif", "jpeg", ".svg", "JPG")):
                request_file_type["image"] += c
            elif contains_tuple(r, (".ttf", ".woff")):
                request_file_type["font"] += c
            elif ".js" in r:
                request_file_type["js"] += c
            elif ".css" in r:
                request_file_type["css"] += c
            elif contains_tuple(r, ("firefox", "mozilla")):
                request_file_type["firefox"] += c
            else:
                request_file_type[r] += c
        for k, v in request_file_type.most_common(50):
            print("%6d--%.2f--%s" % (v, 1.0 * v / total_unfound, k))


def contains_tuple(s, matches):
    return any(x in s for x in matches)
    # at least one of the elements is a substring of some_string


if __name__ == "__main__":
    unittest.main()