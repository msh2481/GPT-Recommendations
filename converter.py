import xmltodict  # type: ignore
import random

with open("cue-target.xml", "r", encoding="utf-8") as f:
    assoc = xmltodict.parse(f.read())


for elem in next(iter(assoc.values()))["cue"]:
    cue = elem["@word"]
    for child in elem["target"]:
        try:
            target = child["@word"]
            fsg = child["@fsg"]
            print(f"{cue}\t{target}\t{fsg}")
        except:
            # print("something strange")
            # print(cue)
            # print(child)
            # break
            continue
