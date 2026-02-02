import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64

# --- 1. GLOBAL AUDIT DATA (Verified Syntax) ---
AUDIT_DATA = {
    "Architecture": {
        "about": "Validates the physical silicon-to-package mapping. It ensures that internal package delays (Pkg Delay) are matched across the data bus to prevent signal skew.",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["Standard", "Standard", "x16 Type", "100ps Max"],
            "Significance": ["Determines addressable space.", "Land pattern design.", "Interleaving efficiency.", "Trace offset matching."]
        })
        
