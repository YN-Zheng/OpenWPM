pid: 2694401
## Replay
### TLS handshakes error
Due to Firefox's automatic connection to:
- location.services.mozilla.com
- firefox.settings.services.mozilla.com
- ...
Setting prefs is not enough to turn these off. So I will just skip this errors and make them disappear in replay.log

### Driver error (seems negligible)
many
```
2021-03-21 12:40:18,360 - MainProcess[log-interceptor-759609898]- selenium_firefox     - DEBUG   : BROWSER 759609898: driver: JavaScript error: resource://openwpm/privileged/stackDump/OpenWPMStackDumpChild.jsm, line 119: InvalidStateError: JSWindowActorChild.contentWindow getter: Cannot access property 'contentWindow' after actor 'OpenWPMStackDump' has been destroyed
```

A browser could crash:
```
2021-03-21 19:37:04,451 - MainProcess[Thread-11340]- task_manager         - INFO    : BROWSER 3078232822: Timeout while executing command, IntitializeCommand(), killing browser manager
```

During freeze:(After about 5,000 crawls at one time)
```
2021-03-21 19:38:34,507 - MainProcess[MainThread]- storage_controller   - DEBUG   : StorageController status: There are currently 0 scheduled tasks for 219 visit_ids
```


### Incomplete crawl

#### Summary
- InitializeCommand
    - timeout(10s)
- GetCommand:
    - timeout(60s)
    - error: selenium.common.exceptions.WebDriverException: Message: Failed to decode response from marionette
    - error: selenium.common.exceptions.InvalidSessionIdException: Message: Tried to run command without establishing a connection
    - error: "TypeError: 'Alert' object is not callable
    - neterror: connectionFailure
    - neterror: redirectLoop
- LinkCountingCommand
    - timeout(30s)
- FinalizeCommand
    - error: selenium.common.exceptions.JavascriptException: Message: TypeError: window.open is not a function
    - selenium.common.exceptions.InvalidSessionIdException: Message: Tried to run command without establishing a connection


- neterror: No response


## Analysis
### Canvas FP
1. The canvas element's height and width properties must not be set below 16 px. 12 
ctx.font = "16px 'Arial'";
ctx.fillRect(125,1,62,20);

2. Text must be written to canvas with least two colors or at least 10 distinct characters.
ctx.fillText(txt, 2, 15);
ctx.fillStyle = "#069";
ctx.shadowColor="blue";

3. The script should not call the save, restore, or addE-ventListener methods of the rendering context.
ctx.save()
ctx.restore()

4. The script extracts an image with toDataURL or with a single call to getImageData that species an area with a minimum size of 16px  16px.
getImageData([x,y,width,height])
HTMLCanvasElement.toDataURL[]  lossy: image/jpeg image/webp
```
CanvasRenderingContext2D.getImageData	call		[0,3,1,1]
CanvasRenderingContext2D.getImageData	call		[0,4,1,1]
CanvasRenderingContext2D.getImageData	call		[0,5,1,1]
...
CanvasRenderingContext2D.getImageData	call		[0,31,1,1]
```

### Replay
URL: Mar_1_2017