import pandas as pd
import plotly.express as px
import streamlit as st
import os
import numpy as np

def create_chart(file_path: str, chart_info: dict, lang: str):

    try:
        if not file_path or not os.path.exists(file_path):
            return None

        if not file_path.endswith(('.xlsx', '.xls', '.csv')):
            return None
            
        # read the entire sheet without assuming a header
        df = pd.read_excel(file_path, header=None) if file_path.endswith(('.xlsx', '.xls')) else pd.read_csv(file_path, header=None)
        
        if df.empty: return None

        # aggressively clean the raw data
        df.dropna(how='all', axis=0, inplace=True)
        df.dropna(how='all', axis=1, inplace=True)
        df.reset_index(drop=True, inplace=True)

        # find the first row that is most likely the real header
        header_row_index = 0
        for i, row in df.iterrows():
            if row.count() > 1 and pd.to_numeric(row, errors='coerce').isnull().sum() / row.count() > 0.5:
                header_row_index = i
                break
        
        # rebuild the DataFrame using the detected header
        df.columns = df.iloc[header_row_index]
        df = df.drop(header_row_index).reset_index(drop=True)
        df.columns.name = None
        df.columns = df.columns.astype(str).str.strip()

        # explicitly identify categorical and numerical columns
        categorical_cols = []
        numerical_cols = []

        for col in df.columns:
            # try to convert column to numbers, coercing errors
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            # if less than half the values are numbers, treat as a category
            if numeric_series.notna().sum() < len(df) / 2:
                categorical_cols.append(col)
            else:
                numerical_cols.append(col)
                df[col] = numeric_series

        if not categorical_cols or not numerical_cols:
            st.warning("Could not identify distinct categorical and numerical columns for plotting.")
            return None

        x_column = categorical_cols[0]
        y_column = numerical_cols[0]
        
        df.dropna(subset=[x_column, y_column], inplace=True)
        if df.empty: return None

        # Chart Generation
        chart_type = chart_info.get("chart_type", "line")
        ai_title = chart_info.get("title") or (f"{y_column} üzrə {x_column}" if lang == 'az' else f"{y_column} by {x_column}")
        
        fig = None
        if chart_type == "bar": fig = px.bar(df, x=x_column, y=y_column, title=ai_title)
        elif chart_type == "line": fig = px.line(df, x=x_column, y=y_column, title=ai_title)
        elif chart_type == "pie": fig = px.pie(df, names=x_column, values=y_column, title=ai_title)
        
        if fig:
            fig.update_layout(yaxis_tickformat='.2f')
            return fig
        return None

    except Exception as e:
        st.error(f"Failed to generate chart: {e}")
        return None