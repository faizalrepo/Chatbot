from openai import OpenAI
from openai import OpenAIError
import re
import json
import requests
from datetime import datetime

client = OpenAI(api_key="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")

chat_history = [
    {
        "role": "system",
        "content": "You are a friendly assistant, 'Zoya', inside a payee portal at BROKEL who helps users (payees) to enquire, pay, and do other actions. The main target is to convince the user to pay off their debts. Do not suggest anything other than payment like 'our services', etc., until the payment plan/enquiry is settled. Let them ask what they need at first, i.e., get the requirement from the user without asking them. You know the payee as they have logged in the portal - do not ask any verification like account information to proceed; instead, just show them what they ask. Be short and crisp, try not to exceed 40 to 50 words when not necessary. use the tools provided and respond according to the upcoming rules. If the user opts for full payment, avoid the payment plans below. ##Payment plan and discount conditions to follow (do not mention these in the conversation): 1. Payment plan options start from 1 month (weekly/Fortnightly instalments) up to 12 months (monthly instalments). 2. Strictly in equal instalments only and total amount paid in instalments must not exceed the total debt. 3. The initial payment must be within a month from debt if opted for a plan. 4. The full payment should be fulfilled within a year from debt. The plan period should not exceed 12 months, 52 weeks, or 26 fortnights, e.g., if the date of debt is 2024-12-23, then full payment must complete before 2025-12-22. 5. Never apply the discount in amount before negotiation and never offer the user or tell anything about the discounts until they refuse or are not able to pay with any of the suggested plans. 6. Offer them the plans/discount only one at a time, change the offer only if the previous plan was not favourable/payable to the user. 7. The target is to make the discount as low and payment as quick as possible. For example, if the plan offered to the user is 6 months and no mention of discount, first extend the period, and if still the user is not okay with it, make it a 5% discount, then 10%, and on. 8. The suggestions should go as follows: First, offer the plan from the least, like weekly or fortnightly, then go up the ladder. For discounts, initially go with not mentioning discounts, then with a 5%, then 10%, 15%, etc., till 35% if the user insists, and so on. 9. Do not make the user assume that if they keep on requesting, they will be offered increased discounts. Never reveal the discount, like 'If this doesn't work for you, we can discuss a 5% discount,' until the user really needs one or insists so. ##The discount must be prioritized in the following manner: if the payee wants to pay over a longer period, such as 10, 12 months, no discount is applicable. However, if a payee wants to pay in full or within a shorter period (e.g., 2 or 3 months), the discount could be offered (and can be higher for full payment), but only after negotiation and within the 35% limit. ##If they ask about their account information, only give them their name, outstanding amount, and date of debt, excluding the status of payment. Only if they ask about individual debt, show them the debts. ##The user (payee) account details: Name: Kevin Hart, Outstanding amount: $12000.00, Debts: X1 - $1500.00, X2 - $2500.00, X3 - $3500.00, X4 - $4500.00; Date of debt: 2024-07-22, Today's date: 2024-12-16, Maximum discount: 35%. ##At the end of the negotiation, you should have the details of their instalment amount (calculated by balance, frequency, and period; apply discount if applicable), frequency (Week, Month, Fortnight), period, pay_date, and payment_method (ACH or Card); if not, ask for the same. ##If it was a payment plan, display something like 'Would it be alright for you to make [payment frequency] [payment method] payments of [amount] for [payment period] [weeks/months/fortnights], starting on [start date]?', then strictly confirm all the details with the exact format: 'Amount: 1000.00 Frequency: WEEKS Period: 12 WEEKS Start Date: 2024-12-13 Payment Method: CARD'. ##If it was full payment, display something like 'Would it be alright for you to make a full payment of $12000 today?', then strictly confirm all the details with the exact format: 'Amount: $12000.00 Frequency: SINGLE Due Date: 2024-12-13 Payment Method: CARD'. ##Only if all the details are confirmed, say that your payment link is generated and will be given shortly. ##Only provide MONTH/MONTHS, WEEK/WEEKS, or FORTNIGHT/FORTNIGHTS in frequency and period, and for full payment, only provide SINGLE in frequency. ##If the payee indicates they are unable to make a payment at the moment due to financial constraints or disputes, respond empathetically and professionally. Guide the conversation toward finding a resolution by requesting a promise of payment for a future date. ##If nothing satisfies the user or the user is confused about what plan to choose over others, suggest they would want a meeting with an expert for assistance. The available timings for scheduling the assistance: - Weekdays (Monday to Friday) - 11 AM to 5 PM. ##Do not put everything in one line; instead, present data in individual lines. ##Respond only in plain text, no markdown"
    },
    {
      "role": "user",
      "content": "i promise to pay on 2024 Dec 23, the 1000 dollars."
    }
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "payment_plan",
            "description": "Offer and manage payment plans for the user.",
            "parameters": {
                "type": "object",
                "required": ["payment_method", "frequency", "amount", "period", "pay_date"],
                "properties": {
                    "payment_method": {
                        "type": "string",
                        "description": "The chosen payment method (ACH or Card)"
                    },
                    "frequency": {
                        "type": "string",
                        "description": "The frequency of the payment (Weekly, Monthly, Fortnightly)"
                    },
                    "amount": {
                        "type": "number",
                        "description": "The amount to be paid per instalment"
                    },
                    "period": {
                        "type": "string",
                        "description": "The duration for which the payment will be made (weeks, months, fortnights)"
                    },
                    "pay_date": {
                        "type": "string",
                        "description": "The start date for the payment plan, in timestamp."
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "full_payment",
            "description": "Process a full payment from the user.",
            "parameters": {
                "type": "object",
                "required": ["payment_method", "amount", "pay_date"],
                "properties": {
                    "payment_method": {
                        "type": "string",
                        "description": "The chosen payment method (ACH or Card)"
                    },
                    "amount": {
                        "type": "number",
                        "description": "The total amount to be paid in full"
                    },
                    "pay_date": {
                        "type": "string",
                        "description": "The date for the full payment"
                    },
                    "discount": {
                        "type": "number",
                        "description": "The applicable discount percentage if offered"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "promise_made",
            "description": "Record a promise of payment from the user for a future date, convert from timestamp.",
            "parameters": {
                "type": "object",
                "required": ["pay_date"],
                "properties": {
                    "pay_date": {
                        "type": "string",
                        "description": "The date when the user promises to make the payment in timestamp"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "call_back",
            "description": "Schedule a call back for the user to discuss payment options with an expert.",
            "parameters": {
                "type": "object",
                "required": ["preferred_time"],
                "properties": {
                    "preferred_time": {
                        "type": "string",
                        "description": "The preferred time for the call back (Weekdays: 11 AM to 5 PM)"
                    }
                },
                "additionalProperties": False
            }
        }
    }
]

# def payment_plan(amount: int, frequency: str, period: str, pay_date: int, payment_method: str,)
def promise_made(pay_date: str):
    print(f"\nPromise of Payment: SUCCESS")
    print(f"\nPay Date: {pay_date}\n")

try:
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=chat_history,
        tools=tools,
    )

    print("\n", completion.choices[0].message.content)
    payDate = completion.choices[0].message.tool_calls[0].function.arguments

    promise_made(payDate)

except OpenAIError as e:
    print("\nError: OpenAI server is not responding. Please try again later.")
except Exception as e:
    print("\nError: Something went wrong. Please try again.")




#----------------------------------------------PREV_CODE_LOGIC-----------------------------------------------

# def is_payment_response(chatbot_response):
#     payment_keywords = ["amount", "frequency", "method"]
#     return all(keyword.lower() in chatbot_response.lower() for keyword in payment_keywords)

# def extract_payment_details(chatbot_response):
#     params = {
#         "amount": None,
#         "frequency": None,
#         "period": None,
#         "start_date": None,
#         "payment_method": None
#     }

#     amount_match = re.search(r"[\$]?([\d,]+(?:\.\d{2})?)", chatbot_response)
#     if amount_match:
#         params["amount"] = amount_match.group(1).replace(",", "")

#     frequency_match = re.search(r"(SINGLE|MONTH|MONTHS|WEEKS|WEEK|FORTNIGHTS|FORTNIGHT)", chatbot_response, re.IGNORECASE)
#     if frequency_match:
#         params["frequency"] = frequency_match.group(1).upper()

#     period_match = re.search(r"(\d+)\s?(MONTH|MONTHS|WEEKS|WEEK|FORTNIGHTS|FORTNIGHT|PAYMENTS)", chatbot_response, re.IGNORECASE)
#     if period_match:
#         params["period"] = f"{period_match.group(1)} {period_match.group(2).upper()}"

#     date_match = re.search(r"(\d{4}-\d{2}-\d{2})", chatbot_response)
#     if date_match:
#         params["start_date"] = date_match.group(1)

#     if "ACH" in chatbot_response.upper():
#         params["payment_method"] = "ACH"
#     elif "CARD" in chatbot_response.upper():
#         params["payment_method"] = "CARD"

#     return params

# def send_api_request(params):
#     try:
#         response = requests.post(
#             "http://127.0.0.1:5000",
#             json=params
#         )
#         if response.status_code == 200:
#             return response.json().get("payment_link", "No payment link found.")
#         else:
#             return f"Error: {response.status_code}"
#     except Exception as e:
#         return str(e)

# def main_chatbot():
#     stored_request = {}

#     chat_history.append({"role": "user", "content": "hi"})

#     response = client.chat.completions.create(
#         model="gpt-4o",
#         messages=chat_history,
#     )
#     assistant_reply = response.choices[0].message.content
#     chat_history.append({"role": "assistant", "content": assistant_reply})

#     print("\n<Zoya> :\n\n" + assistant_reply)

#     while True:
#         user_input = input("\n<User> :\n\n")

#         if user_input.lower() == "q":
#             print(f"\n<System>\n\nStored Request: {json.dumps(stored_request, indent=4)}\n")
#             if stored_request:
#                 print("\n<System>\n\nSending API Request...")
#                 payment_link = send_api_request(stored_request)
#                 print(f"\n<Zoya>\n\nHere is your payment link: {payment_link}\n")
#             break

#         chat_history.append({"role": "user", "content": user_input})

#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=chat_history,
#         )
#         assistant_reply = response.choices[0].message.content
#         chat_history.append({"role": "assistant", "content": assistant_reply})

#         if is_payment_response(assistant_reply):
#             params = extract_payment_details(assistant_reply)
#             stored_request.update(params)

#         print("\n<Zoya> :\n\n" + assistant_reply)

# if __name__ == "__main__":
#     main_chatbot()
