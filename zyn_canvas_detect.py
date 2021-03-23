import math
import sqlite3 as lite
from zyn_test import read_log
from collections import defaultdict
import ast


# 1. There should be both ToDataURL and fillText (or strokeText) method calls and both calls should come from the same URL.
# 2. The canvas image(s) read by the script should contain more than one color and its(their) aggregate size should be greater than 16x16 pixels.
# 3. The image should not be requested in a lossy compres-sion format such as JPEG.

interesting_symbol = [
    "HTMLCanvasElement.toDataURL",  # arguments ["image/webp"]
    "CanvasRenderingContext2D.fillText",  # arguments ["Cwm fjordbank glyphs vext quiz, 😃",4,45]; ["👨🏾‍🤝‍👨🏼",0,0]; ["👨🏾​🤝​👨🏼",0,0]
    "CanvasRenderingContext2D.fillStyle",  # operation: set value:
    "CanvasRenderingContext2D.font",  # operation: set ; value: 600 32px Arial
    "CanvasRenderingContext2D.fillRect",  # arguments: [898,322,2,2]
    "CanvasRenderingContext2D.save",
    "CanvasRenderingContext2D.restore",
    "CanvasRenderingContext2D.getImageData",  # arguments: [0,0,300,150]
]


def main():
    # connect to the output database
    openwpm_db = "datadir/replay-crawl-data.sqlite"
    conn = lite.connect(openwpm_db)
    cur = conn.cursor()

    fp_sites = set()
    site_symbol = defaultdict(lambda: defaultdict(list))
    script_urls = set()
    # scans through the database
    for script_url, symbol, operation, value, arguments, top_url in cur.execute(
        "SELECT j.script_url ,j.symbol, j.operation,j.value, j.arguments, v.site_url "
        "FROM javascript as j JOIN site_visits as v ON j.visit_id = v.visit_id "
        "where j.symbol like 'CanvasRenderingContext2D%' OR j.symbol like 'HTMLCanvasElement%' "
        "ORDER BY j.time_stamp;"
    ):
        if symbol in interesting_symbol:
            if operation == "call":
                site_symbol[top_url][symbol].append(arguments)
            elif operation == "set":
                site_symbol[top_url][symbol].append(value)

    for site, symbol_args in site_symbol.items():
        if is_canvas_fp(symbol_args):
            fp_sites.add(site)

    # outputs the results
    print(fp_sites)


def is_canvas_fp(symbol_args) -> bool:
    # 1. No save or restore
    symbols = symbol_args.keys()
    if (
        "CanvasRenderingContext2D.save" in symbols
        or "CanvasRenderingContext2D.restore" in symbols
    ):
        return False
    # 2. The script extracts an image with toDataURL
    # or with a single call to getImageData that species an area with a minimum size of 16px * 16px.
    # The image should not be requested in a lossy compres-sion format such as JPEG.
    extracted = False
    for arg in symbol_args["HTMLCanvasElement.toDataURL"]:
        if arg != "image/webp" and arg != "image/jpeg":
            extracted == True

    if "HTMLCanvasElement.toDataURL" not in symbols:
        area = 0
        for arg in symbol_args["CanvasRenderingContext2D.getImageData"]:
            array = ast.literal_eval(arg)
            if not isinstance(array, list) or len(array) < 4:
                continue
            area = max(area, abs(array[3] * array[2]))
        if area < 16 * 16:
            return False

    # 3. Text must be written to canvas with least two colors or at least 10 distinct characters.
    elif len(symbol_args["CanvasRenderingContext2D.fillStyle"]) < 2:
        fill_text_length = 0
        for arg in symbol_args["CanvasRenderingContext2D.fillText"]:
            fill_text = ast.literal_eval(arg)[0]
            fill_text_length = max(fill_text_length, len(set(fill_text)))
        if fill_text_length < 10:
            return False

    # 4. The canvas element's height and width properties must not be set below 16 px.
    font_size = 0
    for arg in symbol_args["CanvasRenderingContext2D.font"]:
        # get %d from px
        font_args = arg.split(" ")
        for font_arg in font_args:
            if font_arg[-2:] == "px":
                font_size = max(font_size, float(font_arg[0:-2]))
    if font_size < 16:
        return False
    return True


if __name__ == "__main__":
    main()
