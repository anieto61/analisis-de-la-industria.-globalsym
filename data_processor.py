import pandas as pd
import numpy as np

class FinancialDataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.excel_file = pd.ExcelFile(file_path)

    def process_inventories(self):
        all_inventories = []
        for line in ['Linea 1', 'Linea 2']:
            sheet_name = f'Inventario Empresas {line}'
            if sheet_name not in self.excel_file.sheet_names:
                continue
                
            # Header is on row 2 (0-indexed)
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, skiprows=2)
            
            cols = df.columns.tolist()
            countries = []
            for col in cols:
                if '.' not in str(col) and not str(col).startswith('Unnamed'):
                    countries.append(col)
            
            for idx, row in df.iterrows():
                # The first column seems to be the Company name (or similar)
                company = row.iloc[0] if not pd.isna(row.iloc[0]) else f"Empresa {idx+1}"
                
                for country in countries:
                    try:
                        col_idx = cols.index(country)
                        product = str(row.iloc[col_idx]).strip() if not pd.isna(row.iloc[col_idx]) else None
                        quantity = row.iloc[col_idx + 1]
                        
                        if product and product != 'nan' and pd.notna(quantity):
                            all_inventories.append({
                                'Company': company,
                                'Country': country,
                                'Line': line,
                                'Product': product,
                                'Quantity': quantity
                            })
                    except (IndexError, ValueError):
                        continue
        
        return pd.DataFrame(all_inventories)

    def process_profitability(self):
        all_profit = []
        for line in ['Linea 1', 'Linea 2']:
            sheet_name = f'Rentabilidad {line}'
            if sheet_name not in self.excel_file.sheet_names:
                continue
                
            # Header is on row 3
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, skiprows=3)
            
            cols = df.columns.tolist()
            countries = []
            for col in cols:
                if '.' not in str(col) and not str(col).startswith('Unnamed'):
                    countries.append(col)

            for idx, row in df.iterrows():
                product = str(row.iloc[0]).strip() if not pd.isna(row.iloc[0]) else None
                if not product or product == 'nan':
                    continue
                
                for country in countries:
                    try:
                        base_idx = cols.index(country)
                        # Based on the analysis, we see prices under these columns.
                        # Let's try to detect if columns correspond to cost/industry/consumer
                        # using a few indices or searching for labels.
                        # Usually: .1=Cost, .2=Industry, .3=Consumer
                        cost = row.iloc[base_idx + 1]
                        ind_price = row.iloc[base_idx + 2]
                        cons_price = row.iloc[base_idx + 3]
                        
                        all_profit.append({
                            'Product': product,
                            'Country': country,
                            'Line': line,
                            'Cost': cost,
                            'Industry_Price': ind_price,
                            'Consumer_Price': cons_price
                        })
                    except (IndexError, ValueError):
                        continue
        
        return pd.DataFrame(all_profit)

    def get_cleaned_data(self):
        inv_df = self.process_inventories()
        prof_df = self.process_profitability()
        
        if inv_df.empty or prof_df.empty:
            return pd.DataFrame()
            
        # Merge on Product, Country, Line
        final_df = pd.merge(inv_df, prof_df, on=['Product', 'Country', 'Line'], how='left')
        return final_df
