import fitz
from template_utils import generate_template_json,post_template_request
from page_utils import generate_page_json
from page import Page


def main(pdf_file):
    try:
        file = fitz.open(pdf_file)

        template_json = generate_template_json(file)
        print(template_json)
        # story_id = post_template_request(template_json)
        story_id = ''
        main_name = template_json['OriginalCharacterName']
     
        for page_number in range(1):
            page = file.load_page(page_number)
            if page_number == len(file) - 1:
                current_page = Page(page,-1)
            else:
                current_page = Page(page,page_number)
            page_json = generate_page_json(current_page,main_name)
            print()
            print(f"This is page number: {page_number}")
            print(page_json)

    except Exception as e:
        print(f"An error occured: {e}")

if __name__ == "__main__":
    pdf_file = 'sample.pdf'
    main(pdf_file)
