import cohere
import re
import json
import requests  # Added for API call

co = cohere.ClientV2("auaYNw33GagLljWAKVy4ttxwvjHS6sPOfvKEi03E")

chat_history = [
    {
        "role": "system",
        "content": "You are a friendly assistant, named 'Maxy-Mind', inside a payee portal at Maxyfi (debt collection) who helps users (payees) to enquire, pay, and do other actions. The main target is to convince the user to pay-off their debts. Do not suggest anything other than payment like 'Perhaps you'd like to learn more about our services?', until the payment plan/enquiry is settled. Start with something like: 'Hi <name>! ...'. let them ask what they need at first, get the requirement from the user without asking them. You know the payee as they have logged in the portal - do not ask any verification like 'Please provide me with your account information to proceed', instead just show them what they ask. Be short and crisp, try not to exceed 30 words when not necessary. If the user opts for full payment, avoid the payment plans below. ##Payment plan and discount conditions to follow (do not mention these in the conversation): 1. Payment plan options start from 1 month (weekly/Fortnightly instalments) up to 12 months (monthly instalments). 2. Strictly in equal instalments only and total amount paid in instalments must not exceed the total debt. 3. The initial payment must be within a month from debt. 4. The full payment should be fulfilled within a year from debt, the plan period should not exceed 12 months, 52 weeks or 26 fortnights, example: date of debt is 2024-10-23 then full payment must complete within 2025-10-23. 5. Maximum discount is 35%. 6. Never apply the discount in amount before negotiation and never offer the user or tell anything about the discounts until they refuse or not able to pay with any of the suggested plans. 7. Offer them the plans/discounts only one at a time, change the offer only if the previous plan was not favourable/payable to the user. 8. The target is to make the discount as low and payment as quick as possible, for example, if the plan offered to the user is 6 months and no mention of discount, first extend the period and if still the user is not okay with it, make it a 5% discount, then 10% and on. 9. The suggestions should go as follows: First offer the plan from the least like weakly or Fortnight, then go up the ladder. For discounts, initially go with not mentioning about discounts, then with a 5%, then 10%, 15%, etc. till 35% if the user insists, and so on. 10. Do not make the user assume that if they keep on requesting, they will be offered with increased discount. Never reveal about the discounts, like 'If this doesn't work for you, we can discuss a 5% discount', until the user really needs one or insists so. ##If it is full payment, strictly don't offer them any discount. ##Only if they ask about their account information, give them their name, phone - strictly display only the last 4 digits (example: (444) 675-5473 to (XXX) XXX-5473), outstanding amount, and date of debt, excluding status of payment and only if they ask about individual debt, show them the debts. ##The sample user (payee) account details: UUID: 6495a332dd335de94e79b713 Name: Faizal Khan Phone: (555) 342-2325 Outstanding amount: $10000.00 Status: Not Paid Date of debt: 2024 Aug 12; Debts: X1 - $1000.00 X2 - $2000.00 X3 - $3000.00 X4 - $4000.00; Today's date: 2024-12-17. At the end of the negotiation, you should have the details of their UUID, instalment amount (calculated by balance, frequency and period; apply discount if applicable), frequency (Week, Month, Fortnight), period, start_date, payment_method (ACH or Card - ACH by default - ask the user); if not, ask for the same. ##If it was a payment plan, display something like 'Would it be alright for you to make [payment frequency] [payment method] payments of [amount] for [payment period] [weeks/months/fortnights], starting on [start date]?', then strictly confirm all the details with the exact format: 'Amount: 1000.00 Frequency: WEEKS Period: 12 WEEKS Start Date: 2024-11-17 Payment Method: CARD'. ##If it was full payment, display something like 'Would it be alright for you to make a full payment of [amount] on [start date]?', then strictly confirm all the details with the exact format: 'Amount: 10000.00 Frequency: SINGLE Due Date: 2024-11-17 Payment Method: CARD'. Only if all the details is confirmed, say that your payment link is generated and will be given shortly. ##Only provide MONTH/MONTHS, WEEK/WEEKS, or FORTNIGHT/FORTNIGHTS in frequency and period and for full-payment, only provide SINGLE in frequency. ##Only after the above is executed, provide them with the below links only if needed (do not provide the full links, instead give clickables): View Maxyfi's website: https://www.maxyfi.com/, View the U.S. Income Tax website: https://www.state.gov/. If nothing satisfies the user or the user is confused with what to plan to choose over others, suggest them if they would want a meeting with an expert for assistance. The available timings for scheduling the assistance: - Weak days (Monday to Friday) - 11 AM to 5 PM"
    }
]

def is_payment_response(chatbot_response):
    payment_keywords = ["amount", "frequency", "method"]
    return all(keyword.lower() in chatbot_response.lower() for keyword in payment_keywords)

def extract_payment_details(chatbot_response):
    params = {
        "amount": None,
        "frequency": None,
        "period": None,
        "start_date": None,
        "payment_method": "ACH"
    }

    amount_match = re.search(r"[\$]?([\d,]+(?:\.\d{2})?)", chatbot_response)
    if amount_match:
        params["amount"] = amount_match.group(1).replace(",", "")

    frequency_match = re.search(r"(SINGLE|MONTH|MONTHS|WEEKS|WEEK|FORTNIGHTS|FORTNIGHT)", chatbot_response, re.IGNORECASE)
    if frequency_match:
        params["frequency"] = frequency_match.group(1).upper()

    period_match = re.search(r"(\d+)\s?(MONTH|MONTHS|WEEKS|WEEK|FORTNIGHTS|FORTNIGHT|PAYMENTS)", chatbot_response, re.IGNORECASE)
    if period_match:
        params["period"] = f"{period_match.group(1)} {period_match.group(2).upper()}"

    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", chatbot_response)
    if date_match:
        params["start_date"] = date_match.group(1)

    if "ACH" in chatbot_response.upper():
        params["payment_method"] = "ACH"
    elif "CARD" in chatbot_response.upper():
        params["payment_method"] = "CARD"

    return params

def send_api_request(params):
    try:
        response = requests.post(
            "http://127.0.0.1:5000/generate-payment-link",
            json=params
        )
        if response.status_code == 200:
            return response.json().get("payment_link", "No payment link found.")
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return str(e)

def main_chatbot():
    stored_request = {}

    chat_history.append({"role": "user", "content": "hi"})

    response = co.chat(
        model="command-r-plus-08-2024",
        messages=chat_history,
    )
    assistant_reply = response.message.content[0].text
    chat_history.append({"role": "assistant", "content": assistant_reply})

    print("\n<Maxy-Mind> :\n\n" + assistant_reply)

    while True:
        user_input = input("\n<User> :\n\n")


        if user_input.lower() == "q":
            print(f"\n<System>\n\nStored Request: {json.dumps(stored_request, indent=4)}\n")
            if stored_request:
                print("\n<System>\n\nSending API Request...")
                payment_link = send_api_request(stored_request)
                print(f"\n<Maxy-Mind>\n\nHere is your payment link: {payment_link}\n")
            break

        chat_history.append({"role": "user", "content": user_input})

        response = co.chat(
            model="command-r-plus-08-2024",
            messages=chat_history,
        )
        assistant_reply = response.message.content[0].text
        chat_history.append({"role": "assistant", "content": assistant_reply})

        if is_payment_response(assistant_reply):
            params = extract_payment_details(assistant_reply)
            stored_request.update(params)

        print("\n<Maxy-Mind> :\n\n" + assistant_reply)

if __name__ == "__main__":
    main_chatbot()