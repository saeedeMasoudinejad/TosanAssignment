1. create a virtual environment with "python3 -m venv .venv"
2. Active the virtual environment 'source venv/bin/activate"
3. Install dependencies with "pip install -r  requirements"
4. Apply database migrations with "python manage.py migrate"
5. Run the project with "python manage.py runserver" or set up the run configuration at your IDE

## Usage
1.Access the API at http://localhost:8000/
2.Use http://localhost:8000/schema/swagger-ui/
3.SetUp database name or constance value just change on .env file.

## Scenario Questions:
## Transfer
When transferring between internal accounts, both a source account and a destination account are required for both
deposit and withdrawal. The source account is used for withdrawal, and the destination account is used for deposit.
Therefore, it is still unclear to me why separate implementations are needed for both withdrawal and deposit.
- For this reason, I designed an API that receives both the source and destination accounts, and the user can specify
 the type of operation (deposit or withdrawal). However, I still believe it is unnecessary.
- Therefore, in the transaction history display, I do not determine the type of transfer based on the value
 specified by the user. Instead, it is determined based on the perspective of the user viewing the transaction history.

## Refund
For the "refund" type of transfer:
- I have designed it so that a transfer that has been successfully and completely executed can be refunded using
its transaction ID.
- Each transfer can only be refunded once.
- The status of the transfer that is refunded remains unchanged, but it is marked as refunded. (In the Transaction model)
- Regarding who can perform the refund operation, only the admin, the owner of the source account of the transfer,
or both can initiate the refund?

##NOTE














