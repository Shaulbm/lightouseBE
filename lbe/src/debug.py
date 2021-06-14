import main
import stocks
import time

main.startup()
stocks.register_stock("MSFT")

index = 5

while index > 0:
    result = ""
    try:
        result = stocks.read_default()
    except Exception as e:
        print (e)

    print (result)
    time.sleep(5)
    index -= 1
