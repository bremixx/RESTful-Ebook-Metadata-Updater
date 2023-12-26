from api_call import GenericAPICalls, GoogleBooksAPICall
from img2pdf import convert
from os import remove
import cv2 as cv
import numpy as np
from shutil import copy
from glob import glob
import json

class Convert:
    '''Converts cover_page.jpg to PDF'''
    @staticmethod
    def remove_watermark(file, x1=152, x2=36, y1=15, y2=21):
        '''Removes the watermark from Google Books preview image'''
        img = cv.imread(file)
        blank = np.zeros(img.shape[:2], dtype='uint8')

        start_pt = (img.shape[1]-x1, img.shape[0]-x2)
        end_pt = (img.shape[1]-y1, img.shape[0]-y2)
        mask = cv.rectangle(blank, start_pt, end_pt, 255, -1)

        kernel_size = (5, 5)
        mask = cv.GaussianBlur(mask, kernel_size, cv.BORDER_DEFAULT)

        dst = cv.inpaint(img, mask, 3, cv.INPAINT_TELEA)
        cv.imwrite(file, dst)
    
    @staticmethod
    def import_image(image):
        '''Copies a given image for use by the other methods'''
        assert image.endswith('.jpg'), 'Image file needs to be .jpg'
        copy(image, 'cover_page.jpg')

    @staticmethod
    def convert_to_pdf():
        '''Converts jpg to a PDF'''
        with open('cover_page.pdf', 'wb') as f:
            f.write(convert('cover_page.jpg'))
        
        remove('cover_page.jpg')

class ChangeCoverPage:
    '''Backend operations for MainWindow'''
    def __init__(self):
        self.preview_thumbnails = []
    
    @staticmethod
    def fetch_google_preview_isbn(_json):
        '''Creates a list of previewLinks'''
        with open(_json, 'rb') as f:
            data = json.load(f)
        return [value['volumeInfo']['imageLinks']['thumbnail'] for value in 
                data['items'] if value['volumeInfo'].get('industryIdentifiers') 
                and value['volumeInfo']['readingModes']['image'] is True]

    def format_urls(self):
        '''Formats previewLinks into a list of URLs'''
        self.preview_thumbnails = [value.split('&', 1)[0] + '&printsec=frontcover&img=0&' \
                                   'zoom=0&edge=curl&source=gbs_api' for value
                                   in self.fetch_google_preview_isbn('results.json')]

    @staticmethod
    def fetch_itunes_preview_isbn(value):
        '''Creates a list of artworkUrl60/100'''
        url = f'https://itunes.apple.com/search?term={value}&entity=ebook'
        GoogleBooksAPICall.call_api(url, 'apple_results.json')
    
    def get_apple_artwork(self):
        '''Format iTunes URLs for hi-res artwork'''
        with open('apple_results.json', 'rb') as a:
            data = json.load(a)
            results = [result for result in data['results']]

        high_res = '/100000x100000bb.jpg'
        for result in results:
            split_result = result['artworkUrl100'].split('/')
            self.preview_thumbnails.append('/'.join(split_result[:-1]) + high_res)

    def write_previews_to_file(self):
        '''Writes preview images to file'''
        for index, url in enumerate(self.preview_thumbnails, start=1):
            GenericAPICalls.download_image(url, f'cover_page{index}.jpg')
            Convert.remove_watermark(f'cover_page{index}.jpg', 25, 0, 0, 27)

    @staticmethod
    def convert_to_pdf():
        '''Convert convert.jpg to PDF and delete'''
        with open('cover_page.pdf', 'wb') as f:
            f.write(convert('convert.jpg'))

        remove('convert.jpg')

    @staticmethod
    def delete_artwork():
        '''Delete saved cover_page*.jpg'''
        files = glob('cover_page*.jpg')
        for file in files:
            remove(file)
