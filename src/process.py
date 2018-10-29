from pathlib import Path
import json
import re
import urllib.parse
import grequests
import time


def main():
    dictionary_filename = "efremova.txt"
    dictionary_json_filename = "data.json"
    file = Path(dictionary_json_filename)
    if file.is_file():
        start = time.time()
        analysis_dictionary_json_filename(dictionary_json_filename)
        end = time.time()
        print(end - start)
    else:
        create_dictionary_json_filename(dictionary_filename, dictionary_json_filename)


def analysis_dictionary_json_filename(dictionary_json_filename):
    dictionary = read_dictionary_json(dictionary_json_filename)

    urls = []
    for word, entry in dictionary.items():
        if (
                entry["is_noun_by_dictionary"] and
                entry["is_possible_adjective"] and
                entry["answer_from_wiktionary"] == "null"
        ):
            urls.append('https://ru.wiktionary.org/wiki/' + word)

    requests = (grequests.get(u) for u in urls)
    responses = grequests.map(requests)
    for response in responses:
        if response is not None:
            word = urllib.parse.unquote(response.url.rsplit("/", 1)[1])
            print('{} status_code = {}'.format(word, response.status_code))

            if response.status_code == 200:
                html = response.text
                is_noun_by_wiktionary = False
                if "title=\"существительное\">Существительное</a>" in html:
                    is_noun_by_wiktionary = True
                if "title=\"выступает в роли существительного\">субстантивир.</span>" in html:
                    is_noun_by_wiktionary = True

                if is_noun_by_wiktionary:
                    dictionary[word]["answer_from_wiktionary"] = True
                else:
                    print("is_noun_by_wiktionary = {}".format(is_noun_by_wiktionary))
            else:
                dictionary[word]["answer_from_wiktionary"] = response.status_code


        else:
            print("None")
        print("-------------------------")

    save_dictionary_json(dictionary, dictionary_json_filename)


def save_dictionary_json(dictionary, dictionary_json_filename):
    file = Path(dictionary_json_filename)
    if file.is_file():
        action_string = " updated"
    else:
        action_string = " created"
    with open(dictionary_json_filename, 'w', encoding='utf8') as outfile:
        json.dump(dictionary, outfile, ensure_ascii=False, indent=4)
    print('File ' + dictionary_json_filename + action_string)


def read_dictionary_json(dictionary_json_filename):
    dictionary = dict()
    file = Path(dictionary_json_filename)
    with open(file, encoding='utf8') as f:
        dictionary = json.loads(f.read())
    print('File ' + dictionary_json_filename + ' opened')
    return dictionary


def create_dictionary_json_filename(dictionary_filename, dictionary_json_filename):
    file = Path(dictionary_filename)
    if file.is_file():
        with open(file, encoding="utf8") as f:
            lines = f.read().splitlines()

        dictionary = dict()
        for line in lines:
            split_line = line.split(" ", 1)
            word = split_line[0]
            definition = split_line[1]

            is_noun_by_dictionary = False
            if re.match(r"(ж|м|ср|мн)\.(.*)$", definition) or re.match(r"(1\.|I) (ж|м|ср|мн)\.(.*)$", definition):
                is_noun_by_dictionary = True

            is_possible_adjective = False
            if (
                    word.endswith("ая") or
                    word.endswith("ее") or
                    word.endswith("ие") or
                    word.endswith("ий") or
                    word.endswith("ое") or
                    word.endswith("ой") or
                    word.endswith("ые") or
                    word.endswith("ый") or
                    word.endswith("ье") or
                    word.endswith("ьи") or
                    word.endswith("ья") or
                    word.endswith("яя")
            ):
                is_possible_adjective = True

            entry = dict()
            entry["definition"] = definition
            entry["is_noun_by_dictionary"] = is_noun_by_dictionary
            entry["is_possible_adjective"] = is_possible_adjective
            entry["answer_from_wiktionary"] = "null"
            dictionary[word] = entry

        save_dictionary_json(dictionary, dictionary_json_filename)
    else:
        print('File ' + dictionary_filename + ' not exists')


def test():
    pass


if __name__ == '__main__':
    main()