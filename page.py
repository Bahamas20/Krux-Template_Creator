import fitz

class Page:
    def __init__(self,page,page_number):
        self.page = page
        self.page_number = page_number
    
    def get_page_type(self):
        if self.page_number == 0:
            return 0
        elif self.page_number == -1:
            return 1
        else:
            return 2
    def get_page_width(self):
        return int(self.page.rect.width)

    def get_page_height(self):
        return int(self.page.rect.height)
    
    
    def get_text_boxes_info(self):
        """
        Gets detailed information about text bounding boxes on the page.

        :return: List of dictionaries, each containing information about a text box
        """
        text_boxes_info = []
        blocks = self.page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        bbox = span["bbox"]
                        text = span["text"]
                        font_size = span.get("size", None)
                        font = span.get("font", None)
                        stroke_width = None
                        text_align = 'center'
                        line_height = font_size * 1.2
                        text_color = '#' + str(span.get("color", None))
                        width = bbox[2] - bbox[0] 
                        top = bbox[1] 
                        left = bbox[0]

                        text_box_info = {
                            "bbox": bbox,
                            "text": text,
                            "font_size": int(font_size),
                            "font": font,
                            "stroke_width": stroke_width,
                            "text_align": text_align,
                            "line_height": int(line_height),
                            "text_color": text_color,
                            "width": int(width),
                            "top": int(top),
                            "left": int(left)
                        }
                        text_boxes_info.append(text_box_info)

        # Sort from top to bottom, then left to right
        text_boxes_info.sort(key=lambda x: (x["top"], x["left"]))

        return text_boxes_info

  
    def get_center(self,bbox):
        """
        Gets the center coordinates of a bbox

        :param bbox: Bbox of text 
        :return: Tuple (x, y) representing the center coordinates of bbox
        """
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2

        return center_x, center_y
       
    def get_text_width(self, bbox_list):
        """
        Gets the maximum bbox width

        :param bbox_list: List of bboxes
        :return: Maximum width  
        """
        min_x, max_x = float("inf"), float("-inf")

        for bbox in bbox_list:
            min_x = min(min_x, bbox[0])
            max_x = max(max_x, bbox[2])

        return max_x - min_x
    
    def get_text_height(self, text, fontfile, fontsize, specified_width):
        """
        Calculates the new height required for the new text box

        :param text: Text to insert
        :param font_name: Font of text
        :param font_size: Font size of text
        :param specified_width: Predetermined specified width
        :return: Height of new text box
        """
        dummy_doc = fitz.open()
        dummy_page = dummy_doc.new_page()
        dummy_page_obj = Page(dummy_page)
        INITIAL_HEIGHT = 10000
        used_px = dummy_page_obj.insert_text(fitz.Rect(0, 0, specified_width,
                                                       INITIAL_HEIGHT), text,
                                             fontsize, fontfile, (0, 0, 0), 1)
        rect_height = INITIAL_HEIGHT - used_px 
        dummy_doc.close()

        return rect_height

    def get_text_bbox(self):
        """
        Gets the list of text bboxes in page

        :return: List of bboxes 
        """
        bbox_list = []
        blocks = self.page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        bbox_list.append(span["bbox"])

        # Sort from top to bottom, then left to right
        bbox_list.sort(key=lambda x: (x[1], x[0]))
    
        return bbox_list
    
    def get_image_rects(self):
        """
        Gets the list of image rects in page

        :return: List of rects 
        """
        images = self.page.get_images()
        bbox_list = []

        for image in images:
            rect = self.page.get_image_rects(image)[0]
            bbox_list.append(rect)

        # Sort from top to bottom, then left to right
        bbox_list.sort(key=lambda x: (x[1], x[0])) 

        return bbox_list
      
    def get_fontname(self):
        """
        Get the font names of the current text in the page for each text box.

        :return: Dictionary mapping text box number to font name, or None if no text is found
        """
        text_instances = self.page.get_text("dict")["blocks"]
        font_names = {}

        # Iterate over text blocks
        for block in text_instances:
            if block['type'] == 0:  # Ensure this block contains text
                for line in block["lines"]:
                    for span in line["spans"]:
                        bbox_list = self.get_text_bbox()
                        for index, bbox in enumerate(bbox_list):
                            if bbox == span.get("bbox", None):
                                text_box_number = index + 1
                        font_name = span.get("font", None)
                        if text_box_number is not None and font_name:
                            font_names[text_box_number] = font_name
                        # Assuming there are only 4 text boxes maximum
                        if len(font_names) >= 4:
                            # Sort font_names by text_box_number in ascending order
                            font_names = dict(sorted(font_names.items(), key=lambda item: item[0]))
                            return font_names

        if font_names:
            # Sort font_names by text_box_number in ascending order
            font_names = dict(sorted(font_names.items(), key=lambda item: item[0]))
            return font_names
        else:
            return None


    
    def get_fontsize(self):
        """
        Get fontsize of current text in page. (Assuming all text on page have same size)

        :return: Fontsize if page contains text, else returns None 
        """
        fontsize = None
        blocks = self.page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        fontsize = span["size"]
                        break
                    if fontsize:
                        break
                if fontsize:
                    break
        
        return fontsize

    def get_text_color(self):
        """
        Get color of current text in page.

        :return: Text color in RGB format if page contains text, else returns None 
        """
        color = None
        blocks = self.page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        color = span["color"]
                        break
                    if color:
                        break
                if color:
                    break
        
        return None if not color else tuple(val / 255 for val in fitz.sRGB_to_rgb(color))
        
    def contains_text(self):
        """
        Checks whether current page contains text.

        :return: True if page contains text bboxes, False otherwise 
        """
        return True if self.page.get_text("text") else False
    
    def contains_images(self):
        """
        Checks whether current page contains images. 

        :return True if page contain image bboxes, False otherwise
        """
        return True if self.page.get_images() else False
    
    def get_char_image_rect(self):
        """
        Gets the Rect for character image

        :return: Rect of character image 
        """
        images = self.page.get_images()
        res = None

        for image in images:
            rect = self.page.get_image_rects(image)[0]
            if rect[0] > self.page.rect.x0:
                res = rect
        
        return res
