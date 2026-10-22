import pandas as pd
import numpy as np

class FinancialDataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.excel_file = pd.ExcelFile(file_path)

    def _clean_value(self, val):
        if pd.isna(val): return None
        return str(val).strip()

    def process_inventories(self):
        all_inventories = []
        for line in ['Linea 1', 'Linea 2']:
            sheet_name = f'Inventario Empresas {line}'
            if sheet_name not in self.excel_file.sheet_names: continue
            df_raw = pd.read_excel(self.file_path, sheet_name=sheet_name, header=None)
            header_idx = df_raw.notnull().sum(axis=1).idxmax()
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, skiprows=header_idx)
            cols = df.columns.tolist()
            countries = [c for c in cols if not str(c).startswith('Unnamed') and '.' not in str(c)]
            for idx, row in df.iterrows():
                company = self._clean_value(row.iloc[0]) if not pd.isna(row.iloc[0]) else f"Empresa {idx+1}"
                for country in countries:
                    try:
                        col_idx = cols.index(country)
                        product = self._clean_value(row.iloc[col_idx])
                        quantity = row.iloc[col_idx + 1]
                        if product and product.lower() != 'nan' and pd.notna(quantity):
                            all_inventories.append({
                                'Company': company, 'Country': country, 'Line': line, 
                                'Product': product, 'Quantity': quantity
                            })
                    except: continue
        return pd.DataFrame(all_inventories)

    def process_profitability(self):
        all_profit = []
        for line in ['Linea 1', 'Linea 2']:
            sheet_name = f'Rentabilidad {line}'
            if sheet_name not in self.excel_file.sheet_names: continue
            df_raw = pd.read_excel(self.file_path, sheet_name=sheet_name, header=None)
            header_idx = df_raw.notnull().sum(axis=1).idxmax()
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, skiprows=header_idx)
            cols = df.columns.tolist()
            countries = [c for c in cols if not str(c).startswith('Unnamed') and '.' not in str(c)]
            for idx, row in df.iterrows():
                product = None
                for val in row:
                    if pd.notna(val):
                        product = self._clean_value(val)
                        break
                if not product or product.lower() == 'nan': continue
                for country in countries:
                    try:
                        base_idx = cols.index(country)
                        all_profit.append({
                            'Product': product, 'Country': country, 'Line': line,
                            'Cost': row.iloc[base_idx + 1], 
                            'Industry_Price': row.iloc[base_idx + 2], 
                            'Consumer_Price': row.iloc[base_idx + 3]
                        })
                    except: continue
        return pd.DataFrame(all_profit)

    def get_cleaned_data(self):
        inv_df = self.process_inventories()
        prof_df = self.process_profitability()
        base_cols = ['Company', 'Country', 'Line', 'Product', 'Quantity', 'Cost', 'Industry_Price', 'Consumer_Price']
        if inv_df.empty: return pd.DataFrame(columns=base_cols)
        
        merged = pd.merge(inv_df, prof_df, on=['Product', 'Country', 'Line'], how='left')
        
        # FORZAR TIPOS NUMÉRICOS (Esto soluciona el error de concatenación)
        numeric_cols = ['Quantity', 'Cost', 'Industry_Price', 'Consumer_Price']
        for col in numeric_cols:
            if col in merged.columns:
                merged[col] = pd.to_numeric(merged[col], errors='coerce').fillna(0)
            else:
                merged[col] = 0.0
                
        # Forzar textos
        merged['Company'] = merged['Company'].astype(str)
        merged['Product'] = merged['Product'].astype(str)
        merged['Country'] = merged['Country'].astype(str)
        merged['Line'] = merged['Line'].astype(str)
                
        return merged[base_cols]
