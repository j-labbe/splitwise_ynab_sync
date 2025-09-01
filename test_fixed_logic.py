#!/usr/bin/env python3
"""
Test script to verify the fixed expense and reimbursement logic
"""

def test_comprehensive_scenarios():
    """Test all possible Splitwise scenarios"""
    
    test_scenarios = [
        {
            'name': 'Classic Expense - I owe money (paid=0, owed>0)',
            'paid': 0.0,
            'owed': 15.50,
            'description': 'Restaurant dinner',
            'should_import': True,
            'expected_type': 'expense',
            'expected_amount': 15.50
        },
        {
            'name': 'Reimbursement - I paid more than I owe (paid>owed)',
            'paid': 45.00,
            'owed': 15.00,
            'description': 'Groceries for group',
            'should_import': True,
            'expected_type': 'reimbursement',
            'expected_amount': 30.00
        },
        {
            'name': 'Even split - I paid exactly what I owe (paid=owed)',
            'paid': 20.00,
            'owed': 20.00,
            'description': 'Coffee run',
            'should_import': False,
            'expected_type': 'none',
            'expected_amount': 0.0
        },
        {
            'name': 'Payment transaction (should be ignored)',
            'paid': 0.0,
            'owed': 25.00,
            'description': 'Payment',
            'should_import': False,
            'expected_type': 'none',
            'expected_amount': 0.0
        },
        {
            'name': 'Complex expense - I paid some but still owe more',
            'paid': 10.00,
            'owed': 25.00,
            'description': 'Group lunch',
            'should_import': False,  # Current logic won't catch this
            'expected_type': 'expense',
            'expected_amount': 15.00
        }
    ]
    
    print("Testing comprehensive expense/reimbursement scenarios:")
    print("=" * 70)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\nTest {i}: {scenario['name']}")
        print(f"  Paid: ${scenario['paid']:.2f}, Owed: ${scenario['owed']:.2f}")
        print(f"  Description: '{scenario['description']}'")
        
        # Apply our current logic
        paid = scenario['paid']
        owed = scenario['owed']
        description = scenario['description']
        
        is_append = False
        is_reimbursement = None
        result_amount = 0.0
        
        if description.strip() != 'Payment':
            # Original working condition for expenses (when you owe money)
            if paid == 0 and owed > 0:
                result_amount = owed
                is_reimbursement = False
                is_append = True
            # New condition for reimbursements (when you are owed money)
            elif paid > 0 and paid > owed:
                result_amount = paid - owed
                is_reimbursement = True
                is_append = True
        
        # Determine result type
        if not is_append:
            result_type = 'none'
        elif is_reimbursement:
            result_type = 'reimbursement'
        else:
            result_type = 'expense'
        
        print(f"  Result: {result_type} - ${result_amount:.2f} - Import: {is_append}")
        print(f"  Expected: {scenario['expected_type']} - ${scenario['expected_amount']:.2f} - Import: {scenario['should_import']}")
        
        # Check if result matches expectation
        matches_import = is_append == scenario['should_import']
        matches_type = result_type == scenario['expected_type']
        matches_amount = abs(result_amount - scenario['expected_amount']) < 0.01
        
        if matches_import and matches_type and matches_amount:
            print("  ✅ PASS")
        else:
            print("  ❌ FAIL")
            if not matches_import:
                print(f"    - Import mismatch: got {is_append}, expected {scenario['should_import']}")
            if not matches_type:
                print(f"    - Type mismatch: got {result_type}, expected {scenario['expected_type']}")
            if not matches_amount:
                print(f"    - Amount mismatch: got ${result_amount:.2f}, expected ${scenario['expected_amount']:.2f}")

def test_ynab_transaction_creation():
    """Test YNAB transaction creation for both types"""
    
    print("\n\nTesting YNAB transaction creation:")
    print("=" * 70)
    
    # Test both expense and reimbursement
    test_expenses = [
        {
            'description': 'Restaurant bill',
            'owed': 25.50,
            'is_reimbursement': False,
            'payee_name': 'Alice'
        },
        {
            'description': 'Gas for road trip',
            'owed': 40.00,
            'is_reimbursement': True,
            'payee_name': 'Bob'
        }
    ]
    
    for expense in test_expenses:
        print(f"\nProcessing: {expense['description']}")
        
        if expense['is_reimbursement']:
            amount = int(expense['owed'] * 1000)
            memo_prefix = "Reimbursement:"
            transaction_type = "INFLOW"
        else:
            amount = -int(expense['owed'] * 1000)
            memo_prefix = "Expense:"
            transaction_type = "OUTFLOW"
        
        print(f"  Type: {transaction_type}")
        print(f"  Payee: {expense['payee_name']}")
        print(f"  Amount: {amount} milliunits (${amount/1000:.2f})")
        print(f"  Memo: {memo_prefix} {expense['description']}")

if __name__ == "__main__":
    test_comprehensive_scenarios()
    test_ynab_transaction_creation()
    print("\n" + "=" * 70)
    print("Analysis complete!")