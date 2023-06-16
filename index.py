#!/usr/bin/env python3
import cv2
import sys, getopt, os

found = 0
chapters = []

class Chapter:
    start = 0
    end = 0

    def __repr__(self):
        return f"<start:{self.start} end:{self.end}>"

    def __str__(self):
        return f"<start is {self.start}, end is {self.end}>"


def find_all_chapters(frameArrays, fps):
    print('####### find_all_chapters')
    startTemplate = cv2.imread('common_frame_start.png',0)
    endTemplate = cv2.imread('common_frame_end.png',0)
    for frameArray in frameArrays:
        countFrame = 0
        for frame in frameArray:
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            matchStart = cv2.matchTemplate(frame_gray,startTemplate,cv2.TM_CCOEFF_NORMED)
            matchEnd = cv2.matchTemplate(frame_gray,endTemplate,cv2.TM_CCOEFF_NORMED)
            countFrame += 1
            if (matchStart > 0.8):
                print('## MATCH START !!!!! ', countFrame*20/fps)
                newChapter = Chapter()
                newChapter.start = round(countFrame*20/fps, 2)
            elif (matchEnd > 0.8):
                print('## MATCH END !!!!! ', countFrame*20/fps)
                newChapter.end = round(countFrame*20/fps, 2)
                chapters.append(newChapter)


def find_common_frames(frameArrayA, frameArrayB, fps):
    print('####### find_common_frames')
    commonFramesA = []
    commonFramesB = []
    commonFramesIndexA = []
    commonFramesIndexB = []
    countFrameA = 0

    for frameA in frameArrayA:
        firstFrame = False
        countFrameA += 1
        countFrameB = 0
        for frameB in frameArrayB:
            match = cv2.matchTemplate(frameB,frameA,cv2.TM_CCOEFF_NORMED)
            countFrameB += 1
            if (match > 0.8):
                print('## MATCH !!!!! ')
                commonFramesA.append(frameA)
                commonFramesB.append(frameB)
                commonFramesIndexA.append(countFrameA)
                commonFramesIndexB.append(countFrameB)

    startTimecodeA = commonFramesIndexA[0]*20/fps
    cv2.imwrite('common_frame_start.png',commonFramesA[0])
    # cv2.imwrite('common_frame_a_start-{0}.png'.format(round(startTimecodeA, 2)),commonFramesA[0])

    startTimecodeB = commonFramesIndexB[0]*20/fps
    # cv2.imwrite('common_frame_b_start-{0}.png'.format(round(startTimecodeB, 2)),commonFramesB[0])

    if (len(commonFramesA) > 1):
        endTimecodeA = commonFramesIndexA[len(commonFramesIndexA)-1]*20/fps
        cv2.imwrite('common_frame_end.png',commonFramesA[len(commonFramesA)-1])
        # cv2.imwrite('common_frame_a_end-{0}.png'.format(round(endTimecodeA, 2)),commonFramesA[len(commonFramesA)-1])

    if (len(commonFramesB) > 1):
        endTimecodeB = commonFramesIndexB[len(commonFramesIndexB)-1]*20/fps
        # cv2.imwrite('common_frame_b_end-{0}.png'.format(round(endTimecodeB, 2)),commonFramesB[len(commonFramesB)-1])

    newChapterA = Chapter()
    newChapterA.start = round(startTimecodeA, 2)
    newChapterA.end = round(endTimecodeA, 2)
    
    newChapterB = Chapter()
    newChapterB.start = round(startTimecodeB, 2)
    newChapterB.end = round(endTimecodeB, 2)

    # chapters = Chapters()
    chapters.append(newChapterA)
    chapters.append(newChapterB)

######
## inputDirectory : Folder path containing all the video files to compare (example: all saison episods)
## outputfile : 
def main(argv):
    print('####### main')
    inputDirectory = ''
    outputfile = ''
    opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    for opt, arg in opts:
        if opt == '-h':
            print ('autoFrameDetection.py -i <inputDirectory> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--input"):
            inputDirectory = arg
        elif opt in ("-o", "--output"):
            outputfile = arg

    directory = os.fsencode(inputDirectory)

    vidcap = []
    vidimg = []
    index = 0
    
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".mp4") or filename.endswith(".mov"):
            videoFileName = os.fsdecode(filename)
            videoFilePath = os.path.join(inputDirectory, '') + videoFileName
            print ('filePath : ', videoFilePath)
            videoImages = []
            vidcap.append(cv2.VideoCapture(videoFilePath))
            nbFrame = 0
            ######
            ## We convert videos in array of frames
            while 1:
                success,image = vidcap[index].read()
                if not success: break
                ######
                ## We don't keep all the frames because there would be too many
                ## TODO: maybe cv2 can do this for us
                if nbFrame % 20 == 0:
                    frame = cv2.resize(image,(1280,720),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
                    videoImages.append(frame)
                nbFrame += 1
            vidimg.append(videoImages)
            print('#### len(vidimg) : ', len(vidimg))
            index += 1

    fps = int(vidcap[0].get(cv2.CAP_PROP_FPS))
    ######
    ## Now that we got all frame reduced (otherwise we could get too many frames)
    ## We will compare the common frame between the two first video and save it
    find_common_frames(vidimg[0], vidimg[1], fps)

    if (len(vidimg) > 2):
        ######
        ## We will now compare all commonFrames (start and end) with other video
        ## That way we won't need to compare all the frames of every video 
        find_all_chapters(vidimg, fps)

    print('################')
    print('### Chapters ###')
    print(chapters)

main(sys.argv[1:])