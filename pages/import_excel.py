from datetime import datetime
import pandas as pd
from finance.db import get_session
from sqlalchemy import text

def import_statement():
    filepath = 'Хуулга 2016-01-01  2016-12-31.xlsx'
    df1 = pd.read_excel(filepath, sheet_name='Sheet1')
    
    data = df1.iloc[5:].copy()
    data.columns = ['date', 'description', 'income', 'expense']
    data = data.dropna(subset=['date'])

    with get_session() as session:
        session.execute(text("""
            INSERT OR IGNORE INTO accounts (id, nickname, account_no) 
            VALUES (1, 'Хасбанк харилцах', '1111')
        """))
        
        count = 0
        for _, row in data.iterrows():
            date_str = str(row['date']).strip()
            try:
                txn_date = datetime.strptime(date_str[:10], '%Y/%m/%d')
            except:
                continue
                
            desc = str(row['description']).strip()
            income = float(row['income']) if pd.notna(row['income']) else 0.0
            expense = float(row['expense']) if pd.notna(row['expense']) else 0.0
            
            if income > 0:
                amount = income
                kind = 'income'
            elif expense > 0:
                amount = -abs(expense)
                kind = 'expense'
            else:
                continue

            session.execute(text("""
                INSERT INTO transactions (txn_datetime, amount, description, account_id, category_source)
                VALUES (:dt, :amt, :desc, 1, 'excel_import')
            """), {"dt": txn_date, "amt": amount, "desc": desc})
            count += 1
            
        session.commit()
        print(f"Амжилттай {count} гүйлгээг датабааз руу орууллаа!")

if __name__ == '__main__':
    import_statement()