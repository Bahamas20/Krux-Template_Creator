import fitz

class Page:
    def __init__(self,page):
        self.page = page
    
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

def generate_template_json(theme, is_trending, font_program1, font_program2,
                           price, gender, title, description,
                           original_character_name, original_title,
                           original_description):
    
    data = {
        "ThemeId": theme,
        "IsTrending": is_trending,
        "FontProgram1": font_program1,
        "FontProgram2": font_program2,
        "Price": price,
        "Gender": gender,
        "Title": title,
        "Description": description,
        "OriginalCharacterName": original_character_name,
        "OriginalTitle": original_title,
        "OriginalDescription": original_description
    }
    
    return data


def main(pdf_file):
    try:
        file = fitz.open(pdf_file)

        for page_number in range(len(file)):
            page = file.load_page(page_number)
            current_page = Page(page)
            print(f"This is parameters for page number: {page_number}")
            print()
            if current_page.contains_text():
                bbox_list = current_page.get_text_bbox()
                print(f"Text BBoxes: {bbox_list}")
                print(f"Coordinates of centre: {[current_page.get_center(bbox) for bbox in bbox_list]}")
                print(f"Text width: {current_page.get_text_width(bbox_list)}")
                # You need to pass actual text, font file, and other parameters to this method
                # print(f"Text height: {current_page.get_text_height(text, fontfile, fontsize, specified_width)}")
                print(f"Font Size: {current_page.get_fontsize()}")
                print(f"Font Name: {current_page.get_fontname()}")
                print(f"Text Color: {current_page.get_text_color()}")
            if current_page.contains_images():
                print(f"List of image rects: {current_page.get_image_rects()}")
                print(f"Character Image Rect: {current_page.get_char_image_rect()}")
            print()
    except Exception as e:
        print(f"An error occured: {e}")

if __name__ == "__main__":
    pdf_file = 'sample.pdf'
    main(pdf_file)
