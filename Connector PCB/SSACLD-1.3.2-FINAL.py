import spidev
import RPi.GPIO as GPIO
import numpy as np
import cv2
import sys
import os
import glob
import time

# General settings
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
list_of_gpio_devices = [4, 15, 18, 17, 27, 23, 22, 24, 12, 6, 13, 16, 19, 20, 26, 21]

module_pixel_height = 16
module_pixel_width = 16


def detect_modules_and_validate():
    GPIO.setup(list_of_gpio_devices, GPIO.IN, GPIO.PUD_DOWN)

    list_of_detected_modules = []
    for i in range(16):
        status_spi_device = GPIO.input(list_of_gpio_devices[i])
        list_of_detected_modules.append(status_spi_device)

    resolution_code = 0
    for i in range(16):
        resolution_code = 2 * resolution_code + list_of_detected_modules[i]

    if resolution_code == 32768:
        detected_width_m, detected_height_m = 1, 1
    elif resolution_code == 49152:
        detected_width_m, detected_height_m = 2, 1
    elif resolution_code == 57344:
        detected_width_m, detected_height_m = 3, 1
    elif resolution_code == 61440:
        detected_width_m, detected_height_m = 4, 1
    elif resolution_code == 34816:
        detected_width_m, detected_height_m = 1, 2
    elif resolution_code == 34944:
        detected_width_m, detected_height_m = 1, 3
    elif resolution_code == 34952:
        detected_width_m, detected_height_m = 1, 4
    elif resolution_code == 52224:
        detected_width_m, detected_height_m = 2, 2
    elif resolution_code == 60928:
        detected_width_m, detected_height_m = 3, 2
    elif resolution_code == 65280:
        detected_width_m, detected_height_m = 4, 2
    elif resolution_code == 52416:
        detected_width_m, detected_height_m = 2, 3
    elif resolution_code == 61152:
        detected_width_m, detected_height_m = 3, 3
    elif resolution_code == 65520:
        detected_width_m, detected_height_m = 4, 3
    elif resolution_code == 52428:
        detected_width_m, detected_height_m = 2, 4
    elif resolution_code == 61166:
        detected_width_m, detected_height_m = 3, 4
    elif resolution_code == 65535:
        detected_width_m, detected_height_m = 4, 4
    else:
        print("Didn't detected any connected modules or incorrect setup")
        GPIO.cleanup()
        sys.exit()

    return list_of_detected_modules, detected_width_m, detected_height_m


def spi_setup():
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 4000000
    GPIO.setup(list_of_gpio_devices, GPIO.OUT)
    GPIO.output(list_of_gpio_devices, GPIO.HIGH)
    return spi


def read_frame(source_path):
    try:
        frame = cv2.imread(source_path)
        array = np.array(frame)
        b, g, r = np.split(array, 3, axis=2)

        r = r.reshape(-1)
        g = g.reshape(-1)
        b = b.reshape(-1)

        r = r.tolist()
        g = g.tolist()
        b = b.tolist()

        return r, g, b
    except:
        print("\nInvalid input. Try again.\n")
        main()


def validate_image_resolution(frame, width_m, height_m):

    image_height, image_width, channels = frame.shape

    if image_width == module_pixel_width * width_m and image_height == module_pixel_height * height_m:
        print("Resolutions match. Image will be displayed.")
        return True
    else:
        print("Resolutions don't match. Image will be converted and then displayed.")
        return False


def validate_video_resolution(frame, width_m, height_m):

    video_height = frame.get(cv2.CAP_PROP_FRAME_HEIGHT)
    video_width = frame.get(cv2.CAP_PROP_FRAME_WIDTH)

    if video_width == module_pixel_width * width_m and video_height == module_pixel_height * height_m:
        print("Resolutions match. Image will be displayed.")
        return True
    else:
        print("Resolutions don't match. Image will be converted and then displayed.")
        return False


def resize_image(source_path, targeted_width_m, targeted_height_m):
    new_size = (targeted_width_m * module_pixel_width, targeted_height_m * module_pixel_height)

    exists = os.path.exists('converted')
    if exists:
        files = glob.glob('converted/*')
        for i in files:
            os.remove(i)
    elif not exists:
        os.mkdir('converted')

    image = cv2.imread(source_path)

    try:
        resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_NEAREST)
        print("Converted image.")
    except:
        print("All converted.")

    resized_image_path = 'converted/image.bmp'
    cv2.imwrite(resized_image_path, resized_image)

    return None


def resize_video(source_path, targeted_width_m, targeted_height_m):
    new_size = (targeted_width_m * module_pixel_width, targeted_height_m * module_pixel_height)

    exists = os.path.exists('converted')
    if exists:
        files = glob.glob('converted/*')
        for i in files:
            os.remove(i)
    elif not exists:
        os.mkdir('converted')

    video_cap = cv2.VideoCapture(source_path)
    success, image = video_cap.read()
    resized_image_path = 'converted/frame0.bmp'
    try:
        resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_NEAREST)
        cv2.imwrite(resized_image_path, resized_image)
    except Exception as e:
        print(str(e))
    frame_number = 1
    if success:
        print("Converting. Please wait...")
    while success:
        success, image = video_cap.read()
        resized_image_path = 'converted/frame' + str(frame_number) + '.bmp'
        try:
            resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_NEAREST)
            cv2.imwrite(resized_image_path, resized_image)
        except:
            print("All converted.")

        frame_number += 1

    return None


def convert_to_bmp(source_path):
    exists = os.path.exists('converted')
    if exists:
        files = glob.glob('converted/*')
        for i in files:
            os.remove(i)
    elif not exists:
        os.mkdir('converted')

    video_cap = cv2.VideoCapture(source_path)
    success, image = video_cap.read()
    image_path = 'converted/frame0.bmp'
    try:
        cv2.imwrite(image_path, image)
    except Exception as e:
        print(str(e))
    frame_number = 1
    if success:
        print("Converting. Please wait...")
    while success:
        success, image = video_cap.read()
        image_path = 'converted/frame' + str(frame_number) + '.bmp'
        try:
            cv2.imwrite(image_path, image)
        except:
            print("All converted.")

        frame_number += 1

    return None


def split_frame_for_each_module(list_of_detected_modules, r, g, b):
    data_for_modules = []
    n = 0
    for i in range(4):
        r_0_data, g_0_data, b_0_data = [], [], []
        r_1_data, g_1_data, b_1_data = [], [], []
        r_2_data, g_2_data, b_2_data = [], [], []
        r_3_data, g_3_data, b_3_data = [], [], []

        for j in range(16):
            if list_of_detected_modules[i * 4 + 0] == 1:
                r_0, g_0, b_0 = [], [], []
                for k in range(16):
                    r_0.append(r[n + k])
                    g_0.append(g[n + k])
                    b_0.append(b[n + k])
                r_0_data = r_0_data + r_0
                g_0_data = g_0_data + g_0
                b_0_data = b_0_data + b_0
                n = n + 16

            if list_of_detected_modules[i * 4 + 1] == 1:
                r_1, g_1, b_1 = [], [], []
                for k in range(16):
                    r_1.append(r[n + k])
                    g_1.append(g[n + k])
                    b_1.append(b[n + k])
                r_1_data = r_1_data + r_1
                g_1_data = g_1_data + g_1
                b_1_data = b_1_data + b_1
                n = n + 16

            if list_of_detected_modules[i * 4 + 2] == 1:
                r_2, g_2, b_2 = [], [], []
                for k in range(16):
                    r_2.append(r[n + k])
                    g_2.append(g[n + k])
                    b_2.append(b[n + k])
                r_2_data = r_2_data + r_2
                g_2_data = g_2_data + g_2
                b_2_data = b_2_data + b_2
                n = n + 16

            if list_of_detected_modules[i * 4 + 3] == 1:
                r_3, g_3, b_3 = [], [], []
                for k in range(16):
                    r_3.append(r[n + k])
                    g_3.append(g[n + k])
                    b_3.append(b[n + k])
                r_3_data = r_3_data + r_3
                g_3_data = g_3_data + g_3
                b_3_data = b_3_data + b_3
                n = n + 16
        data_for_modules.extend((r_0_data + g_0_data + b_0_data, r_1_data + g_1_data + b_1_data, r_2_data + g_2_data +
                                 b_2_data, r_3_data + g_3_data + b_3_data))
    return data_for_modules


def send_data(spi, list_of_detected_modules, data_for_modules):
    for i in range(len(list_of_gpio_devices)):
        if list_of_detected_modules[i] == 1:
            start = time.time()
            GPIO.output(list_of_gpio_devices[i], GPIO.LOW)
            spi.writebytes(data_for_modules[i])
            GPIO.output(list_of_gpio_devices[i], GPIO.HIGH)
            stop = time.time()
            print(stop-start)
    return None


def display_image(spi, list_of_detected_modules, detected_width_m, detected_height_m):
    source_path = str(input("\nEnter path to image:\n\n>>> "))
    exist_source_path = os.path.exists(source_path)
    if exist_source_path:
        start = time.time()
        r, g, b = read_frame(source_path)
        frame = cv2.imread(source_path)
        resolutions_match = validate_image_resolution(frame, detected_width_m, detected_height_m)
        if resolutions_match:
            data_for_modules = split_frame_for_each_module(list_of_detected_modules, r, g, b)
            send_data(spi, list_of_detected_modules, data_for_modules)
        elif not resolutions_match:
            resize_image(source_path, detected_width_m, detected_height_m)
            r, g, b = read_frame('converted/image.bmp')
            data_for_modules = split_frame_for_each_module(list_of_detected_modules, r, g, b)
            send_data(spi, list_of_detected_modules, data_for_modules)
        stop = time.time()
        print(stop - start)
    else:
        print("File don't exist.")
        select_action(spi, list_of_detected_modules, detected_width_m, detected_height_m)


def display_video(spi, list_of_detected_modules, detected_width_m, detected_height_m):
    try:
        delay = float(input("Enter delay:\n>>> "))
    except:
        print("Invalid input. Try again.")
        select_action(spi, list_of_detected_modules, detected_width_m, detected_height_m)

    is_converted = str(input("Is video / GIF already converted? Yes / No:\n>>> "))
    if is_converted == 'yes' or is_converted == 'y' or is_converted == 'Yes' or is_converted == 'Y':
        frame_path = 'converted/frame0.bmp'
        exist_frame_path = os.path.exists(frame_path)
        if exist_frame_path:
            frame = cv2.imread(frame_path)
            resolution_match = validate_image_resolution(frame, detected_width_m, detected_height_m)
            if resolution_match:
                number_of_frames = os.listdir('converted')
                number_of_frames = len(number_of_frames)
                while True:
                    for i in range(number_of_frames):
                        #start = time.time()
                        frame_path = 'converted/frame' + str(i) + '.bmp'
                        r, g, b = read_frame(frame_path)
                        data_for_modules = split_frame_for_each_module(list_of_detected_modules, r, g, b)
                        send_data(spi, list_of_detected_modules, data_for_modules)
                        time.sleep(delay)
                        #stop = time.time()
                        #print(stop - start)
            elif not resolution_match:
                print("Resolutions don't match.")
                select_action(spi, list_of_detected_modules, detected_width_m, detected_height_m)
        else:
            print('Converted video / GIF not found.')
            select_action(spi, list_of_detected_modules, detected_width_m, detected_height_m)

    elif is_converted == 'no' or is_converted == 'n' or is_converted == 'No' or is_converted == 'N':
        source_path = str(input("Enter path to video / GIF:\n>>> "))
        exist_source_path = os.path.exists(source_path)
        if exist_source_path:
            video_cap = cv2.VideoCapture(source_path)
            resolution_match = validate_video_resolution(video_cap, detected_width_m, detected_height_m)
            if resolution_match:
                convert_to_bmp(source_path)
                number_of_frames = os.listdir('converted')
                number_of_frames = len(number_of_frames)
                while True:
                    for i in range(number_of_frames):
                        start = time.time()
                        frame_path = 'converted/frame' + str(i) + '.bmp'
                        r, g, b = read_frame(frame_path)
                        data_for_modules = split_frame_for_each_module(list_of_detected_modules, r, g, b)
                        send_data(spi, list_of_detected_modules, data_for_modules)
                        time.sleep(delay)
                        stop = time.time()
                        print(stop - start)

            elif not resolution_match:
                resize_video(source_path, detected_width_m, detected_height_m)
                number_of_frames = os.listdir('converted')
                number_of_frames = len(number_of_frames)
                while True:
                    for i in range(number_of_frames):
                        start = time.time()
                        frame_path = 'converted/frame' + str(i) + '.bmp'
                        r, g, b = read_frame(frame_path)
                        data_for_modules = split_frame_for_each_module(list_of_detected_modules, r, g, b)
                        send_data(spi, list_of_detected_modules, data_for_modules)
                        time.sleep(delay)
                        stop = time.time()
                        print(stop - start)
        else:
            print("File don't exist.")
            select_action(spi, list_of_detected_modules, detected_width_m, detected_height_m)
    else:
        print("Invalid input. Enter again.")
        select_action(spi, list_of_detected_modules, detected_width_m, detected_height_m)


def select_action(spi, list_of_detected_modules, detected_width_m, detected_height_m):
    while True:
        to_display = str(input("\nIf you want to display image enter 'img'\n"
                               "If you want to display video or GIF enter 'vid'\n"
                               "If you want to exit program enter 'exit'\n\n"
                               "What do you want to display?\n>>> "))
        if to_display == 'img':
            display_image(spi, list_of_detected_modules, detected_width_m, detected_height_m)
        elif to_display == 'vid' or to_display == 'gif':
            display_video(spi, list_of_detected_modules, detected_width_m, detected_height_m)
        elif to_display == 'exit':
            GPIO.cleanup()
            sys.exit()
        else:
            print("\nInvalid input. Try again.\n")


def main():
    os.system('clear')
    print('Welcome to Size-scalable Advertising Color LED Display v1.3.2!\n')
    list_of_detected_modules, detected_width_m, detected_height_m = detect_modules_and_validate()
    print("Detected resolution in modules:", detected_width_m, "x", detected_height_m)
    spi = spi_setup()
    select_action(spi, list_of_detected_modules, detected_width_m, detected_height_m)


main()
