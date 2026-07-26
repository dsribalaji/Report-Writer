from api2pdf import Api2Pdf
import os

def convert_docx_to_pdf(docx_path, output_pdf_path):
    """
    Uses Api2Pdf to convert a .docx file to .pdf.
    """
    api_key = os.getenv("API2PDF_API_KEY")
    if not api_key:
        print("API2PDF_API_KEY not found.")
        return None

    try:
        a2p_client = Api2Pdf(api_key)

        # We need to upload the file or use a public URL.
        # Api2Pdf libreoffice endpoint supports local files via multipart/form-data upload using libreoffice_convert

        api_response = a2p_client.LibreOffice.convert(docx_path)

        if api_response.result and 'FileUrl' in api_response.result:
            pdf_url = api_response.result['FileUrl']

            # Download the PDF from the provided URL
            import requests
            response = requests.get(pdf_url)
            if response.status_code == 200:
                with open(output_pdf_path, 'wb') as f:
                    f.write(response.content)
                return output_pdf_path
            else:
                print(f"Failed to download PDF from Api2Pdf: {response.status_code}")
                return None
        else:
            print(f"Api2Pdf error: {api_response.error}")
            return None

    except Exception as e:
        print(f"Exception during PDF conversion: {e}")
        return None
