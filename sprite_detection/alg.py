import cv2
from numpy import uint8
from numpy import frombuffer
from numpy import float32
from numpy import array

from random import randrange
from base64 import b64decode
from base64 import b64encode
import re

from typing import Tuple
from numpy.typing import NDArray


class SpriteSlicer:
    def __init__(
        self,
        image_base64: str = "",
        scale_percent: int = 100,
        distance: int = 3,
        toleranci: int = 0,
        toleranci_char: str = "+",
    ) -> None:
        self.image_base64 = image_base64
        self.scale_percent = scale_percent
        self.distance = distance
        self.toleranci = toleranci
        self.toleranci_char = toleranci_char

    def init(self) -> Tuple[list, str]:
        image = self.base64_to_cv2()
        image = self.resize_image(image)
        image_copy = image.copy()
        size = (image.shape[1], image.shape[0])

        reDraw_color = (36, 254, 12)
        background_color = self.get_background_color(image)

        toleranci_start, toleranci_end = self.set_toleranci(background_color)

        reDraw_color = self.set_reDraw_color(
            reDraw_color, toleranci_start, toleranci_end
        )

        image = self.draw_object(image, reDraw_color, toleranci_start, toleranci_end)

        sprites_coords, mask = self.detect_sprite(image, reDraw_color, size)
        image_transparent_background = self.remove_background(image_copy, mask, size)

        return sprites_coords, image_transparent_background

    def base64_to_cv2(self) -> NDArray[uint8]:
        """
        decode base64 string to numpy.ndarray
        """
        decoded_data = b64decode(self.image_base64)
        decoded_data_arr = frombuffer(decoded_data, dtype=uint8)
        cv2_object = cv2.imdecode(decoded_data_arr, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(cv2_object, cv2.COLOR_RGB2BGR)

        return image

    def resize_image(self, image: NDArray[uint8]) -> NDArray[uint8]:
        """
        resize image with aspect ratio if scale_percent default value(100) notting change
        """
        width = int(image.shape[1] * self.scale_percent / 100)
        height = int(image.shape[0] * self.scale_percent / 100)
        dim = (width, height)

        image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        return image

    def set_toleranci(self, background_color: tuple) -> Tuple:
        """
        tolerant colors means another backgrounds color
        """
        toleranci_movement = {}
        start = end = (0, 0, 0)

        if self.toleranci_char == "+":
            toleranci_movement["+"] = tuple(
                [i + self.toleranci for i in background_color]
            )
            start, end = background_color, toleranci_movement["+"]

        elif self.toleranci_char == "-":
            toleranci_movement["-"] = tuple(
                [i - self.toleranci for i in background_color]
            )
            start, end = toleranci_movement["-"], background_color

        elif self.toleranci_char == "+-":
            toleranci_movement["+"] = tuple(
                [i + self.toleranci for i in background_color]
            )
            toleranci_movement["-"] = tuple(
                [i - self.toleranci for i in background_color]
            )
            start, end = toleranci_movement["-"], toleranci_movement["+"]

        return start, end

    def get_background_color(self, image: NDArray[uint8]) -> Tuple[int]:
        """
        find the most uses color in image (background color)
        """
        (channel_b, channel_g, channel_r) = cv2.split(image)
        channel_b = channel_b.flatten()
        channel_g = channel_g.flatten()
        channel_r = channel_r.flatten()

        color_count = {}
        for i in range(len(channel_b)):
            RGB = (
                "("
                + str(channel_r[i])
                + ","
                + str(channel_g[i])
                + ","
                + str(channel_b[i])
                + ")"
            )
            if RGB in color_count:
                color_count[RGB] += 1
            else:
                color_count[RGB] = 0

        last = sorted(color_count, key=lambda x: color_count[x])[-1]
        return tuple([int(i) for i in re.findall(r"\d+", last)][::-1])

    def set_reDraw_color(self, color: tuple, start: tuple, end: tuple) -> None:
        """
        check if drawing color is in toleranci colors change to random
        """

        while self.check_background_color(color, start, end):
            color(randrange(255), randrange(255), randrange(255))

        return color

    def check_background_color(self, object: tuple, start: tuple, end: tuple) -> bool:
        """
        check if color is in range start-end
        """

        if (
            object[0] >= start[0]
            and object[1] >= start[1]
            and object[2] >= start[2]
            and object[0] <= end[0]
            and object[1] <= end[1]
            and object[2] <= end[2]
        ):
            return True
        return False

    def draw_object(
        self, image: NDArray[uint8], color: tuple, start: tuple, end: tuple
    ) -> NDArray[uint8]:
        """
        draw pixels with reDraw_color who is not toleranci(not background)
        """
        rows, cols = image.shape[:2]

        for i in range(rows):
            for j in range(cols):
                pixel = image[i, j].tolist()
                if not (self.check_background_color(pixel, start, end)):
                    cv2.rectangle(image, (j, i), (j, i), color, 1)
                else:
                    cv2.rectangle(
                        image, (j, i), (j, i), (255, 255, 255), 1
                    )  # black color

        return image

    def detect_sprite(
        self, image: NDArray[uint8], color, image_size: tuple
    ) -> Tuple[list, NDArray[uint8]]:
        """
        border detected objects and the border coords save to lst
        """
        lw = rw = array(list(color))

        mask = cv2.inRange(image, lw, rw)
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (self.distance, self.distance)
        )
        close = cv2.morphologyEx(mask.copy(), cv2.MORPH_CLOSE, kernel)
        close = cv2.resize(close, image_size, interpolation=cv2.INTER_AREA)
        dilate = cv2.dilate(close, kernel)
        detect = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cnts = detect[0] if len(detect) == 2 else detect[1]

        lst = []
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            lst.append([x, y, w, h])

        return lst, mask.copy()

    def remove_background(
        self, image: NDArray[uint8], mask: NDArray[uint8], image_size: tuple
    ) -> str:
        """
        if image is jpej, jpg remove background
        """
        mask = cv2.resize(mask, image_size, interpolation=cv2.INTER_AREA)
        mask = cv2.GaussianBlur(
            mask, (0, 0), sigmaX=2, sigmaY=2, borderType=cv2.BORDER_DEFAULT
        )
        mask = (2 * (mask.astype(float32)) - 255.0).clip(0, 255).astype(uint8)

        transparent_background_image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        transparent_background_image[:, :, 3] = mask

        return b64encode(cv2.imencode(".png", transparent_background_image)[1])
