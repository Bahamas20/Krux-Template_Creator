import os
import tempfile
import fitz
from PIL import Image

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
                        font = self.get_font(span.get("font", None))
                        stroke_width = None
                        text_align = 'center'
                        line_height = font_size * 1.2 
                        color_value = self.get_color(span.get("color", None))
                        width = (bbox[2] - bbox[0]) + 5
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
                            "text_color": color_value,
                            "width": int(width),
                            "top": int(top),
                            "left": int(left)
                        }
                        text_boxes_info.append(text_box_info)


        text_boxes_info.sort(key=lambda x: (x["top"], x["left"]))

        return text_boxes_info

    def get_font(font):
        if font == 'SueEllenFrancisco':
            return 'Sue Ellen Francisco.ttf'
        elif font == 'LettersforLearners':
            return 'Letters for Learners.ttf'
        else:
            return None
    
    def get_color(color_value):
        if color_value is not None:
            return f"#{color_value:06x}"
        else:
            return None
           
    def get_background_img(self):
        image_list = self.page.get_images()

        # max_width = -1
        # max_height = -1
        background_image = None

        for img in image_list:
            xref = img[0]  
            width = img[2]
            height = img[3]

            if width == 1536 and height == 1536:
                # max_width = width
                # max_height = height
                background_image = (xref, width, height)
        
        return background_image

    def save_background_image(self,file):

        background_img = self.get_background_img()
        resized_width = self.get_page_width()
        resized_height = self.get_page_height()

        if background_img:
            xref = background_img[0]

            try:
                pix = fitz.Pixmap(file, xref)
                if pix.n - pix.alpha > 3: 
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_file_path = tmp_file.name


                    pix_pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


                    pix_resized = pix_pil.resize((resized_width, resized_height))

                    # Save the resized image to the temporary file
                    pix_resized.save(tmp_file_path, format='PNG')
                    files = {
                        'Image': ('norm_image_{}.png'.format(xref), open(tmp_file_path, 'rb'), 'image/png'),
                        'LowResImage': ('low_res_{}.jpeg'.format(xref), open(tmp_file_path, 'rb'), 'image/jpeg')
                    }

                    os.remove(tmp_file_path)  # Clean up temporary file

                    return files

            except Exception as e:
                print(f"Error saving image: {e}")
            finally:
                if pix:
                    pix = None 
        else:
            try:
                # Create a blank white image 
                empty_image = Image.new('RGB', (resized_width,resized_height), (255, 255, 255))
                
                # Save the empty image to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_file_path = tmp_file.name
                    empty_image.save(tmp_file_path, format='PNG')


                files = {
                    'Image': ('empty_image.png', open(tmp_file_path, 'rb'), 'image/png'),
                    'LowResImage': ('empty_image.png', open(tmp_file_path, 'rb'), 'image/png')
                }

                os.remove(tmp_file_path)  # Clean up temporary file

                return files
            
            except Exception as e:
                print(f"Error creating empty image: {e}")

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


        bbox_list.sort(key=lambda x: (x[1], x[0]))
    
        return bbox_list
    
    def contains_images(self):
        """
        Checks whether current page contains images. 

        :return True if page contain image bboxes, False otherwise
        """
        return True if self.page.get_images() else False
    
    def contains_text(self):
        """
        Checks whether current page contains text.

        :return: True if page contains text bboxes, False otherwise 
        """
        return True if self.page.get_text("text") else False
    