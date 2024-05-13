price_calc_json=[{
  "type": "function",
  "function":{'name': 'Best_Price_Calculator',
 'description': 'It takes information like cost of product,loan values like interest rate, max tenure, savings for the product,minimum downpayement percentage and emi paying capacity\nand calculate to lower the final cost of the product.',
 'parameters': {'type': 'object',
  'properties': {'cost': {'description': 'It is the cost of the product that the user wants to buy.',
    'type': 'integer'},
   'Loan_interest_rate': {'description': 'It is the interest rate per annum at which the bank is providing the loan.',
    'type': 'integer'},
   'max_tenure': {'description': 'It is the maximum tenure for which the bank is ready to give the loan.',
    'type': 'integer'},
   'Investment_interest_rate': {'description': "It is the risk taking ability of the user whether he is a 'high risk taker' or 'moderate risk taker' or 'low risk taker'",
    'type': 'string'},
   'savings': {'description': 'It is the amount that the user has saved for buying the product.',
    'type': 'integer'},
   'min_downpayment': {'description': 'It is the minimum downpayment percentage that the user needs to make for buying the product.It should be below 100%',
    'type': 'integer'},
   'emi_limit': {'description': 'It is the emi paying capacity of the user',
    'type': 'integer'}
                }
            }
        }
    }
]