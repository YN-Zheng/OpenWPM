import ast
import sqlite3 as lite
import time
from collections import Counter, defaultdict

from utils import get_base_script_url

# 1. There should be both ToDataURL and fillText (or strokeText) method calls and both calls should come from the same URL.
# 2. The canvas image(s) read by the script should contain more than one color and its(their) aggregate size should be greater than 16x16 pixels.
# 3. The image should not be requested in a lossy compres-sion format such as JPEG.

CANVAS_SYMBOLS = {
    # canvas fp
    "HTMLCanvasElement.toDataURL",  # arguments ["image/webp"]
    "CanvasRenderingContext2D.fillText",  # arguments ["Cwm fjordbank glyphs vext quiz, 😃",4,45]; ["👨🏾‍🤝‍👨🏼",0,0]; ["👨🏾​🤝​👨🏼",0,0]
    "CanvasRenderingContext2D.fillStyle",  # operation: set value:
    "CanvasRenderingContext2D.font",  # operation: set ; value: 600 32px Arial
    "CanvasRenderingContext2D.fillRect",  # arguments: [898,322,2,2]
    "CanvasRenderingContext2D.save",
    "CanvasRenderingContext2D.restore",
    "CanvasRenderingContext2D.getImageData",  # arguments: [0,0,300,150]
}

AUDIO_SYMBOLS = {
    "OfflineAudioContext.createOscillator",
    "OfflineAudioContext.createDynamicsCompressor",
    "OfflineAudioContext.destination",
    "OfflineAudioContext.startRendering",
    "OfflineAudioContext.oncomplete",
}


def main():
    crawl_date = "Mar_1_2019"
    # connect to the output database
    openwpm_db = "data/%s/datadir/replay-crawl-data.sqlite" % crawl_date
    conn = lite.connect(openwpm_db)
    cur = conn.cursor()

    site_symbol = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    sites_canvas_fp = set()
    sites_audio_fp = set()
    scripts_canvas_fp = Counter()
    scripts_audio_fp = Counter()

    # scans through the database
    for script_url, symbol, operation, value, arguments, top_url in cur.execute(
        "SELECT j.script_url ,j.symbol, j.operation,j.value, j.arguments, v.site_url "
        "FROM javascript as j JOIN site_visits as v ON j.visit_id = v.visit_id "
        "where j.symbol like 'OfflineAudioContext%' OR j.symbol like 'CanvasRenderingContext2D%' OR j.symbol like 'HTMLCanvasElement%' "
        "ORDER BY j.time_stamp;"
    ):
        if symbol in AUDIO_SYMBOLS or symbol:
            if operation == "call":
                site_symbol[top_url][script_url][symbol].append(arguments)
            elif operation == "set" or operation == "get":
                site_symbol[top_url][script_url][symbol].append(value)

    for site, script_symbol in site_symbol.items():
        for script_url, symbol_args in script_symbol.items():
            if is_canvas_fp(symbol_args):
                sites_canvas_fp.add(site)
                scripts_canvas_fp[get_base_script_url(script_url)] += 1
            if is_audio_fp(symbol_args):
                sites_audio_fp.add(site)
                scripts_audio_fp[get_base_script_url(script_url)] += 1
    audio_canvas = sites_canvas_fp & sites_audio_fp

    # outputs the results

    print("\nDate: %s" % crawl_date)
    print("Canvas finger printing :%4d out of 10,000" % len(sites_canvas_fp))
    print("Audio finger printing : %4d out of 10,000" % len(sites_audio_fp))
    print("Both:                   %4d out of 10,000" % len(audio_canvas))

    print("\n--- Most common scripts for canvas fp: ---")
    for fp_script in scripts_canvas_fp.most_common(3):
        print(fp_script)
    print("\n--- Most common scripts for audio fp: ---")
    for fp_script in scripts_audio_fp.most_common(3):
        print(fp_script)


# https://www.cs.princeton.edu/~arvindn/publications/OpenWPM_1_million_site_tracking_measurement.pdf
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
            extracted = True
            break

    if not extracted:
        area = 0
        for arg in symbol_args["CanvasRenderingContext2D.getImageData"]:
            array = ast.literal_eval(arg)
            if not isinstance(array, list) or len(array) < 4:
                continue
            area += abs(array[3] * array[2])
        if area < 16 * 16:
            return False

    # 3. Text must be written to canvas with least two colors or at least 10 distinct characters.
    if len(symbol_args["CanvasRenderingContext2D.fillStyle"]) < 2:
        text_length = 0
        for arg in symbol_args["CanvasRenderingContext2D.fillText"]:
            text = ast.literal_eval(arg)[0]
            text_length = max(text_length, len(text.encode("ascii", "ignore")))
        if text_length < 10:
            return False

    # 4. The canvas element's height and width properties must not be set below 16 px.
    font_size = 0
    for arg in symbol_args["CanvasRenderingContext2D.font"]:
        # get %d from px
        font_args = arg.split(" ")
        for font_arg in font_args:
            if font_arg[-2:] == "px":
                font_size = float(font_arg[0:-2])
            elif font_arg[-2:] == "pt":
                font_size = float(font_arg[0:-2]) * 4 / 3
            if font_size > 16:
                return True
    return False


def is_audio_fp(symbol_args) -> bool:
    symbols = set(symbol_args.keys())
    return AUDIO_SYMBOLS.issubset(symbols)


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print("--- %s seconds ---" % (time.time() - start_time))
