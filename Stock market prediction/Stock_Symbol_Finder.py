from yahooquery  import search

while True:
    def search_stock_symbol_by_name(company_name):
        try:
            result = search(company_name)
            if result and 'quotes' in result:
                quotes = result['quotes']
                if quotes:
                    # Return the first stock symbol found for the given company name
                    return quotes[0]['symbol']
        except Exception as e:
            print(f"Error: {str(e)}")
        return None

    # Example usage:
    company_name = input("Enter Company Name:")
    stock_symbol = search_stock_symbol_by_name(company_name)

    if stock_symbol:
        print(f"Stock symbol for {company_name}: {stock_symbol}")
    else:
        print(f"Could not find stock symbol for {company_name}")

