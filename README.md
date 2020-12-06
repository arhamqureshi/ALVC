# Apex Legends Video Clipper
Automatically create clips of your knocks/elimations in your Apex Legends Gameplay!

## Purpose
It can get very tedious and time consuming scrolling through your gameplay to find knocks and eliminations. The purpose of this application is to save you time by automatically creating small clips of your knocks/eliminations.

## How It Works
The program analyses the frames in your gameplay recordings and looks for the big red hitmarker that appears when an enemy is knocked down or eliminated. The timestamp of each knock/elimination is recorded and then the video is split into clips of each knock/elimination found. 

**IMPORTANT**: You must enable hitmarkers in your gameplay settings or else the program will not detect any knocks/elims. At the moment the detection is only based on hitmarkers however the program may be improved to use other means of detection in the future.

## Program Settings
The following settings can be set in the program:

| Setting | Description |
|----------------|-------------|
|**Samples**|This value determines the amount of frames in the video that will be analysed for hitmarkers. The default value is 30, which means that every 30th frame in the video will be analysed. Lower values provide more accuracy, but increase the processing time. Higher values will lower the processing time, but will provide worse accuracy. The optimal value is half of your gameplay recording FPS. For example, if you record your gameplay at 60FPS you should set this value to 30.|
|**Seconds to Capture**|These two values determine how many seconds should be captured before and after the knock/elimination in the clip.|
|**Delete Original File**|If set to yes, the original gameplay video will be permanently deleted. You should keep this set to "No" unless you're absolutely sure you won't need the original video.|
|**Input & Output Folders**|The first directory should be where your gameplay recordings are stored and the second directory is where you want the clips to be saved. The program will analyse every compatible video in the input directory.|

#### Note
A file called ".alvc-settings.json" is created in your home directory (C:/Users/Your Profile) when launching the program for the first time. The purpose of this file is to store your settings so they don't change to the default values every time you launch the program.

### Cancelling The Process
Cancelling the process will only prevent the current and future videos from being processed, but all previous actions will not be reversed. The program makes changes as the process runs, so if the previous videos had been marked for deletion, they will be deleted and the program cannot reverse this.

### Supported File Formats
- MP4

## Issues
If you have encountered an issue with the program please create a [Bug Report](https://github.com/arhamqureshi/ALVC/issues/new/choose) in the Issues section of the GitHub Repository. Please provide as much information as you can including screenshots if possible!

## Support Me!
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=WALNKNVGR4L8S&currency_code=AUD)

