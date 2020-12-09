from src.analyse_video import get_timestamps
from src.analyse_image import resource_path
import os, sys, subprocess

def analyse_timestamps(timestamps):
    """
    Anlyses the timestamps to ensure that each timestamp corresponds to a unique knock/elim. 
    This is done by checking to see if the difference between the next timestamp is > 0.8 seconds 
    (roughly the amount of time it takes for the hit marker to disappear).

    :param timestamps: A list of floats which represent the time of each knock/elimination
    :returns adjusted_timestamps: A list of floats which represent the time of each knock/elimination
    """
    adjusted_timestamps = []
    for idx, t in enumerate(timestamps):
        if idx < len(timestamps) - 1:
            diff = (timestamps[idx+1] - t)
            if diff > 0.8:
                adjusted_timestamps.append(round(t, 2))
        else:
            adjusted_timestamps.append(round(t, 2))
    return adjusted_timestamps

def ffmpeg_extract_subclip(inputfile, start_time, end_time, outputfile=None, logger=None):
    """
    ===============================================================
    THIS FUNCTION HAS BEEN COPIED FROM MOVIEPY AND MODIFIED
    https://github.com/Zulko/moviepy/blob/4185e51c82dd8f239b2ade5aca0991b85ab08bd0/moviepy/video/io/ffmpeg_tools.py#L11
    
    The original function had an issue where the clip created did not cut on key frames which 
    caused unexpected freezing at either the start or the end of the clip. This issue has been 
    resolved with the changes made to the function.
    ===============================================================
    Makes a new video file playing video file ``inputfile`` between
    the times ``start_time`` and ``end_time``.
    """
    name, ext = os.path.splitext(inputfile)
    if not outputfile:
        T1, T2 = [int(1000 * t) for t in [start_time, end_time]]
        outputfile = "%sSUB%d_%d%s" % (name, T1, T2, ext)

    cmd = [
        resource_path("ffmpeg.exe"),
        "-noaccurate_seek",
        "-ss",
        "%0.2f" % start_time,
        "-i",
        inputfile,
        "-t",
        "%0.2f" % (end_time - start_time),
        "-vcodec",
        "copy",
        "-acodec",
        "copy",
        "-avoid_negative_ts",
        "make_zero",
        outputfile,
    ]
    proc = subprocess.Popen(cmd, shell=False, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
    proc.communicate()

    del proc

def create_clips(input_dir, filename, output_dir, merge=False, pre=2, post=0.8, sample_rate=30, delete=False, gui=None):
    """
    Creates short clips of each knock/elim in the gameplay. The clip length is determined by `pre` and `post`.

    :param input_dir: Path of the directory where the video is location
    :param filename: Name of the video file to be analysed
    :param output_dir: The directory where the clips should be saved
    :param merge: If True, merge all the clips into one. Default Value: False
    :param pre: In seconds, how much gameplay should be captured before the knock/elim
    :param post: In seconds, how much gameplay should be captured after the knock/elim
    :param delete: If True, delete the original file after process is complete. Default Value: False
    :param gui: If there is a gui, update the progress on the GUI. Default Value: None
    :returns: Does not return anything
    """
    path = os.path.join(input_dir, filename)
    timestamps = analyse_timestamps(get_timestamps(path, sample_rate, gui))
    gui.knocks_elims_found = gui.knocks_elims_found + len(timestamps)
    gui.update_progress("knocks_elims", 0, 0, 0) # All values are 0 because this is handled differently
    
    for idx, timestamp in enumerate(timestamps):
        start_time = timestamp - pre if timestamp - pre > 0 else 0
        end_time = timestamp + post
        out = "{}/{}-{}.mp4".format(output_dir, filename.split(".mp4")[0], idx)
        if os.path.isfile(out):
            os.remove(out)

        # Extract clip and save it
        ffmpeg_extract_subclip(path, start_time, end_time, outputfile=out)

    if delete:
        os.remove(path)
