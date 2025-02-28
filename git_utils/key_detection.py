import numpy as np
import ffmpy
from ffmpy import FFmpeg
import cv2
import os
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from skimage.segmentation import clear_border
from skimage.morphology import label
from string import ascii_lowercase

WB_key_len_ratio = 0.65
threshold = 0.8
wk_min_width = 15
gap_max = 7


def detect_keys(img_binary, img_binary_sobel, start_key):
    # get an array defining each key
    [whiteKeys, numWhiteKeys, white_notes] = detect_white_keys(img_binary_sobel, start_key)

    [blackKeys, numBlackKeys, black_notes] = detect_black_keys(img_binary, start_key)

    return whiteKeys, numWhiteKeys, blackKeys, numBlackKeys, white_notes, black_notes


# detect white keys on the binary sobel image
def detect_white_keys(im_bw, startKey):
    imheight = im_bw.shape[0]

    im_bottom = im_bw[int(imheight - (imheight / 5)):imheight, :]
    cv2.imwrite("./data/im_bottom.jpg", im_bottom)
    cv2.imshow("im_bot", im_bottom)
    cv2.waitKey(0)
    [gap_width, wk_width, start] = findAverageWidths(im_bottom)
    print("average_widths")
    print(gap_width, wk_width, start)

    print("image bottom shape", im_bottom.shape)
    [numWhiteKeys, whiteKeys] = workTowardRight(start, wk_width, gap_width, im_bottom.shape[1], imheight)
    [numWhiteKeys, whiteKeys] = workTowardLeft(whiteKeys, numWhiteKeys, start, wk_width, gap_width, imheight)

    sorted_white_keys = organizeWhiteKeys(whiteKeys)

    white_notes = getWhiteNotes(startKey, sorted_white_keys)

    return sorted_white_keys, numWhiteKeys, white_notes


# gather a few sample keys to find the average width of a white key and ave width of key gap
def findAverageWidths(im_bottom):
    widths = []
    start = int(im_bottom.shape[1] / 3)
    start_edge = start
    pixel = start
    firstKey = True
    numSampleKeys = 0
    gap_sizes = []
    numGaps = 0
    while numSampleKeys < 5:
        if firstKey == True:
            # if starting in middle of key, move to closest start next key
            if im_bottom[int(im_bottom.shape[0] / 2), pixel] < threshold:
                while im_bottom[
                    int(im_bottom.shape[0] / 2), pixel] < threshold:  # move to end of the key you're in the middle of
                    pixel += 1
                pixel = movePastBoundaryAndGap(im_bottom, pixel, threshold)
                start = pixel
                start_edge = pixel
            else:  # if starting in the middle of a gap between keys, move to closest start of next key
                pixel = movePastBoundaryAndGap(im_bottom, pixel, threshold)
                start = pixel
                start_edge = pixel

            firstKey = False
        else:
            pixel = moveThroughKey(im_bottom, pixel, threshold)

            if (abs(start_edge - pixel) > wk_min_width):  # if you detected a key
                widths.append(abs(start_edge - pixel))

                numSampleKeys += 1
                # move past white-black-white gap to get to next key
                gap_size = 0

                while im_bottom[int(im_bottom.shape[0] / 2), pixel] < threshold:
                    if gap_size > gap_max:
                        break
                    else:
                        gap_size += 1
                        pixel += 1

                gap_sizes.append(gap_size)
                numGaps += 1
                start_edge = pixel
            else:
                # move past white blip that made program think it might have been at end of key
                while im_bottom[int(im_bottom.shape[0] / 2), pixel] > threshold:
                    pixel += 1

    gap_width = sum(gap_sizes) / numGaps
    wk_width = sum(widths) / numSampleKeys

    return gap_width, wk_width, start


def movePastBoundaryAndGap(im_bottom, pixel, threshold):
    beginning = pixel
    while abs(beginning - pixel) < gap_max:
        while im_bottom[int(im_bottom.shape[0] / 2), pixel] > threshold:  # move past white edge
            pixel += 1
        while im_bottom[int(im_bottom.shape[0] / 2), pixel] < threshold:  # move past black gap
            pixel += 1
    return pixel


def moveThroughKey(im_bottom, pixel, threshold):
    while im_bottom[int(im_bottom.shape[0] / 2), pixel] > threshold:  # start white edge
        pixel += 1
    while im_bottom[int(im_bottom.shape[0] / 2), pixel] < threshold:  # move past black middle
        pixel += 1
    while im_bottom[int(im_bottom.shape[0] / 2), pixel] > threshold:  # end white edge
        pixel += 1
    return pixel


# correlate each key with its note based on the left-most-note passed in
def getWhiteNotes(startKey, whiteKeys):
    whiteNoteString = "A0B0C1D1E1F1G1A1B1C2D2E2F2G2A2B2C3D3E3F3G3A3B3C4D4E4F4G4A4B4C5D5E5F5G5A5B5C6D6E6F6G6A6B6C7D7E7F7G7A7B7C8"
    offset = whiteNoteString.find(startKey)
    white_notes = []
    for i in range(0, whiteKeys.shape[0] * 2, 2):
        white_notes.append(whiteNoteString[i + offset: i + offset + 2])

    return white_notes


# get rid of empty rows and sort key regions
def organizeWhiteKeys(whiteKeys):
    nonzero_row_indices = []
    zeros = np.zeros((4, 1))

    # remove rows that are all 0's
    print(whiteKeys.shape[0])
    for i in range(0, whiteKeys.shape[0]):
        if not np.array_equal(whiteKeys[i, :].reshape(4, 1), zeros):
            nonzero_row_indices.append(i)

    whiteKeys = whiteKeys[nonzero_row_indices, :]
    ind = np.argsort(whiteKeys[:, 2])
    sorted_white_keys = whiteKeys[ind]

    return sorted_white_keys


# from the first detected edge in the middle of the keyboard, mark regions going right
def workTowardRight(start_edge, wk_width, gap_width, imwidth, imheight):
    whiteKeys = np.zeros((52, 4))
    last_edge = start_edge
    numWhiteKeys = 1
    first_edge = start_edge

    print("workTowardRight")
    print("start edge", start_edge)


    while first_edge < (imwidth - gap_width):  # work across the photo towards the right
        if numWhiteKeys < 52:
            first_edge = last_edge + gap_width
            print("numWhiteKeys", numWhiteKeys - 1)
            whiteKeys[numWhiteKeys - 1][0] = 0
            whiteKeys[numWhiteKeys - 1][1] = imheight
            whiteKeys[numWhiteKeys - 1][2] = first_edge
            last_edge = first_edge + wk_width
            whiteKeys[numWhiteKeys - 1][3] = last_edge
            numWhiteKeys += 1
        else:
            break
    # get the last key
    whiteKeys[numWhiteKeys - 1][0] = 0
    whiteKeys[numWhiteKeys - 1][1] = imheight
    whiteKeys[numWhiteKeys - 1][2] = first_edge
    whiteKeys[numWhiteKeys - 1][3] = imwidth
    return numWhiteKeys, whiteKeys


# from the same first detected edge in the middle of the keyboard, mark regions going left
def workTowardLeft(whiteKeys, numWhiteKeys, start_edge, wk_width, gap_width, imheight):
    last_edge = start_edge
    first_edge = start_edge
    while first_edge > wk_width + gap_width:  # work across the photo towards the left
        if numWhiteKeys < 52:
            last_edge = first_edge - gap_width

            whiteKeys[numWhiteKeys - 1][0] = 0
            whiteKeys[numWhiteKeys - 1][1] = imheight
            whiteKeys[numWhiteKeys - 1][3] = last_edge
            first_edge = last_edge - wk_width
            whiteKeys[numWhiteKeys - 1][2] = first_edge
            numWhiteKeys += 1
        else:
            break
    # get the last key
    whiteKeys[numWhiteKeys - 1][0] = 0
    whiteKeys[numWhiteKeys - 1][1] = imheight
    whiteKeys[numWhiteKeys - 1][2] = 0
    whiteKeys[numWhiteKeys - 1][3] = first_edge - gap_width
    return numWhiteKeys, whiteKeys


# detect black keys on the binary image
def detect_black_keys(im_bw, start_key):
    white_key_len = im_bw.shape[0]
    im_top = im_bw[0:int(white_key_len / 2), :]
    [blackKeys, numBlackKeys] = get_black_key_boundaries(white_key_len, im_top)

    nonzero_row_indices = []
    zeros = np.zeros((4, 1))
    # remove rows that are all 0's
    for i in range(0, blackKeys.shape[0]):
        if not np.array_equal(blackKeys[i, :].reshape(4, 1), zeros):
            nonzero_row_indices.append(i)

    blackKeys = blackKeys[nonzero_row_indices, :]

    # sort by x-axis min bound just in case something went wrong
    ind = np.argsort(blackKeys[:, 2])
    blackKeys = blackKeys[ind]

    black_notes = []

    blackNoteString = "a0c1d1f1g1a1c2d2f2g2a2c3d3f3g3a3c4d4f4g4a4c5d5f5g5a5c6d6f6g6a6c7d7f7g7a7"
    offset = blackNoteString.find(start_key)
    if offset == -1:  # if the start white key did not have a black key to its right
        found = ascii_lowercase.find(start_key[0])
        nextBlackKey = ascii_lowercase[found + 1] + start_key[1]
        offset = blackNoteString.find(nextBlackKey)

    if im_top[im_top.shape[0] - 1, 0] > threshold:  # if the edge doesn't start with a black key
        for i in range(0, blackKeys.shape[0] * 2, 2):
            black_notes.append(blackNoteString[
                               i + offset - 2: i + offset])  # first black key will be the sharp following first white key
    else:  # if edge starts with black key
        for i in range(0, blackKeys.shape[0] * 2, 2):
            black_notes.append(
                blackNoteString[i + offset: i + offset + 2])  # first black key will be the sharp before first white key

    return blackKeys, numBlackKeys, black_notes


# scan across image to collect black key regions
def get_black_key_boundaries(white_key_len, im_top):
    blackKeys = np.zeros((36, 4))
    numBlackKeys = 0

    start = True
    start_edge = 0
    pixel = start_edge
    while pixel < im_top.shape[1]:
        if start:  # only do this for the first key
            if im_top[im_top.shape[0] - 1, 0] > threshold:  # if the edge doesn't start with a black key
                while im_top[im_top.shape[0] - 1, pixel] > threshold:  # move past white space
                    pixel += 1
                start_edge = pixel  # set start edge of first black key

        # mark region of black key
        blackKeys[numBlackKeys - 1][0] = 0
        blackKeys[numBlackKeys - 1][1] = white_key_len * WB_key_len_ratio
        blackKeys[numBlackKeys - 1][2] = start_edge

        # move through black region
        while im_top[im_top.shape[0] - 1, pixel] < threshold:
            if pixel < im_top.shape[1] - 1:
                pixel += 1
            else:
                blackKeys[numBlackKeys - 1][3] = pixel
                numBlackKeys += 1
                return blackKeys, numBlackKeys

        if abs(pixel - start_edge) > 15:
            blackKeys[numBlackKeys - 1][3] = pixel
            numBlackKeys += 1

        else:  # if this isn't actually the end of the key but a blip of white pixels interrupting key,
            # move past blip
            while im_top[im_top.shape[0] - 1, pixel] > threshold:
                if pixel < im_top.shape[1] - 1:
                    pixel += 1
                else:
                    return blackKeys, numBlackKeys

            # find the actual end of the key
            while im_top[im_top.shape[0] - 1, pixel] < threshold:
                if pixel < im_top.shape[1] - 1:
                    pixel += 1
                else:
                    blackKeys[numBlackKeys - 1][3] = pixel
                    numBlackKeys += 1
                    return blackKeys, numBlackKeys

            blackKeys[numBlackKeys - 1][3] = pixel
            numBlackKeys += 1

        # move past white space
        while im_top[im_top.shape[0] - 1, pixel] > threshold:
            if pixel < im_top.shape[1] - 1:
                pixel += 1
                start_edge = pixel
            else:
                return blackKeys, numBlackKeys

    return blackKeys, numBlackKeys