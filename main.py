import fitz
from template_utils import generate_template_json,post_template_request
from page_utils import generate_page_json
from page import Page


def main(pdf_file):
    try:
        file = fitz.open(pdf_file)

        template_json = generate_template_json(file)
        print(template_json)
        

        for page_number in range(len(file)):
            page = file.load_page(page_number)
            current_page = Page(page)
            page_json = generate_page_json(current_page)

    except Exception as e:
        print(f"An error occured: {e}")

if __name__ == "__main__":
    pdf_file = 'sample.pdf'
    main(pdf_file)
