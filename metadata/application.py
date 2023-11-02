from pypdf import PdfReader, PdfWriter
from api_call import GoogleBooksAPICall, GenericAPICalls
from format_metadata import FormatMetadata, DirectInput
from write_to_file import Write
from utility import Utilities
from convert import Convert
import argparse

def main():
    
    parser = argparse.ArgumentParser()

    parser.add_argument('file', nargs='?', help='PDF file to modify')
    parser.add_argument('-o', '--output', help='Where to save the modified PDF')
    parser.add_argument('-a', '--author', help='Option to search by author')
    parser.add_argument('-i', '--isbn', type=str, help='Option to search by ISBN')
    parser.add_argument('-c', '--change', action='store_true', help='Changes file cover page')
    parser.add_argument('-d', '--drop', action='store_true', help='Drops PDF cover page')
    parser.add_argument('-b', '--bookmark', action='store_true', help='Flag to reconstruct PDF outline')
    parser.add_argument('-l', '--local', help='Use a local image file for PDF cover page')
    parser.add_argument('-m', '--manual', action='store_true', help='Manualy enter PDF metadata')

    args = parser.parse_args()
    
    if args.drop: assert args.change is True, '-c required when dropping cover page'
    if args.local: assert args.change is not None, '--change flag is required'

    if args.file.endswith('.txt'):
        assert args.isbn is None, 'ISBN search not supported for .txt'
        assert args.author is None, 'Search by author isn\'t supported for .txt'
        utility = Utilities()
        file = utility.unpack_text_file(args.file)
    else: file = [args.file]

    isbn = args.isbn if args.isbn else ''

    for file in file:
        
        if args.manual:
            metadata = DirectInput.user_metadata_prompt()
        else:
            api_call = GoogleBooksAPICall(file)
            url = api_call.build_api_request(args.author, isbn)

            api_call.call_api(url, output='results.json')

            _format = FormatMetadata()
            _format.format_metadata()
            metadata = _format.metadata()

        if args.change:

            isbn = isbn if args.isbn else metadata[2]

            convert = Convert()
            gap = GenericAPICalls(isbn)
            if 10 < len(isbn) < 13:
                source = gap.call_google_preview()
                gap.download_image(source)
                convert.remove_watermark()
            elif args.local is not None:
                print(f'Importing cover page from {args.local}')
                convert.import_image(args.local)
            else:
                try:
                    source = gap.call_itunes_api()
                    gap.download_image(source)
                except:
                    source = gap.call_google_preview()
                gap.download_image(source)
                convert.remove_watermark()
            convert.convert_to_pdf()

        reader = PdfReader(file)
        writer = PdfWriter()

        write = Write(metadata[0], metadata[1], reader, writer, file, args.drop)
        write.write_to_file(args.output, args.change, args.bookmark)