from splitwise import Splitwise
from splitwise.expense import Expense
from splitwise.user import ExpenseUser
import os
from utils import setup_environment_vars

# https://github.com/namaggarwal/splitwise

class SW():
    def __init__(self, consumer_key, consumer_secret, api_key) -> None:
        # Initialize the Splitwise object with the API key
        self.sw = Splitwise(consumer_key, consumer_secret, api_key=api_key)

        self.limit = 100
        self.current_user = self.sw.getCurrentUser().getFirstName()
        self.current_user_id = self.sw.getCurrentUser().getId()

    def get_friends(self):
        friends_fullnames = []
        friends_ids = []
        for friend in self.sw.getFriends():
            id = friend.getId()
            full_name = friend.getFirstName()
            if friend.getLastName() is not None:
                full_name = " ".join([full_name, friend.getLastName()])
            friends_fullnames.append(full_name)
            friends_ids.append(id)
        return friends_fullnames, friends_ids

    def get_expenses(self, dated_before=None, dated_after=None):
        # get all expenses between 2 dates
        expenses = self.sw.getExpenses(limit=self.limit, dated_before=dated_before, dated_after=dated_after)
        owed_expenses = []
        for expense in expenses:
            owed_expense = {}
            users = expense.getUsers()
            user_names = []
            other_users_info = []  # Store detailed info about other users
            expense_cost = float(expense.getCost())
            is_append = False

            for user in users:
                user_first_name = user.getFirstName()
                if user_first_name == self.current_user:
                    paid = float(user.getPaidShare())
                    owed = float(user.getOwedShare())
                    description = expense.getDescription()
                    
                    # Handle both scenarios: user owes money (expense) or user is owed money (reimbursement)
                    if description.strip() != 'Payment':
                        # Original working condition for expenses (when you owe money)
                        if paid == 0 and owed > 0:
                            owed_expense['owed'] = owed
                            owed_expense['is_reimbursement'] = False
                            is_append = True
                        # New condition for reimbursements (when you are owed money)
                        elif paid > 0 and paid > owed:
                            owed_expense['owed'] = paid - owed
                            owed_expense['is_reimbursement'] = True
                            is_append = True
                        
                        if is_append:
                            owed_expense['date'] = expense.getDate()
                            owed_expense['created_time'] = expense.getCreatedAt()
                            owed_expense['updated_time'] = expense.getUpdatedAt()
                            owed_expense['deleted_time'] = expense.getDeletedAt()
                            owed_expense['description'] = description
                            owed_expense['cost'] = expense_cost
                else:       # get user names other than current_user
                    user_paid_share = float(user.getPaidShare())
                    user_owed_share = float(user.getOwedShare())
                    
                    # Store detailed user info for payee determination
                    other_users_info.append({
                        'name': user_first_name,
                        'paid': user_paid_share,
                        'owed': user_owed_share
                    })
                    
                    if user_paid_share == expense_cost:
                        user_names.append("[" + user_first_name + "]")
                    else:
                        user_names.append(user_first_name)
            if is_append:      # check category instead of description
                owed_expense['users'] = user_names
                
                # Determine payee based on expense type
                payee_name = None
                if owed_expense.get('is_reimbursement', False):
                    # For reimbursements, payee is who owes you money (has positive owed_share)
                    max_owed = 0
                    for user_info in other_users_info:
                        if user_info['owed'] > max_owed:
                            max_owed = user_info['owed']
                            payee_name = user_info['name']
                else:
                    # For expenses, payee is who you owe money to (who paid the most)
                    max_paid = 0
                    for user_info in other_users_info:
                        if user_info['paid'] > max_paid:
                            max_paid = user_info['paid']
                            payee_name = user_info['name']
                
                # If no clear payee found, use first user or combined names
                if not payee_name and user_names:
                    if len(user_names) == 1:
                        payee_name = user_names[0].strip('[]')
                    else:
                        # For multiple users, use combined format
                        payee_name = "Split: " + ", ".join([name.strip('[]') for name in user_names])
                
                owed_expense['payee_name'] = payee_name
                owed_expenses.append(owed_expense)
        return owed_expenses
    
    def create_expense(self, expense):
        e = Expense()
        e.setCost(expense['cost'])
        e.setDate(expense['date'])
        e.setDescription(expense['description'])

        users = []
        for user in expense['users']:
            u = ExpenseUser()
            u.setId(user['id'])
            u.setPaidShare(user['paid'])
            u.setOwedShare(user['owed'])

            users.append(u)

        e.setUsers(users)
        expense, errors = self.sw.createExpense(e)
        if errors:
            print(errors.getErrors())
        return expense, errors


if __name__ == "__main__":
    # load environment variables from yaml file (locally)
    setup_environment_vars()
    
    # splitwise creds
    consumer_key = os.environ.get('sw_consumer_key')
    consumer_secret = os.environ.get('sw_consumer_secret')
    api_key = os.environ.get('sw_api_key')

    a = SW(consumer_key, consumer_secret, api_key)
    # e = a.get_expenses(dated_after="2023-11-29", dated_before="2023-12-01")
    
    a.create_expense()
    # a.get_friends()
