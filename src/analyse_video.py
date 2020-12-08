import cv2
from src.analyse_image import get_expected_result, compare
from progress.bar import Bar

def analyse_frames(video_path, frames, progress, gui):
    """
    Analyse the specified frames in the video for knocks/elims and record their timestamps

    :param video_path: The location of the video that needs to be processed
    :param frames: A list of ints which define the frames that need to be analysed
    :param progress: The progress bar which needs to be updated as the frames are analysed (progress.bar.Bar)
    :param gui: If there is a gui use it to update the progress. This for the GUI.
    :returns timestamps: A list of floats which represent the time of each knock/elimination
    """
    timestamps = []
    expected = get_expected_result() # This is what the hitmarker looks like for a valid knock/elim
    cap = cv2.VideoCapture(video_path)
    total = len(frames)
    for idx, fn in enumerate(frames):
        gui.update_progress("video", (idx / total) * 100, idx + 1, total)
        # Set the video to the corresponding frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, fn)
        success, image = cap.read()
        if success:
            # If the frame exists, compare the frame with the expected outcome
            # If it's valid, record the timestamp
            valid, score = compare(expected, image)
            if valid:
                timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)
        progress.next()
    cap.release()
    return timestamps

def get_timestamps(video_path, sample_rate, gui):
    """
    Finds the timestamps of each knock/elim

    :param video_path: The location of the video that needs to be processed
    :param gui: If there is a gui, update the progress on the GUI. This for the GUI.
    :returns timestamps: A list of floats which represent the time of each knock/elimination
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = list(range(0, frame_count, sample_rate))
    
    cap.release()
    
    progress = Bar('Processing', max=len(frames))
    timestamps = analyse_frames(video_path, frames, progress, gui) # The main function
    progress.finish()

    return timestamps
    