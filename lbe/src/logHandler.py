import logging
import os
 
class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        return repr(result)
 
    def format(self, record):
        result = super().format(record)
        if record.exc_text:
            result = result.replace("\n", "")
        return result

def initLog():
    handler = logging.StreamHandler()
    # formatter = OneLineExceptionFormatter(logging.BASIC_FORMAT)
        # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
    handler.setFormatter(formatter)
    
    logging.basicConfig(filename='..\..\logs\claroLog.log', filemode='a', level=os.environ.get("LOGLEVEL", "INFO"))
    root = logging.getLogger()
    root.addHandler(handler)