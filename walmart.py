import requests as r 
import json 
from PIL import Image
import pytesseract
import re 
from glob import glob
from custom_logger import CustomFormatter
import logging 

# reference: https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
# create logger from custom logger class 
logger = logging.getLogger("walmart")
logger.setLevel(logging.INFO)

#create console handlerto send output to terminal 
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

logger.info('starting walmart receipt parser')

# @dataclass
# class Receipt: 
#         store_number : str
#         card_last_4: str 
#         card_type :str 
#         purchase_date: str 
#         receipt_total: str 
        # broken 
        # card_types : list = list([
        #         "Visa",
        #         "Mastercard",
        #         "Amex",
        #         "Discover",                 
        #         "Debit", 
        #         "Other"])

#todo need to rework the loop validation. Havent set everything up to run through a list yet. 

receipts = glob('receipts/*', recursive=False)
logger.debug(f"found {len(receipts)} receipts")
# url  https://walmart.com/receipt-lookup
# sent after submitting receipt lookup https://walmart.com/chcwebapp/api/receipts
# If you don't have tesseract executable in your PATH, include the following:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# all scans 
# scan_data = [pytesseract.image_to_string(Image.open(file)) for file in receipts ]
# test data 

# required for sending off the recepit api call 
card_types = ["Visa", "Mastercard",
              "Amex", "Discover", 
              "Debit", "Other"]

def parse_receipt_data(receipt_img_file: str) -> dict: 
        logger.info(f'parsing receipt {receipt_img_file}')
        
        scan_data = pytesseract.image_to_string(Image.open(receipt_img_file))
        if scan_data: 
                logger.debug(f'parsed receipt data: {scan_data}')
        else : 
                logger.warning('no receipt data parsed by parser')
                return 
        
        # done 
        store_match = re.search(r'ST\# \d+', scan_data) 
        if not store_match:
                logger.warning('no store number found by parser')
                return  
        logger.info(f'store number: {store_match.group()}')
        
        store_number = int((store_match.group()).split(' ')[1])

        # done 
        card_type_match = re.search(
                r'|'.join([i for i in card_types]), 
                scan_data, 
                flags=re.IGNORECASE
                ) 
        if card_type_match: 
                logger.info(f'card type: {card_type_match.group()}')
                card_type = card_type_match.group().strip().title() 
                logger.info(f'card type: {card_type}')
        else: 
                logger.warning('no card type parsed by parser')
                return  

        # Done 
        purchase_date_match = re.search(
                r'\d{2}\/\d{2}\/\d{2}', scan_data
                )
        if not purchase_date_match:
                logger.warning('no receipt purchase date found by parser') 
                return  
                        
        # convert "1/2/3 to 1-2-3 (expected date)"
        logger.info(f'purchase date: {purchase_date_match.group()}')
        purchase_date = purchase_date_match.group().replace('/','-')
        logger.info(f'mutating purchase date: {purchase_date}') 
        purchase_date = [i for i in purchase_date]
        if len(purchase_date) == 8:
                logger.info(f'purchase date length: {len(purchase_date)}') 
                # convert 23 into year 2023 
                purchase_date[:-2] += '20'
                purchase_date = ''.join(purchase_date)
                logger.info(f" walmart formatted purchase date: {purchase_date}")
        else: 
                logger.warning('invalid purchase length on purchase date')
                return 
                        
        #TODO validate against debit string "US DEBIT-"" 
        card_last_4_match = re.search(f'{card_type}.*', scan_data, flags=re.IGNORECASE)
        if not card_last_4_match: 
                logger.warning('last 4 of card digits not extracted from receipt.')
                return 
        card_last_4_whole_match_string = card_last_4_match.group()
        # check if we're on the right line 
        if "APPR" in card_last_4_whole_match_string: 
                logger.info('card last 4 digits found on correct line')
                card_last_4 = re.search(
                        rf'{card_type}.*?(\d\d\d\d)',
                        card_last_4_whole_match_string,
                        flags=re.IGNORECASE
                        ).groups()[0] # get the last 4 
                logger.info(f'card last 4 digits: {card_last_4}')
        else: 
                logger.warning('card last 4 digits not found on correct line')
                return 
                
        receipt_total_match = re.search(r'TOTAL (\d+\.\d+)', scan_data)
        if not receipt_total_match:
                logger.warning('no receipt total found by parser')
                return  
        receipt_total = receipt_total_match.group(1)
        logger.info(f'receipt total: {receipt_total}')
        
        logger.info('receipt parsed successfully')
        
        
        try : 
                        
                receipt_info = {
                        "store_number":store_number,
                        "card_type":card_type,
                        "card_last_4":card_last_4,
                        "purchase_date":purchase_date,
                        "receipt_total":receipt_total
                        } 
        except UnboundLocalError as e: 
                logger.warning(f'error parsing receipt: {e}')
                return False
        return receipt_info       



        

def itemize_walmart_receipt(
        store_number: str,
        card_type: str,
        card_last_4: str,
        purchase_date: str,
        receipt_total: str
        ): 
         
        data = {
                "storeId":f"{store_number}",
                "purchaseDate":f"{purchase_date}",
                "cardType":f"{card_type.title()}",
                "total":f"{receipt_total}",
                "lastFourDigits":f"{card_last_4}"
        }
        
                
        
        print(data) 
        url = 'https://www.walmart.com/chcwebapp/api/receipts'
        headers = {
                'sec-ch-ua':'"Chromium";v="98", " Not A;Brand";v="99", "Google Chrome";v="98"',
                'Accept':'application/json' ,
                'Referer':'https://www.walmart.com/receipt-lookup',
                'Content-Type':'application/json',
                'sec-ch-ua-mobile':'?0' ,
                'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
                'sec-ch-ua-platform':'"Mac OS X"' 
                }

        res = r.post(url, json=data, headers=headers)
        json_data = res.json
        
        print(res.text)
        
        # for item in json_data['receipts'][0]['items']: 
        #         item_description = item['description']
        #         item_id = item['itemId']
        #         item_upc = item['upc']
        #         item_price = item['price']
        #         item_quantity = item['quantity']

        #         print(
        #                 f"item_description: {item_description}\n",
        #                 f"item_id: {item_id}\n",
        #                 f"item_upc: {item_upc}\n",
        #                 f"item_price: {item_price}\n",
        #                 f"item_quantity: {item_quantity}\n\n"
        #                         )
                
        # with open('output.json', 'w') as f: 
        #         json.dump(res_json, f)
        


if __name__ == "__main__":
        rec1_data = parse_receipt_data(receipt_img_file=receipts[0])
        # if the parser extracted data from the receipt correctly 
        if rec1_data:
                print(rec1_data)
                # itemize_walmart_receipt(**rec1_data)
        else: 
                logger.critical("there was an error parsing the receipt data")


# TODO left off here 


# with open("output.json", 'r') as f: 
#         json_data = f.read()
#         json_data = json.loads(json_data)

print(
        # json_data['receipts'][0].keys()
        # json_data['receipts'][0]['store'], 
        # json_data['receipts'][0]['dateTime'], # of receipt 
        # json_data['receipts'][0]['noOfItems'], # int representing total items 
        # json_data['receipts'][0]['total'], #{'subtotal': 138.14, 'taxTotal': 3.14, 'totalAmount': 141.28, 'changeDue': 0}
        # json_data['receipts'][0]['tcNumber'], # ? 493112705621507227449
        # json_data['receipts'][0]['barCodeImageUrl'], # https://receipts-query.edge.walmart.com/barcode?barWidth=2&barHeight=50&data=GQ9%24V0W5C9+PKL+M
        # json_data['receipts'][0]['items'][1],
        # json_data['receipts'][0]['tender']
        )


# DEV ZONE ###########################
# walmart info 
# Under the store information it will have 
# St# that’s the store number 
# OP# is the checker and 
# TE# is the terminal or chevkstand followed by the TR# threats the transaction. On the bottom of the receipt is a barcode and a TC# that’s what they will use if you need to return an item.







